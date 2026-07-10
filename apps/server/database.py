from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Clase base declarativa
Base = declarative_base()

# Dependencia para obtener la sesión de BD en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from config.settings import settings

# Crear motor de conexión
engine = create_engine(settings.DATABASE_URL)

# Creador de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

