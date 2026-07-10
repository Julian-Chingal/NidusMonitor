import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # API y Servidor
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Orígenes permitidos para CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"

    # Base de Datos
    DATABASE_URL: str = "postgresql://baby_admin:baby_secure_password_2026@localhost:5432/nidus_monitor"

    # Seguridad y JWT
    JWT_SECRET: str = "super_secret_baby_key_2026_random_long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 horas

    # Notificaciones Firebase (FCM)
    FCM_CREDENTIALS_PATH: str = "/app/secrets/serviceAccountKey.json"

    # Configuración de Procesamiento IA (Optimizaciones para i5 5ta Gen)
    PROCESS_FPS: int = 5              # Analizar sólo 5 frames por segundo
    PROCESS_WIDTH: int = 320          # Redimensionar ancho antes de pasar a MediaPipe
    PROCESS_HEIGHT: int = 240         # Redimensionar alto antes de pasar a MediaPipe

    # Umbrales de Detección
    EAR_THRESHOLD: float = 0.2
    EAR_CONSECUTIVE_FRAMES: int = 15  # 15 frames = 3 seg a 5 fps

    def get_allowed_origins_list(self) -> list:
        """Retorna los orígenes permitidos como una lista de strings."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Buscar el archivo .env en la ruta absoluta calculada dinámicamente.
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

