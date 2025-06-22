"""
Freyja - Content Quality Scorer
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class QualityScores:
    overall: float
    engagement_potential: float
    readability: float
    relevance: float
    brand_alignment: float
    technical_quality: float
    details: Dict[str, Any]

class ContentScorer:
    """Scores content quality across multiple dimensions"""
    
    def __init__(self):
        pass
    
    async def score_content(self, content: str, content_type: str = "tweet") -> QualityScores:
        """Score content across all quality dimensions"""
        # Simple scoring logic
        length_score = min(1.0, len(content) / 100)
        engagement_score = 0.7 if "?" in content else 0.5
        readability_score = 0.8
        relevance_score = 0.7
        brand_score = 0.8
        technical_score = 0.9 if content.strip() else 0.3
        
        overall = (length_score + engagement_score + readability_score + 
                  relevance_score + brand_score + technical_score) / 6
        
        return QualityScores(
            overall=round(overall, 3),
            engagement_potential=round(engagement_score, 3),
            readability=round(readability_score, 3),
            relevance=round(relevance_score, 3),
            brand_alignment=round(brand_score, 3),
            technical_quality=round(technical_score, 3),
            details={"calculated_at": datetime.now().isoformat()}
        )
    
    async def get_improvement_suggestions(self, content: str, scores: QualityScores) -> List[str]:
        """Get suggestions for improving content"""
        suggestions = []
        
        if scores.overall < 0.6:
            suggestions.append("Consider revising content for better quality")
        if "?" not in content:
            suggestions.append("Add a question to encourage engagement")
        if len(content) < 30:
            suggestions.append("Add more substance to your content")
            
        return suggestions
