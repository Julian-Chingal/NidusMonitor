import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import database, models, config
from config import settings

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nidus.main")

# Inicializar Base de Datos
try:
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Tablas de Base de Datos inicializadas/verificadas.")
except Exception as e:
    logger.error(f"Error al inicializar la base de datos: {e}")

app = FastAPI(
    title="Nidus Baby Monitor API",
    description="Backend de monitoreo inteligente de bebé en tiempo real.",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar usuario administrador por defecto (si no existe)
def ensure_default_user():
    db = database.SessionLocal()
    try:
        admin_exists = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_exists:
            hashed_pwd = config.get_password_hash("admin123")
            default_user = models.User(username="admin", password_hash=hashed_pwd)
            db.add(default_user)
            db.commit()
            logger.info("Usuario administrador por defecto creado (admin / admin123).")
    except Exception as e:
        logger.error(f"Error al verificar/crear usuario por defecto: {e}")
    finally:
        db.close()

ensure_default_user()

# --- Registrar Rutas ---
from routes import router
app.include_router(router)

# --- Envolver FastAPI con Socket.IO para correr en un único puerto ---
import socketio
from services.socket_manager import sio

fastapi_app = app
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    # Levantar el servidor unificado (FastAPI + Socket.IO) en el puerto 8000
    logger.info(f"Iniciando API FastAPI y Socket.IO en {settings.HOST}:{settings.PORT}...")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, log_level="info")

