"""
Freyja - Brand Voice Checker
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
from enum import Enum

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"

@dataclass
class ComplianceResult:
    level: ComplianceLevel
    score: float
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]

class BrandVoiceChecker:
    """Checks content compliance with brand voice guidelines"""
    
    def __init__(self, brand_config: Optional[Dict] = None):
        self.brand_config = brand_config or self._get_default_config()
        
    def _get_default_config(self) -> Dict:
        return {
            "voice": {"tone": "professional", "style": "informative", "personality": "helpful"},
            "guidelines": {
                "max_hashtags": 3,
                "preferred_topics": ["tech", "ai", "productivity"],
                "avoid_topics": ["politics", "controversial"],
                "forbidden_words": ["spam", "clickbait", "urgent"],
                "character_limits": {"tweet": 280, "thread": 280, "reply": 280}
            }
        }
    
    async def check_compliance(self, content: str, content_type: str = "tweet") -> ComplianceResult:
        """Check content compliance with brand guidelines"""
        issues = []
        suggestions = []
        details = {}
        
        # Basic checks
        char_limit = self.brand_config["guidelines"]["character_limits"].get(content_type, 280)
        if len(content) > char_limit:
            issues.append(f"Content exceeds {char_limit} character limit")
        
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > self.brand_config["guidelines"]["max_hashtags"]:
            issues.append("Too many hashtags")
        
        details["hashtag_count"] = len(hashtags)
        score = max(0.0, 1.0 - (len(issues) * 0.3))
        level = ComplianceLevel.COMPLIANT if score > 0.7 else ComplianceLevel.WARNING
        
        return ComplianceResult(
            level=level, score=score, issues=issues, 
            suggestions=suggestions, details=details
        )
