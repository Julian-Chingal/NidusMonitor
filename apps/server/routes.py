import logging
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import database, models, schemas, config
from config import settings
from services import webrtc_manager

# Configurar logger
logger = logging.getLogger("nidus.routes")

# Crear enrutador principal
router = APIRouter()


# --- Rutas de Autenticación ---
@router.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not user or not config.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso usando el módulo config
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = config.create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/register", response_model=schemas.UserOut)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    
    hashed_pwd = config.get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# --- Rutas de Streaming WebRTC ---
@router.post("/webrtc/transmitter/offer")
async def transmitter_offer(offer_schema: dict):
    """Recibe la oferta SDP de la cámara transmisora y devuelve la respuesta SDP."""
    sdp = offer_schema.get("sdp")
    if not sdp:
        raise HTTPException(status_code=400, detail="SDP inválido")
    try:
        answer_sdp = await webrtc_manager.handle_transmitter_offer(sdp)
        return {"sdp": answer_sdp, "type": "answer"}
    except Exception as e:
        logger.error(f"Error procesando oferta del transmisor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webrtc/client/offer")
async def client_offer(offer_schema: dict):
    """Recibe la oferta SDP del celular de los padres (cliente) y devuelve la respuesta SDP con el feed clonado."""
    sdp = offer_schema.get("sdp")
    if not sdp:
        raise HTTPException(status_code=400, detail="SDP inválido")
    try:
        answer_sdp = await webrtc_manager.handle_client_offer(sdp)
        return {"sdp": answer_sdp, "type": "answer"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error procesando oferta del cliente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Historial de Eventos ---
@router.get("/events/history", response_model=List[schemas.BabyEventOut])
def get_events_history(
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(config.get_current_user)
):
    """Consulta la lista histórica de eventos registrados en la base de datos (requiere login)."""
    events = db.query(models.BabyEvent).order_by(models.BabyEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return events


# --- Configuración de ROI ---
@router.post("/config/roi")
def configure_roi(roi_coords: schemas.ROICoordinates, current_user: models.User = Depends(config.get_current_user)):
    """Actualiza la zona segura configurada (requiere login)."""
    tx_id = "baby_1"
    if tx_id in webrtc_manager.active_transmitters:
        processor = webrtc_manager.active_transmitters[tx_id]["processor"]
        processor.set_roi(
            roi_coords.x_min,
            roi_coords.y_min,
            roi_coords.x_max,
            roi_coords.y_max
        )
        logger.info(f"ROI actualizada vía REST para {tx_id}: {roi_coords}")
        return {"status": "success", "message": "ROI actualizada correctamente."}
    else:
        raise HTTPException(status_code=404, detail="No hay ningún dispositivo transmitiendo activamente para configurar.")
