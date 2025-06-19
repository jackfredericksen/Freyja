"""
Freyja - AI-Powered Social Media Assistant - Configuration Module
Handles all configuration settings for the application
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///./freyja.db")
    echo: bool = Field(default=False)
    
    class Config:
        env_prefix = "DB_"

class AISettings(BaseSettings):
    """AI service configuration"""
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    default_model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.7)
    
    class Config:
        env_prefix = "AI_"

class SchedulingSettings(BaseSettings):
    """Third-party scheduling platform settings"""
    buffer_api_key: Optional[str] = Field(default=None)
    hootsuite_api_key: Optional[str] = Field(default=None)
    later_api_key: Optional[str] = Field(default=None)
    
    class Config:
        env_prefix = "SCHEDULE_"

class ResearchSettings(BaseSettings):
    """Research and monitoring settings"""
    google_trends_enabled: bool = Field(default=True)
    news_api_key: Optional[str] = Field(default=None)
    monitoring_interval: int = Field(default=3600)  # seconds
    max_trends_per_check: int = Field(default=20)
    
    class Config:
        env_prefix = "RESEARCH_"

class BrandSettings(BaseSettings):
    """Brand voice and content guidelines"""
    brand_name: str = Field(default="Your Brand")
    brand_voice_tone: str = Field(default="professional")
    brand_voice_style: str = Field(default="informative")
    brand_personality: str = Field(default="helpful")
    
    max_hashtags: int = Field(default=3)
    preferred_topics: List[str] = Field(default=["tech", "ai", "productivity"])
    avoid_topics: List[str] = Field(default=["politics", "controversial"])
    
    posting_frequency: str = Field(default="3-5 posts per day")
    optimal_times: List[str] = Field(default=["9:00", "13:00", "17:00"])
    timezone: str = Field(default="UTC")
    
    class Config:
        env_prefix = "BRAND_"

class GrowthSettings(BaseSettings):
    """Growth coaching configuration"""
    follower_target: int = Field(default=10000)
    monthly_growth_rate: float = Field(default=15.0)
    engagement_rate_target: float = Field(default=5.0)
    growth_timeline: str = Field(default="6 months")
    
    coaching_frequency: str = Field(default="weekly")
    focus_areas: List[str] = Field(default=["audience_growth", "engagement", "content_strategy"])
    learning_style: str = Field(default="data-driven")
    
    competitors: List[str] = Field(default=[])
    benchmark_metrics: List[str] = Field(default=["followers", "engagement_rate", "posting_frequency"])
    
    class Config:
        env_prefix = "GROWTH_"

class SecuritySettings(BaseSettings):
    """Security and authentication settings"""
    secret_key: str = Field(default="your-secret-key-change-this")
    jwt_secret: str = Field(default="your-jwt-secret-change-this")
    access_token_expire_minutes: int = Field(default=30)
    
    class Config:
        env_prefix = "SECURITY_"

class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = Field(default="Freyja")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    scheduling: SchedulingSettings = SchedulingSettings()
    research: ResearchSettings = ResearchSettings()
    brand: BrandSettings = BrandSettings()
    growth: GrowthSettings = GrowthSettings()
    security: SecuritySettings = SecuritySettings()
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "data")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "logs")
    config_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "config")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def update_brand_settings(**kwargs):
    """Update brand settings dynamically"""
    for key, value in kwargs.items():
        if hasattr(settings.brand, key):
            setattr(settings.brand, key, value)

def update_growth_settings(**kwargs):
    """Update growth settings dynamically"""
    for key, value in kwargs.items():
        if hasattr(settings.growth, key):
            setattr(settings.growth, key, value)