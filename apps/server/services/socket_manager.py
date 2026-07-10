import socketio
import logging
from typing import Dict, Any

logger = logging.getLogger("nidus.socket")

# Crear el servidor Async de Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    logger.info(f"Cliente conectado al socket: {sid}")
    # Enviar estado actual de bienvenida si es necesario
    await sio.emit("message", {"text": "Conexión establecida con NidusMonitor"}, to=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Cliente desconectado del socket: {sid}")

@sio.event
async def update_roi(sid, data: Dict[str, Any]):
    """
    Recibe la actualización de la zona segura (ROI) desde la app del cliente
    y la transmite al backend de procesamiento.
    data debe contener: x_min, y_min, x_max, y_max
    """
    logger.info(f"Actualización de ROI recibida de {sid}: {data}")
    # Disparar un evento global o importar localmente para actualizar el procesador activo
    from services.webrtc_manager import active_transmitters
    for tx_id, tx_data in active_transmitters.items():
        processor = tx_data.get("processor")
        if processor:
            processor.set_roi(
                data.get("x_min", 0.0),
                data.get("y_min", 0.0),
                data.get("x_max", 1.0),
                data.get("y_max", 1.0)
            )
            logger.info(f"ROI actualizada en el transmisor: {tx_id}")
            
    # Confirmar actualización al cliente
    await sio.emit("roi_updated", data, to=sid)

async def broadcast_metrics(metrics: Dict[str, Any]):
    """Transmite las métricas en tiempo real (EAR, movimiento) a todos los clientes."""
    try:
        await sio.emit("metrics", metrics)
    except Exception as e:
        logger.error(f"Error al transmitir métricas por socket: {e}")

async def broadcast_alert(event_type: str, description: str):
    """Transmite una alerta inmediata por cambio de estado."""
    try:
        await sio.emit("alert", {
            "event_type": event_type,
            "description": description,
            "timestamp": sio.handlers.get('time', lambda: None)() or None # fallback
        })
    except Exception as e:
        logger.error(f"Error al transmitir alerta por socket: {e}")
