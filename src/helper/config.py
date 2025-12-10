from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):

    APP_NAME: str

    FILE_ALLOWED_EXTENSIONS: list
    MAX_FILE_SIZE: int  
    FILE_DEFAULT_CHUNK_SIZE: int  # in bytes

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_MAIN_DATABASE: str

    DAFAULT_INPUT_MAX_CHARACTERS: Optional[int] = None
    DAFAULT_OUTPUT_MAX_TOKENS: Optional[int] = None
    DAFAULT_TEMPERATURE: Optional[float] = None
    
    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_DIMENSION: Optional[str] = None

    COHERE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    VECTOR_DB_BACKEND: str
    QDRANT_DB_PATH: Optional[str] = None
    QDRANT_CACHE_PATH: Optional[str] = None
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None
    INDEX_THRESHOLD: int

    RERANK_CROSS_ENCODER_NAME: Optional[str] = None

    PRIMARY_LANG: Optional[str] = None
    DEFAULT_LANG: str

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()

# config = get_settings()

# print(config.GEMINI_API_KEY)
# print('\n')
# print(config.OPENAI_API_KEY)