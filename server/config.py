from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/researchpilot"
    CLIENT_URL: str = "http://localhost:5173"
    
    # API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    
    # App Config
    MAX_RETRY_COUNT: int = 2
    MIN_QUALITY_SCORE: float = 6.0
    MAX_SUB_QUESTIONS: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
