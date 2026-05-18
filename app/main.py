from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


# Creamos la instancia principal de FastAPI.
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for Pokemon card search, PSA-like grading and market estimation.",
)


# Registramos las rutas versionadas de la aplicacion.
app.include_router(router)


@app.get("/health", tags=["health"])
def health_check():
    # Endpoint simple para comprobar que la API esta funcionando.
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }