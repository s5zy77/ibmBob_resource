"""Configuration management for Payment Service"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Payment service configuration with environment variable support"""
    
    # Payment Gateway Configuration
    PAYMENT_GATEWAY_URL: str = "https://pay.internal.corp/api/v1/charge"
    PAYMENT_API_KEY: str = "pk_live_ABCDEF1234567890"
    
    # Service Configuration
    MAX_RETRIES: int = 3
    CURRENCY: str = "USD"
    WIRE_MINIMUM: float = 1000.0
    
    # Service Discovery
    SERVICE_PORT: int = 8001
    SERVICE_HOST: str = "0.0.0.0"
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = ["dev-api-key-123", "prod-api-key-xyz"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:5000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Made with Bob
