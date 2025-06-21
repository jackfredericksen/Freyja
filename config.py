"""
Freyja - Fresh Configuration Module
Created to fix caching issues
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# FORCE load environment variables every time
load_dotenv(override=True, verbose=False)

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///./freyja.db")
    echo: bool = Field(default=False)
    
    model_config = {"env_prefix": "DB_", "extra": "allow"}

class AISettings(BaseSettings):
    """AI service configuration"""
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    default_model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.7)
    
    model_config = {"env_prefix": "AI_", "extra": "allow"}

class SchedulingSettings(BaseSettings):
    """Third-party scheduling platform settings"""
    buffer_api_key: Optional[str] = Field(default=None)
    hootsuite_api_key: Optional[str] = Field(default=None)
    later_api_key: Optional[str] = Field(default=None)
    
    # Twitter API v2 Keys
    twitter_bearer_token: Optional[str] = Field(default=None)
    twitter_api_key: Optional[str] = Field(default=None)
    twitter_api_secret: Optional[str] = Field(default=None)
    twitter_access_token: Optional[str] = Field(default=None)
    twitter_access_token_secret: Optional[str] = Field(default=None)
    
    model_config = {"env_prefix": "SCHEDULE_", "extra": "allow"}

class ResearchSettings(BaseSettings):
    """Research and monitoring settings"""
    google_trends_enabled: bool = Field(default=True)
    news_api_key: Optional[str] = Field(default=None)
    monitoring_interval: int = Field(default=3600)
    max_trends_per_check: int = Field(default=20)
    
    model_config = {"env_prefix": "RESEARCH_", "extra": "allow"}

class BrandSettings(BaseSettings):
    """Brand voice and content guidelines"""
    brand_name: str = Field(default="Your Brand")
    brand_voice_tone: str = Field(default="professional")
    brand_voice_style: str = Field(default="informative")
    brand_personality: str = Field(default="helpful")
    
    max_hashtags: int = Field(default=3)
    preferred_topics: str = Field(default="tech,ai,productivity")
    avoid_topics: str = Field(default="politics,controversial")
    
    posting_frequency: str = Field(default="3-5 posts per day")
    optimal_times: str = Field(default="9:00,13:00,17:00")
    timezone: str = Field(default="UTC")
    
    model_config = {"env_prefix": "BRAND_", "extra": "allow"}
    
    @property
    def preferred_topics_list(self) -> List[str]:
        return [topic.strip() for topic in self.preferred_topics.split(",")]
    
    @property
    def avoid_topics_list(self) -> List[str]:
        return [topic.strip() for topic in self.avoid_topics.split(",")]
    
    @property
    def optimal_times_list(self) -> List[str]:
        return [time.strip() for time in self.optimal_times.split(",")]

class GrowthSettings(BaseSettings):
    """Growth coaching configuration"""
    follower_target: int = Field(default=10000)
    monthly_growth_rate: float = Field(default=15.0)
    engagement_rate_target: float = Field(default=5.0)
    growth_timeline: str = Field(default="6 months")
    
    coaching_frequency: str = Field(default="weekly")
    focus_areas: str = Field(default="audience_growth,engagement,content_strategy")
    learning_style: str = Field(default="data-driven")
    
    competitors: str = Field(default="")
    benchmark_metrics: str = Field(default="followers,engagement_rate,posting_frequency")
    
    model_config = {"env_prefix": "GROWTH_", "extra": "allow"}
    
    @property
    def focus_areas_list(self) -> List[str]:
        return [area.strip() for area in self.focus_areas.split(",")]
    
    @property
    def competitors_list(self) -> List[str]:
        if not self.competitors:
            return []
        return [comp.strip() for comp in self.competitors.split(",")]
    
    @property
    def benchmark_metrics_list(self) -> List[str]:
        return [metric.strip() for metric in self.benchmark_metrics.split(",")]

class SecuritySettings(BaseSettings):
    """Security and authentication settings"""
    secret_key: str = Field(default="your-secret-key-change-this")
    jwt_secret: str = Field(default="your-jwt-secret-change-this")
    access_token_expire_minutes: int = Field(default=30)
    
    model_config = {"env_prefix": "SECURITY_", "extra": "allow"}

class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = Field(default="Freyja")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "data")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "logs")
    config_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "config")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

def create_settings():
    """Create fresh settings instances every time"""
    # Force reload environment
    load_dotenv(override=True)
    
    # Create fresh instances
    database = DatabaseSettings()
    ai = AISettings()
    scheduling = SchedulingSettings()
    research = ResearchSettings()
    brand = BrandSettings()
    growth = GrowthSettings()
    security = SecuritySettings()
    settings = Settings()
    
    # Attach sub-settings
    settings.database = database
    settings.ai = ai
    settings.scheduling = scheduling
    settings.research = research
    settings.brand = brand
    settings.growth = growth
    settings.security = security
    
    # Backward compatibility
    brand.preferred_topics = brand.preferred_topics_list
    brand.avoid_topics = brand.avoid_topics_list
    brand.optimal_times = brand.optimal_times_list
    growth.focus_areas = growth.focus_areas_list
    growth.competitors = growth.competitors_list
    growth.benchmark_metrics = growth.benchmark_metrics_list
    
    return settings

# Create the global settings instance
_settings = None

def get_settings():
    """Get application settings - always returns fresh instance"""
    global _settings
    if _settings is None:
        _settings = create_settings()
    return _settings

def reload_settings():
    """Force reload settings"""
    global _settings
    _settings = None
    _settings = create_settings()
    return _settings

# Create initial instance
settings = create_settings()
