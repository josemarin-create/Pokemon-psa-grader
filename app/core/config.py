from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Nombre visible de la API. Se puede sobrescribir desde el archivo .env.
    app_name: str = Field(default="Pokemon PSA-like Grader API", alias="APP_NAME")

    # Version inicial del proyecto. Nos ayuda a controlar cambios en la API.
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")

    # API key opcional. La Pokemon TCG API puede funcionar sin clave, pero con limites.
    pokemon_tcg_api_key: str | None = Field(default=None, alias="POKEMON_TCG_API_KEY")

    class Config:
        # Archivo local desde el que se cargan variables de entorno.
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuracion para importarla desde otros modulos.
settings = Settings()