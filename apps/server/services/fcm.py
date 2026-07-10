import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, messaging
from config import settings

logger = logging.getLogger("nidus.fcm")
firebase_initialized = False

# Intentar inicializar Firebase Admin SDK
credentials_path = settings.FCM_CREDENTIALS_PATH

if os.path.exists(credentials_path):
    try:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        logger.info("Firebase Admin SDK inicializado exitosamente.")
    except Exception as e:
        logger.error(f"Error al inicializar Firebase Admin con {credentials_path}: {e}")
else:
    logger.warning(
        f"Archivo de credenciales FCM no encontrado en {credentials_path}. "
        "Las notificaciones push correrán en MODO MOCK (sólo se imprimirán en consola)."
    )

def send_push_notification(title: str, body: str, topic: str = "baby_alerts", token: Optional[str] = None):
    """
    Envía una notificación push mediante Firebase Cloud Messaging.
    Si Firebase no está inicializado, simula el envío imprimiendo en logs.
    """
    if not firebase_initialized:
        logger.info(f"[MOCK FCM] Enviando notificación: Título='{title}' | Cuerpo='{body}' | Destino: Topic='{topic}' Token='{token}'")
        return True

    try:
        if token:
            # Enviar a un dispositivo específico
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                token=token,
                data={
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "status": "done"
                }
            )
        else:
            # Enviar a un canal / topic general (recomendado para simplificar)
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                topic=topic,
                data={
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "status": "done"
                }
            )

        response = messaging.send(message)
        logger.info(f"Notificación FCM enviada con éxito. ID Respuesta: {response}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación FCM: {e}")
        return False
