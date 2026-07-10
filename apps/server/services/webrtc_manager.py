import asyncio
import logging
import time
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import MediaStreamError
from typing import Dict, Set, Optional
import av
from config import settings
from services.processor import BabyMonitorProcessor

logger = logging.getLogger("nidus.webrtc")

# Repositorio global de transmisores activos
# "baby_1" -> { "pc": RTCPeerConnection, "video_broadcaster": TrackBroadcaster, "audio_broadcaster": TrackBroadcaster, "processor": BabyMonitorProcessor }
active_transmitters: Dict[str, dict] = {}

class BroadcastTrack(MediaStreamTrack):
    """
    Track que consume frames de una cola de manera asincrónica.
    Se utiliza para retransmitir a los clientes conectados.
    """
    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind
        self.queue = asyncio.Queue()

    async def recv(self):
        try:
            frame = await self.queue.get()
            if frame is None:
                raise MediaStreamError("Track detenido")
            return frame
        except Exception as e:
            raise MediaStreamError(str(e))


class TrackBroadcaster:
    """
    Escucha un track origen (del transmisor), procesa si es video (MediaPipe)
    y duplica el flujo hacia todas las colas de los clientes suscritos.
    """
    def __init__(self, source_track: MediaStreamTrack, processor: Optional[BabyMonitorProcessor] = None, is_video: bool = False):
        self.source_track = source_track
        self.processor = processor
        self.is_video = is_video
        self.subscribers: Set[BroadcastTrack] = set()
        self.task: Optional[asyncio.Task] = None
        self.running = False
        self.last_process_time = 0.0
        self.frame_interval = 1.0 / settings.PROCESS_FPS

    def start(self):
        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info(f"Broadcaster de {self.source_track.kind} iniciado.")

    async def _run(self):
        try:
            while self.running:
                try:
                    frame = await self.source_track.recv()
                except MediaStreamError:
                    logger.info(f"El track origen de {self.source_track.kind} ha terminado.")
                    break
                except Exception as e:
                    logger.error(f"Error recibiendo del track de {self.source_track.kind}: {e}")
                    break

                # Procesamiento por IA sólo si es video y hay un procesador asignado
                if self.is_video and self.processor:
                    now = time.time()
                    if now - self.last_process_time >= self.frame_interval:
                        self.last_process_time = now
                        # Programar el análisis del frame en segundo plano para no bloquear
                        asyncio.create_task(self._process_frame_async(frame))

                # Retransmitir a los subscriptores
                for sub in list(self.subscribers):
                    if sub.queue.qsize() < 30: # Evitar acumulación de latencia
                        sub.queue.put_nowait(frame)
                    else:
                        # Drop frame más viejo si la cola está llena (mantener tiempo real)
                        try:
                            sub.queue.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        sub.queue.put_nowait(frame)

        except Exception as e:
            logger.error(f"Excepción en el loop del broadcaster: {e}")
        finally:
            self.running = False
            # Notificar fin a todos los suscriptores
            for sub in list(self.subscribers):
                sub.queue.put_nowait(None)
            self.subscribers.clear()
            logger.info(f"Broadcaster de {self.source_track.kind} detenido.")

    async def _process_frame_async(self, frame):
        try:
            # Convertir a numpy BGR para procesamiento
            img = frame.to_ndarray(format="bgr24")
            
            # Ejecutar en el pool de hilos para no bloquear la ejecución asíncrona
            loop = asyncio.get_running_loop()
            metrics = await loop.run_in_executor(None, self.processor.process_frame, img)
            
            # Transmitir por WebSockets (Socket.IO)
            from services.socket_manager import broadcast_metrics
            await broadcast_metrics(metrics)
        except Exception as e:
            logger.error(f"Error procesando frame en segundo plano: {e}")

    def add_subscriber(self, track: BroadcastTrack):
        self.subscribers.add(track)
        logger.info(f"Nuevo suscriptor añadido al track de {self.source_track.kind}. Total: {len(self.subscribers)}")

    def remove_subscriber(self, track: BroadcastTrack):
        if track in self.subscribers:
            self.subscribers.remove(track)
            track.queue.put_nowait(None)
            logger.info(f"Suscriptor removido del track de {self.source_track.kind}. Restantes: {len(self.subscribers)}")

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()


