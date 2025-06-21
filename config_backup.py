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
    monitoring_interval: int = Field(default=3600)  # seconds
    max_trends_per_check: int = Field(default=20)
    
    model_config = {"env_prefix": "RESEARCH_", "extra": "allow"}

class BrandSettings(BaseSettings):
    """Brand voice and content guidelines"""
    brand_name: str = Field(default="Your Brand")
    brand_voice_tone: str = Field(default="professional")
    brand_voice_style: str = Field(default="informative")
    brand_personality: str = Field(default="helpful")
    
    max_hashtags: int = Field(default=3)
    preferred_topics: str = Field(default="tech,ai,productivity")  # Store as string, parse later
    avoid_topics: str = Field(default="politics,controversial")    # Store as string, parse later
    
    posting_frequency: str = Field(default="3-5 posts per day")
    optimal_times: str = Field(default="9:00,13:00,17:00")  # Store as string, parse later
    timezone: str = Field(default="UTC")
    
    model_config = {"env_prefix": "BRAND_", "extra": "allow"}
    
    @property
    def preferred_topics_list(self) -> List[str]:
        """Get preferred topics as a list"""
        return [topic.strip() for topic in self.preferred_topics.split(",")]
    
    @property
    def avoid_topics_list(self) -> List[str]:
        """Get avoid topics as a list"""
        return [topic.strip() for topic in self.avoid_topics.split(",")]
    
    @property
    def optimal_times_list(self) -> List[str]:
        """Get optimal times as a list"""
        return [time.strip() for time in self.optimal_times.split(",")]

class GrowthSettings(BaseSettings):
    """Growth coaching configuration"""
    follower_target: int = Field(default=10000)
    monthly_growth_rate: float = Field(default=15.0)
    engagement_rate_target: float = Field(default=5.0)
    growth_timeline: str = Field(default="6 months")
    
    coaching_frequency: str = Field(default="weekly")
    focus_areas: str = Field(default="audience_growth,engagement,content_strategy")  # Store as string
    learning_style: str = Field(default="data-driven")
    
    competitors: str = Field(default="")  # Store as string
    benchmark_metrics: str = Field(default="followers,engagement_rate,posting_frequency")  # Store as string
    
    model_config = {"env_prefix": "GROWTH_", "extra": "allow"}
    
    @property
    def focus_areas_list(self) -> List[str]:
        """Get focus areas as a list"""
        return [area.strip() for area in self.focus_areas.split(",")]
    
    @property
    def competitors_list(self) -> List[str]:
        """Get competitors as a list"""
        if not self.competitors:
            return []
        return [comp.strip() for comp in self.competitors.split(",")]
    
    @property
    def benchmark_metrics_list(self) -> List[str]:
        """Get benchmark metrics as a list"""
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

# Create global instances - simpler approach
database = DatabaseSettings()
ai = AISettings()
scheduling = SchedulingSettings()
research = ResearchSettings()
brand = BrandSettings()
growth = GrowthSettings()
security = SecuritySettings()
settings = Settings()

# Add sub-settings as attributes to main settings for compatibility
settings.database = database
settings.ai = ai
settings.scheduling = scheduling
settings.research = research
settings.brand = brand
settings.growth = growth
settings.security = security

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

def reload_settings():
    """Reload settings from environment"""
    global settings, database, ai, scheduling, research, brand, growth, security
    
    database = DatabaseSettings()
    ai = AISettings()
    scheduling = SchedulingSettings()
    research = ResearchSettings()
    brand = BrandSettings()
    growth = GrowthSettings()
    security = SecuritySettings()
    settings = Settings()
    
    # Re-attach sub-settings
    settings.database = database
    settings.ai = ai
    settings.scheduling = scheduling
    settings.research = research
    settings.brand = brand
    settings.growth = growth
    settings.security = security
    
    return settings

# Helper function to validate configuration
def validate_configuration():
    """Validate that critical configuration is present"""
    issues = []
    
    # Check for critical missing configurations
    if not settings.ai.anthropic_api_key and not settings.ai.openai_api_key:
        issues.append("No AI API keys configured")
    
    if not any([
        settings.scheduling.buffer_api_key,
        settings.scheduling.hootsuite_api_key,
        settings.scheduling.later_api_key
    ]):
        issues.append("No scheduling platform API keys configured")
    
    # Check database path is writable
    try:
        if settings.database.url.startswith("sqlite"):
            db_path = Path(settings.database.url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        issues.append(f"Database path issue: {e}")
    
    return issues

# Backward compatibility - make brand.preferred_topics work as a list
# This ensures existing code expecting lists will still work
def _patch_brand_for_backward_compatibility():
    """Patch brand settings for backward compatibility with list properties"""
    if hasattr(brand, 'preferred_topics') and isinstance(brand.preferred_topics, str):
        # Create a property that returns the list when accessed
        original_preferred_topics = brand.preferred_topics
        original_avoid_topics = brand.avoid_topics
        original_optimal_times = brand.optimal_times
        
        # Override with list versions for backward compatibility
        brand.preferred_topics = brand.preferred_topics_list
        brand.avoid_topics = brand.avoid_topics_list
        brand.optimal_times = brand.optimal_times_list

def _patch_growth_for_backward_compatibility():
    """Patch growth settings for backward compatibility with list properties"""
    if hasattr(growth, 'focus_areas') and isinstance(growth.focus_areas, str):
        # Override with list versions for backward compatibility
        growth.focus_areas = growth.focus_areas_list
        growth.competitors = growth.competitors_list
        growth.benchmark_metrics = growth.benchmark_metrics_list

# Apply backward compatibility patches
_patch_brand_for_backward_compatibility()
_patch_growth_for_backward_compatibility()

if __name__ == "__main__":
    # Test configuration loading
    print("🔧 Testing Configuration...")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.version}")
    print(f"Database URL: {settings.database.url}")
    print(f"AI Anthropic Key: {'✅ Set' if settings.ai.anthropic_api_key else '❌ Not set'}")
    print(f"Brand Name: {settings.brand.brand_name}")
    print(f"Preferred Topics: {settings.brand.preferred_topics}")
    print(f"Growth Target: {settings.growth.follower_target}")
    print(f"Focus Areas: {settings.growth.focus_areas}")
    
    # Validate configuration
    validation_issues = validate_configuration()
    if validation_issues:
        print("\n⚠️ Configuration Issues:")
        for issue in validation_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration is valid!")