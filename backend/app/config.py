from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

_backend_dir = Path(__file__).resolve().parent.parent
_env_paths = [_backend_dir / ".env", _backend_dir.parent / ".env"]
_env_file = next((p for p in _env_paths if p.exists()), ".env")


class Settings(BaseSettings):
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # LLM Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    ollama_url: str = "http://165.245.128.29:11434"
    llm_priority: str = "gemini,openai,ollama"  # Gemini first for credit appraisal

    # JWT Auth
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # App
    app_name: str = "Credit Appraisal Engine"
    debug: bool = True
    
    # External APIs for credit appraisal
    cibil_api_key: str = ""
    mca_api_key: str = ""
    ecourts_api_key: str = ""
    pdf_parser_api_key: str = ""
    news_api_key: str = ""  # NewsAPI key for real-time news

    class Config:
        env_file = str(_env_file)
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