def make_state_callback():
    """Genera la función de callback para registrar cambios de estado del bebé."""
    from database import SessionLocal
    from models import BabyEvent
    from services.fcm import send_push_notification

    def callback(new_state: str, description: str):
        # 1. Guardar en Base de Datos (PostgreSQL)
        db = SessionLocal()
        try:
            event = BabyEvent(baby_id=1, event_type=new_state, description=description)
            db.add(event)
            db.commit()
            db.refresh(event)
            logger.info(f"[DB EVENT] Registrado: {new_state} - {description}")
        except Exception as e:
            logger.error(f"Error al guardar evento en BD: {e}")
        finally:
            db.close()

        # 2. Transmitir alerta por SocketIO
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                from services.socket_manager import broadcast_alert
                loop.create_task(broadcast_alert(new_state, description))
        except Exception as e:
            logger.error(f"Error al agendar broadcast_alert: {e}")

        # 3. Notificación Push FCM si es alerta crítica
        if new_state in ["awake", "out_of_area", "strong_motion"]:
            title = "⚠️ Alerta Crítica" if new_state != "awake" else "👶 Bebé Despierto"
            try:
                send_push_notification(title=title, body=description)
            except Exception as e:
                logger.error(f"Error al enviar push FCM: {e}")

    return callback


async def handle_transmitter_offer(sdp: str, client_id: str = "baby_1") -> str:
    """
    Procesa la oferta SDP del celular transmisor (cámara).
    Crea el peer connection, captura video/audio e inicializa los broadcasters.
    """
    # Si ya existía un transmisor bajo ese ID, limpiarlo
    if client_id in active_transmitters:
        await clean_transmitter(client_id)

    pc = RTCPeerConnection()
    transmitter_data = {
        "pc": pc,
        "video_broadcaster": None,
        "audio_broadcaster": None,
        "processor": BabyMonitorProcessor(state_callback=make_state_callback())
    }
    active_transmitters[client_id] = transmitter_data

    @pc.on("track")
    def on_track(track):
        logger.info(f"Transmisor conectó un track de tipo: {track.kind}")
        if track.kind == "video":
            broadcaster = TrackBroadcaster(track, processor=transmitter_data["processor"], is_video=True)
            transmitter_data["video_broadcaster"] = broadcaster
            broadcaster.start()
        elif track.kind == "audio":
            broadcaster = TrackBroadcaster(track, is_video=False)
            transmitter_data["audio_broadcaster"] = broadcaster
            broadcaster.start()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Estado de conexión del transmisor {client_id}: {pc.connectionState}")
        if pc.connectionState in ["failed", "closed"]:
            await clean_transmitter(client_id)

    # Configurar oferta remota y generar respuesta
    offer = RTCSessionDescription(sdp=sdp, type="offer")
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return pc.localDescription.sdp


async def handle_client_offer(sdp: str, target_id: str = "baby_1") -> str:
    """
    Procesa la oferta SDP del cliente visualizador (padres).
    Suscibe al cliente a los broadcasters del transmisor activo y retransmite.
    """
    if target_id not in active_transmitters:
        raise ValueError("No hay ningún dispositivo transmitiendo actualmente.")

    tx_data = active_transmitters[target_id]
    pc = RTCPeerConnection()

    client_tracks = []

    # Suscribirse al stream de video si está disponible
    if tx_data["video_broadcaster"] and tx_data["video_broadcaster"].running:
        sub_video = BroadcastTrack(kind="video")
        tx_data["video_broadcaster"].add_subscriber(sub_video)
        pc.addTrack(sub_video)
        client_tracks.append((tx_data["video_broadcaster"], sub_video))

    # Suscribirse al stream de audio si está disponible
    if tx_data["audio_broadcaster"] and tx_data["audio_broadcaster"].running:
        sub_audio = BroadcastTrack(kind="audio")
        tx_data["audio_broadcaster"].add_subscriber(sub_audio)
        pc.addTrack(sub_audio)
        client_tracks.append((tx_data["audio_broadcaster"], sub_audio))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Estado de conexión del cliente: {pc.connectionState}")
        if pc.connectionState in ["failed", "closed"]:
            # Desvincular al cliente de los broadcasters
            for broadcaster, sub_track in client_tracks:
                broadcaster.remove_subscriber(sub_track)
            await pc.close()

    offer = RTCSessionDescription(sdp=sdp, type="offer")
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return pc.localDescription.sdp


async def clean_transmitter(client_id: str):
    """Limpia la conexión y recursos del transmisor."""
    logger.info(f"Limpiando recursos del transmisor: {client_id}")
    if client_id in active_transmitters:
        tx_data = active_transmitters.pop(client_id)
        # Detener broadcasters
        if tx_data["video_broadcaster"]:
            tx_data["video_broadcaster"].stop()
        if tx_data["audio_broadcaster"]:
            tx_data["audio_broadcaster"].stop()
        # Cerrar PeerConnection
        try:
            await tx_data["pc"].close()
        except Exception:
            pass
        # Cerrar procesador MediaPipe
        if tx_data["processor"]:
            tx_data["processor"].close()
        logger.info(f"Transmisor {client_id} limpiado por completo.")
