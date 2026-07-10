from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- Autenticación ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserLogin):
    pass

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- Eventos del Bebé ---
class BabyEventCreate(BaseModel):
    baby_id: int = 1
    event_type: str
    description: Optional[str] = None

class BabyEventOut(BaseModel):
    id: int
    baby_id: int
    event_type: str
    description: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# --- Configuración de Región de Interés (ROI / Zona Segura) ---
class ROICoordinates(BaseModel):
    # Coordenadas relativas de 0.0 a 1.0
    x_min: float = Field(..., ge=0.0, le=1.0)
    y_min: float = Field(..., ge=0.0, le=1.0)
    x_max: float = Field(..., ge=0.0, le=1.0)
    y_max: float = Field(..., ge=0.0, le=1.0)
