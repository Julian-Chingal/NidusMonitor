import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from typing import Dict, Any, Optional, Tuple, Callable
from config import settings

class BabyMonitorProcessor:
    def __init__(self, state_callback: Optional[Callable[[str, str], None]] = None):
        """
        Clase de procesamiento de visión computacional optimizada para CPU i5 5ta Gen.
        Utiliza MediaPipe Face Mesh (complejidad reducida) y Pose (complejidad 0).
        """
        self.state_callback = state_callback

        # Configuración de ROI segura (Valores relativos 0.0 - 1.0)
        # Por defecto, toda la pantalla es zona segura
        self.roi: Dict[str, float] = {
            "x_min": 0.0,
            "y_min": 0.0,
            "x_max": 1.0,
            "y_max": 1.0
        }

        # Inicializar soluciones de MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # model_complexity=0 es el más rápido y ligero de Pose
        self.mp_pose = mp.solutions.pose.Pose(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Historial y contadores para la máquina de estados
        self.consecutive_open_frames = 0
        self.consecutive_closed_frames = 0
        self.last_pose_landmarks: Optional[np.ndarray] = None
        self.motion_history = deque(maxlen=15) # Almacena movimiento de los últimos ~3 segundos (a 5 fps)
        self.not_detected_counter = 0

        # Estados posibles del bebé
        # "deep_sleep", "moving", "awake", "position_change", "strong_motion", "out_of_area"
        self.current_state = "deep_sleep"
        self.last_state_change_time = time.time()
        self.last_position_change_time = 0.0

        # Índices de landmarks para EAR en MediaPipe Face Mesh
        # Ojo Izquierdo
        self.LEFT_EYE_VERT_1 = (160, 144)
        self.LEFT_EYE_VERT_2 = (158, 153)
        self.LEFT_EYE_HORIZ = (33, 133)
        # Ojo Derecho
        self.RIGHT_EYE_VERT_1 = (385, 380)
        self.RIGHT_EYE_VERT_2 = (387, 373)
        self.RIGHT_EYE_HORIZ = (362, 263)

    def set_roi(self, x_min: float, y_min: float, x_max: float, y_max: float):
        """Actualiza la zona segura / ROI."""
        self.roi = {
            "x_min": min(x_min, x_max),
            "y_min": min(y_min, y_max),
            "x_max": max(x_min, x_max),
            "y_max": max(y_min, y_max)
        }

    def _euclidean_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calcula la distancia euclidiana entre dos puntos 2D."""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _calculate_eye_ear(self, landmarks, vert_pair1: Tuple[int, int], vert_pair2: Tuple[int, int], horiz_pair: Tuple[int, int]) -> float:
        """Calcula el Eye Aspect Ratio (EAR) para un ojo dado."""
        p_v1_top = (landmarks[vert_pair1[0]].x, landmarks[vert_pair1[0]].y)
        p_v1_bot = (landmarks[vert_pair1[1]].x, landmarks[vert_pair1[1]].y)
        p_v2_top = (landmarks[vert_pair2[0]].x, landmarks[vert_pair2[0]].y)
        p_v2_bot = (landmarks[vert_pair2[1]].x, landmarks[vert_pair2[1]].y)
        p_h_left = (landmarks[horiz_pair[0]].x, landmarks[horiz_pair[0]].y)
        p_h_right = (landmarks[horiz_pair[1]].x, landmarks[horiz_pair[1]].y)

        dist_v1 = self._euclidean_distance(p_v1_top, p_v1_bot)
        dist_v2 = self._euclidean_distance(p_v2_top, p_v2_bot)
        dist_h = self._euclidean_distance(p_h_left, p_h_right)

        if dist_h == 0:
            return 0.0

        return (dist_v1 + dist_v2) / (2.0 * dist_h)

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Procesa un frame individual:
        1. Downscaling a 320x240 para eficiencia.
        2. Corrección de color y ejecución de MediaPipe.
        3. Cálculo de EAR y Detección de Pose.
        4. Transición de estados y lógica de alertas.
        """
        # 1. Redimensionar para ahorrar CPU
        h_orig, w_orig = frame.shape[:2]
        frame_resized = cv2.resize(frame, (settings.PROCESS_WIDTH, settings.PROCESS_HEIGHT))

        # Convertir a RGB (MediaPipe requiere RGB)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # 2. Ejecutar MediaPipe
        face_results = self.mp_face_mesh.process(frame_rgb)
        pose_results = self.mp_pose.process(frame_rgb)

        # Inicialización de métricas
        ear = -1.0
        motion = 0.0
        in_safe_zone = True
        baby_detected = False
        pose_centroid = None

        # 3. Procesar Cara (EAR)
        if face_results.multi_face_landmarks:
            baby_detected = True
            self.not_detected_counter = 0
            landmarks = face_results.multi_face_landmarks[0].landmark

            left_ear = self._calculate_eye_ear(landmarks, self.LEFT_EYE_VERT_1, self.LEFT_EYE_VERT_2, self.LEFT_EYE_HORIZ)
            right_ear = self._calculate_eye_ear(landmarks, self.RIGHT_EYE_VERT_1, self.RIGHT_EYE_VERT_2, self.RIGHT_EYE_HORIZ)
            ear = (left_ear + right_ear) / 2.0

            # Lógica de parpadeo / ojos abiertos/cerrados
            if ear < settings.EAR_THRESHOLD:
                self.consecutive_closed_frames += 1
                self.consecutive_open_frames = 0
            else:
                self.consecutive_open_frames += 1
                self.consecutive_closed_frames = 0
        else:
            # Si no se detecta la cara, no alteramos bruscamente los contadores,
            # pero podemos decrementar lentamente o marcarlos como no disponibles (-1)
            pass

        # 4. Procesar Pose y Movimiento
        if pose_results.pose_landmarks:
            baby_detected = True
            self.not_detected_counter = 0
            landmarks = pose_results.pose_landmarks.landmark

            # Usar hombros, orejas y nariz para el centro de gravedad del bebé (tren superior)
            key_indices = [0, 7, 8, 11, 12] # nariz, oreja izq, oreja der, hombro izq, hombro der
            points = []
            for idx in key_indices:
                lm = landmarks[idx]
                if lm.visibility > 0.5: # Filtrar si el punto no es confiable
                    points.append([lm.x, lm.y])

            if points:
                pose_centroid = np.mean(points, axis=0)

                # Calcular movimiento comparando con el frame anterior
                if self.last_pose_landmarks is not None:
                    # Distancia de desplazamiento del centroide
                    motion = float(np.linalg.norm(pose_centroid - self.last_pose_landmarks))
                else:
                    motion = 0.0

                self.last_pose_landmarks = pose_centroid

                # Verificar si está en la Zona Segura (ROI)
                x_c, y_c = pose_centroid[0], pose_centroid[1]
                if not (self.roi["x_min"] <= x_c <= self.roi["x_max"] and self.roi["y_min"] <= y_c <= self.roi["y_max"]):
                    in_safe_zone = False
            else:
                motion = 0.0
        else:
            motion = 0.0
            # Si no se detecta la pose, mantenemos el último centroide pero incrementamos no detectado
            if not face_results.multi_face_landmarks:
                self.not_detected_counter += 1

        # Guardar en historial de movimiento
        self.motion_history.append(motion)

        # 5. Máquina de Estados
        new_state = self.current_state
        state_description = ""

        # Si el bebé lleva más de 5 segundos sin ser detectado en absoluto
        # (5 frames por seg * 5 = 25 frames)
        if self.not_detected_counter >= 25:
            new_state = "out_of_area"
            state_description = "Bebé no detectado en el área de la cámara."
        elif not in_safe_zone:
            new_state = "out_of_area"
            state_description = "¡El bebé ha salido de la zona segura configurada!"
        else:
            # Calcular promedio de movimiento en los últimos ~3 segundos
            avg_motion = np.mean(self.motion_history) if self.motion_history else 0.0

            # Lógica de estados según movimiento y EAR
            if avg_motion > 0.05: # Movimiento sumamente fuerte
                new_state = "strong_motion"
                state_description = "Movimiento fuerte detectado (posible llanto o agitación)."
            elif motion > 0.08 and (time.time() - self.last_position_change_time > 8.0):
                # Un cambio repentino de pose (un solo frame con alto desplazamiento que luego se calma)
                new_state = "position_change"
                state_description = "El bebé ha cambiado de posición (se dio la vuelta)."
                self.last_position_change_time = time.time()
            elif self.consecutive_open_frames >= settings.EAR_CONSECUTIVE_FRAMES:
                # Ojos abiertos por más de 3 segundos consecutivos
                new_state = "awake"
                state_description = "El bebé se encuentra despierto (ojos abiertos)."
            elif self.consecutive_closed_frames >= settings.EAR_CONSECUTIVE_FRAMES:
                # Ojos cerrados por más de 3 segundos consecutivos y bajo movimiento
                if avg_motion < 0.015:
                    new_state = "deep_sleep"
                    state_description = "El bebé duerme profundamente."
                else:
                    new_state = "moving"
                    state_description = "El bebé está dormido pero moviéndose levemente."
            else:
                # Estado intermedio de transición si no se cumple lo anterior
                if avg_motion > 0.015:
                    new_state = "moving"
                    state_description = "Transición: Movimiento leve detectado."

        # Registrar cambios de estado y ejecutar el callback
        if new_state != self.current_state:
            # Para "position_change", es un evento transitorio.
            # Volvemos a evaluar el estado base (awake o moving) en el siguiente frame si se calma,
            # pero notificamos el evento inmediatamente.
            old_state = self.current_state
            self.current_state = new_state
            self.last_state_change_time = time.time()

            if self.state_callback:
                self.state_callback(new_state, state_description)

        # Retornar métricas en tiempo real
        return {
            "state": self.current_state,
            "ear": float(ear) if ear != -1.0 else None,
            "motion": float(motion),
            "in_safe_zone": in_safe_zone,
            "baby_detected": baby_detected,
            "centroid": [float(pose_centroid[0]), float(pose_centroid[1])] if pose_centroid is not None else None,
            "timestamp": time.time()
        }

    def close(self):
        """Libera recursos de MediaPipe."""
        self.mp_face_mesh.close()
        self.mp_pose.close()
