"""
Configuration Settings Module
============================

Centralized configuration management for environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration management."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "unifeast-food-index")
    PINECONE_NAMESPACE: str = os.getenv("PINECONE_NAMESPACE", "__default__")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    
    # DynamoDB Configuration
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "unifeast-users")
    
    # PostgreSQL Configuration (for future use)
    FOOD_DB_ARN: Optional[str] = os.getenv("FOOD_DB_ARN")
    FOOD_DB_SECRET: Optional[str] = os.getenv("FOOD_DB_SECRET")
    FOOD_DB_NAME: str = os.getenv("FOOD_DB_NAME", "postgres")
    FOOD_DB_READONLY: str = os.getenv("FOOD_DB_READONLY", "true")
    
    # Memory Configuration
    MEMORY_RETENTION_DAYS: int = int(os.getenv("MEMORY_RETENTION_DAYS", "3"))
    MEMORY_STORAGE_BACKEND: str = os.getenv("MEMORY_STORAGE_BACKEND", "sqlite")
    
    # Search Configuration
    DEFAULT_SEARCH_TOP_K: int = int(os.getenv("DEFAULT_SEARCH_TOP_K", "10"))
    HIGH_CONFIDENCE_THRESHOLD: float = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.8"))
    MEDIUM_CONFIDENCE_THRESHOLD: float = float(os.getenv("MEDIUM_CONFIDENCE_THRESHOLD", "0.6"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    LOG_DATE_FORMAT: str = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    
    # Application Configuration
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "test_user_123")
    SYSTEM_PROMPT_FILE: str = os.getenv("SYSTEM_PROMPT_FILE", "agent/prompts/system_prompt_with_pinecone.txt")
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Validate that all required settings are present."""
        required_settings = [
            cls.OPENAI_API_KEY,
            cls.PINECONE_API_KEY,
            cls.AWS_ACCESS_KEY_ID,
            cls.AWS_SECRET_ACCESS_KEY,
        ]
        
        missing_settings = [setting for setting in required_settings if not setting]
        
        if missing_settings:
            print(f"❌ Missing required environment variables: {missing_settings}")
            return False
        
        return True
    
    @classmethod
    def get_pinecone_config(cls) -> dict:
        """Get Pinecone configuration as a dictionary."""
        return {
            "api_key": cls.PINECONE_API_KEY,
            "index_name": cls.PINECONE_INDEX_NAME,
            "namespace": cls.PINECONE_NAMESPACE,
        }
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration as a dictionary."""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "embedding_model": cls.OPENAI_EMBEDDING_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
        }
    
    @classmethod
    def get_aws_config(cls) -> dict:
        """Get AWS configuration as a dictionary."""
        return {
            "access_key_id": cls.AWS_ACCESS_KEY_ID,
            "secret_access_key": cls.AWS_SECRET_ACCESS_KEY,
            "region": cls.AWS_REGION,
        }
    
    @classmethod
    def get_memory_config(cls) -> dict:
        """Get memory configuration as a dictionary."""
        return {
            "retention_days": cls.MEMORY_RETENTION_DAYS,
            "storage_backend": cls.MEMORY_STORAGE_BACKEND,
        }
    
    @classmethod
    def get_search_config(cls) -> dict:
        """Get search configuration as a dictionary."""
        return {
            "default_top_k": cls.DEFAULT_SEARCH_TOP_K,
            "high_confidence_threshold": cls.HIGH_CONFIDENCE_THRESHOLD,
            "medium_confidence_threshold": cls.MEDIUM_CONFIDENCE_THRESHOLD,
        }


# Create a global settings instance
settings = Settings()
