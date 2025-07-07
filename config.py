"""
Freyja - Fixed Configuration Module
Resolves all import and caching issues
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import os

# Force load environment variables every time
load_dotenv(override=True, verbose=False)

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///./data/freyja.db")
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
    
    # Twitter API v2 Keys - support multiple env var formats
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
    
    def get_preferred_topics_list(self) -> List[str]:
        """Get preferred topics as list"""
        return [topic.strip() for topic in self.preferred_topics.split(",")]
    
    def get_avoid_topics_list(self) -> List[str]:
        """Get avoid topics as list"""
        return [topic.strip() for topic in self.avoid_topics.split(",")]
    
    def get_optimal_times_list(self) -> List[str]:
        """Get optimal times as list"""
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
    
    def get_focus_areas_list(self) -> List[str]:
        """Get focus areas as list"""
        return [area.strip() for area in self.focus_areas.split(",")]
    
    def get_competitors_list(self) -> List[str]:
        """Get competitors as list"""
        if not self.competitors:
            return []
        return [comp.strip() for comp in self.competitors.split(",")]
    
    def get_benchmark_metrics_list(self) -> List[str]:
        """Get benchmark metrics as list"""
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
    settings = Settings()
    settings.database = DatabaseSettings()
    settings.ai = AISettings()
    settings.scheduling = SchedulingSettings()
    settings.research = ResearchSettings()
    settings.brand = BrandSettings()
    settings.growth = GrowthSettings()
    settings.security = SecuritySettings()
    
    # Ensure data directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.config_dir.mkdir(parents=True, exist_ok=True)
    
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

# Validation function
def validate_configuration():
    """Validate that critical configuration is present"""
    issues = []
    
    try:
        settings = get_settings()
        
        # Check AI configuration
        if not settings.ai.anthropic_api_key and not settings.ai.openai_api_key:
            issues.append("No AI API keys configured (OpenAI or Anthropic)")
        
        # Check Twitter configuration
        twitter_keys = [
            settings.scheduling.twitter_api_key,
            settings.scheduling.twitter_api_secret,
            settings.scheduling.twitter_access_token,
            settings.scheduling.twitter_access_token_secret
        ]
        
        if not all(twitter_keys):
            issues.append("Twitter API credentials incomplete")
        
        # Check database path
        try:
            if settings.database.url.startswith("sqlite"):
                db_path = Path(settings.database.url.replace("sqlite:///", ""))
                db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Database path issue: {e}")
        
    except Exception as e:
        issues.append(f"Configuration loading error: {e}")
    
    return issues

if __name__ == "__main__":
    # Test configuration loading
    print("🔧 Testing Fixed Configuration...")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.version}")
    print(f"Database URL: {settings.database.url}")
    print(f"Data Directory: {settings.data_dir}")
    
    # Check API keys
    print(f"OpenAI Key: {'✅ Set' if settings.ai.openai_api_key else '❌ Not set'}")
    print(f"Anthropic Key: {'✅ Set' if settings.ai.anthropic_api_key else '❌ Not set'}")
    print(f"Twitter API Key: {'✅ Set' if settings.scheduling.twitter_api_key else '❌ Not set'}")
    
    # Brand settings
    print(f"Brand Name: {settings.brand.brand_name}")
    print(f"Preferred Topics: {settings.brand.get_preferred_topics_list()}")
    print(f"Growth Target: {settings.growth.follower_target}")
    
    # Validate configuration
    validation_issues = validate_configuration()
    if validation_issues:
        print("\n⚠️ Configuration Issues:")
        for issue in validation_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration is valid!")