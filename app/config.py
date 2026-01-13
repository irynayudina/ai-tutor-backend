from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "AI Tutor API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/ai"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = "gpt-4-turbo-preview"  # or "claude-3-opus-20240229"
    embedding_model: str = "text-embedding-3-small"
    
    # NestJS Backend
    nestjs_api_url: str = "http://localhost:3000"
    nestjs_graphql_url: str = "http://localhost:3000/graphql"
    
    # Auth0 Configuration
    auth0_domain: str
    auth0_audience: str
    auth0_issuer: str
    
    # Cache Configuration
    cache_ttl_seconds: int = 300  # 5 minutes
    enable_redis: bool = False
    redis_url: Optional[str] = None
    
    # Feature Flags
    enable_daily_goals: bool = True
    enable_roadmap_assistant: bool = True
    enable_note_assistant: bool = True
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()