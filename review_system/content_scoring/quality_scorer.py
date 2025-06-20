"""
Freyja - Content Quality Scorer
Analyzes and scores content based on engagement potential and quality metrics
"""

import re
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import math

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Content quality metrics"""
    overall_score: float
    readability_score: float
    engagement_potential: float
    hashtag_quality: float
    length_optimization: float
    emotional_appeal: float
    call_to_action_score: float
    timing_score: float
    originality_score: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'overall_score': round(self.overall_score, 2),
            'readability_score': round(self.readability_score, 2),
            'engagement_potential': round(self.engagement_potential, 2),
            'hashtag_quality': round(self.hashtag_quality, 2),
            'length_optimization': round(self.length_optimization, 2),
            'emotional_appeal': round(self.emotional_appeal, 2),
            'call_to_action_score': round(self.call_to_action_score, 2),
            'timing_score': round(self.timing_score, 2),
            'originality_score': round(self.originality_score, 2)
        }

class ContentScorer:
    """Main content quality scoring system"""
    
    def __init__(self):
        self.engagement_keywords = [
            'question', 'why', 'how', 'what', 'when', 'where', 'who',
            'tips', 'secrets', 'hack', 'trick', 'guide', 'tutorial',
            'amazing', 'incredible', 'unbelievable', 'shocking',
            'free', 'new', 'breaking', 'urgent', 'limited'
        ]
        
        self.emotional_words = {
            'positive': [
                'amazing', 'awesome', 'brilliant', 'fantastic', 'incredible',
                'love', 'excited', 'happy', 'thrilled', 'delighted',
                'success', 'win', 'achievement', 'breakthrough', 'victory'
            ],
            'negative': [
                'terrible', 'awful', 'horrible', 'disaster', 'failure',
                'angry', 'frustrated', 'disappointed', 'sad', 'worried'
            ],
            'curiosity': [
                'secret', 'hidden', 'unknown', 'mystery', 'discover',
                'reveal', 'uncover', 'behind', 'inside', 'truth'
            ]
        }
        
        self.call_to_action_phrases = [
            'what do you think', 'share your thoughts', 'comment below',
            'let me know', 'tell me', 'agree?', 'disagree?', 'thoughts?',
            'experience', 'advice', 'tips', 'suggestions', 'ideas',
            'retweet', 'share', 'follow', 'like', 'reply'
        ]
        
        self.weak_words = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'sort of', 'kind of', 'somewhat', 'rather', 'fairly'
        ]
    
    async def score_content(self, content: str, content_type: str = "tweet") -> QualityMetrics:
        """Score content across multiple quality dimensions"""
        try:
            # Calculate individual scores
            readability = self._calculate_readability_score(content)
            engagement = self._calculate_engagement_potential(content)
            hashtag_quality = self._calculate_hashtag_quality(content)
            length_opt = self._calculate_length_optimization(content, content_type)
            emotional = self._calculate_emotional_appeal(content)
            cta_score = self._calculate_call_to_action_score(content)
            timing = self._calculate_timing_score()
            originality = self._calculate_originality_score(content)
            
            # Calculate weighted overall score
            weights = {
                'readability': 0.15,
                'engagement': 0.25,
                'hashtag_quality': 0.10,
                'length_optimization': 0.10,
                'emotional_appeal': 0.15,
                'call_to_action': 0.15,
                'timing': 0.05,
                'originality': 0.05
            }
            
            overall_score = (
                readability * weights['readability'] +
                engagement * weights['engagement'] +
                hashtag_quality * weights['hashtag_quality'] +
                length_opt * weights['length_optimization'] +
                emotional * weights['emotional_appeal'] +
                cta_score * weights['call_to_action'] +
                timing * weights['timing'] +
                originality * weights['originality']
            )
            
            return QualityMetrics(
                overall_score=overall_score,
                readability_score=readability,
                engagement_potential=engagement,
                hashtag_quality=hashtag_quality,
                length_optimization=length_opt,
                emotional_appeal=emotional,
                call_to_action_score=cta_score,
                timing_score=timing,
                originality_score=originality
            )
            
        except Exception as e:
            logger.error(f"Error scoring content: {e}")
            # Return default scores
            return QualityMetrics(
                overall_score=50.0, readability_score=50.0, engagement_potential=50.0,
                hashtag_quality=50.0, length_optimization=50.0, emotional_appeal=50.0,
                call_to_action_score=50.0, timing_score=50.0, originality_score=50.0
            )
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score based on sentence structure and complexity"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Average sentence length
        words = content.split()
        avg_sentence_length = len(words) / len(sentences)
        
        # Penalize very long sentences
        length_score = max(0, 100 - (avg_sentence_length - 10) * 5)
        
        # Count complex words (3+ syllables)
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        complexity_score = max(0, 100 - (complex_words / len(words)) * 100)
        
        # Check for weak words
        weak_word_count = sum(1 for word in words if word.lower() in self.weak_words)
        weak_word_penalty = min(30, weak_word_count * 5)
        
        # Final readability score
        readability = (length_score + complexity_score) / 2 - weak_word_penalty
        return max(0, min(100, readability))
    
    def _calculate_engagement_potential(self, content: str) -> float:
        """Calculate potential for engagement based on content analysis"""
        content_lower = content.lower()
        score = 50.0  # Base score
        
        # Check for engagement keywords
        keyword_matches = sum(1 for keyword in self.engagement_keywords if keyword in content_lower)
        score += min(25, keyword_matches * 5)
        
        # Check for questions
        if '?' in content:
            score += 15
        
        # Check for numbers (people love lists and statistics)
        numbers = re.findall(r'\d+', content)
        if numbers:
            score += min(10, len(numbers) * 3)
        
        # Check for emojis (increase engagement on social media)
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
        score += min(10, emoji_count * 2)
        
        # Penalize excessive capitalization
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            score -= 20
        
        return max(0, min(100, score))
    
    def _calculate_hashtag_quality(self, content: str) -> float:
        """Evaluate hashtag usage quality"""
        hashtags = re.findall(r'#\w+', content)
        
        if not hashtags:
            return 70.0  # Neutral score for no hashtags
        
        hashtag_count = len(hashtags)
        max_recommended = settings.brand.max_hashtags
        
        # Optimal hashtag count score
        if hashtag_count <= max_recommended:
            count_score = 100
        else:
            # Penalize excessive hashtags
            count_score = max(20, 100 - (hashtag_count - max_recommended) * 15)
        
        # Check hashtag relevance (basic check for topic alignment)
        relevant_hashtags = 0
        for hashtag in hashtags:
            hashtag_clean = hashtag.lower().replace('#', '')
            if any(topic.lower() in hashtag_clean for topic in settings.brand.preferred_topics):
                relevant_hashtags += 1
        
        relevance_score = (relevant_hashtags / hashtag_count) * 100 if hashtag_count > 0 else 100
        
        # Check for hashtag length (avoid too long hashtags)
        avg_hashtag_length = sum(len(h) for h in hashtags) / len(hashtags)
        length_score = max(50, 100 - max(0, avg_hashtag_length - 15) * 3)
        
        return (count_score + relevance_score + length_score) / 3
    
    def _calculate_length_optimization(self, content: str, content_type: str) -> float:
        """Score content length optimization for the platform"""
        length = len(content)
        
        optimal_lengths = {
            'tweet': {'min': 71, 'max': 250, 'optimal': 120},
            'thread': {'min': 100, 'max': 280, 'optimal': 200},
            'reply': {'min': 50, 'max': 200, 'optimal': 100},
            'quote_tweet': {'min': 50, 'max': 200, 'optimal': 120}
        }
        
        targets = optimal_lengths.get(content_type, optimal_lengths['tweet'])
        
        if length < targets['min']:
            # Too short
            score = (length / targets['min']) * 70
        elif length > targets['max']:
            # Too long
            excess = length - targets['max']
            score = max(20, 70 - excess * 2)
        else:
            # In acceptable range
            distance_from_optimal = abs(length - targets['optimal'])
            score = max(70, 100 - distance_from_optimal * 0.5)
        
        return max(0, min(100, score))
    
    def _calculate_emotional_appeal(self, content: str) -> float:
        """Calculate emotional impact and appeal"""
        content_lower = content.lower()
        score = 50.0  # Base neutral score
        
        # Count emotional words
        emotional_impact = 0
        for category, words in self.emotional_words.items():
            matches = sum(1 for word in words if word in content_lower)
            if category == 'positive':
                emotional_impact += matches * 8
            elif category == 'negative':
                emotional_impact += matches * 6
            elif category == 'curiosity':
                emotional_impact += matches * 10
        
        score += min(30, emotional_impact)
        
        # Check for personal pronouns (increases relatability)
        personal_pronouns = ['i', 'me', 'my', 'we', 'us', 'our', 'you', 'your']
        pronoun_count = sum(1 for word in content_lower.split() if word in personal_pronouns)
        score += min(15, pronoun_count * 3)
        
        # Check for storytelling elements
        story_words = ['when', 'then', 'after', 'before', 'during', 'while']
        story_elements = sum(1 for word in story_words if word in content_lower)
        score += min(10, story_elements * 5)
        
        return max(0, min(100, score))
    
    def _calculate_call_to_action_score(self, content: str) -> float:
        """Score the presence and quality of call-to-action elements"""
        content_lower = content.lower()
        
        # Direct CTA phrases
        cta_matches = sum(1 for phrase in self.call_to_action_phrases if phrase in content_lower)
        if cta_matches > 0:
            return min(100, 80 + cta_matches * 10)
        
        # Implicit CTAs (questions, invitations)
        if '?' in content:
            return 70
        
        # Action verbs at the beginning
        action_verbs = ['try', 'use', 'check', 'read', 'watch', 'learn', 'discover']
        first_word = content.split()[0].lower() if content.split() else ''
        if first_word in action_verbs:
            return 60
        
        return 40  # No clear CTA
    
    def _calculate_timing_score(self) -> float:
        """Score based on current timing (placeholder for now)"""
        # This could be enhanced with actual audience activity data
        current_hour = datetime.now().hour
        
        # Assume peak hours are 9AM, 1PM, 5PM, 8PM
        peak_hours = [9, 13, 17, 20]
        
        if current_hour in peak_hours:
            return 100
        elif current_hour in [h-1 for h in peak_hours] or current_hour in [h+1 for h in peak_hours]:
            return 80
        else:
            return 60
    
    def _calculate_originality_score(self, content: str) -> float:
        """Basic originality check (could be enhanced with similarity checking)"""
        # Check for common phrases that might indicate template usage
        template_phrases = [
            'check out this', 'click the link', 'link in bio',
            'follow for more', 'rt if you agree'
        ]
        
        content_lower = content.lower()
        template_matches = sum(1 for phrase in template_phrases if phrase in content_lower)
        
        if template_matches > 0:
            return max(30, 80 - template_matches * 20)
        
        # Check for unique elements
        uniqueness_score = 80
        
        # Bonus for specific numbers, dates, or personal details
        if re.search(r'\b\d{4}\b', content):  # Year
            uniqueness_score += 10
        if re.search(r'\b\d+%\b', content):  # Percentage
            uniqueness_score += 10
        
        return min(100, uniqueness_score)
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting for readability analysis"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(1, syllable_count)
    
    async def get_improvement_suggestions(self, content: str, metrics: QualityMetrics) -> List[str]:
        """Generate specific improvement suggestions based on quality scores"""
        suggestions = []
        
        # Readability suggestions
        if metrics.readability_score < 70:
            if len(content.split()) / len(re.split(r'[.!?]+', content)) > 15:
                suggestions.append("💡 Break up long sentences for better readability")
            
            complex_words = sum(1 for word in content.split() if self._count_syllables(word) >= 3)
            if complex_words > len(content.split()) * 0.2:
                suggestions.append("💡 Use simpler words to improve readability")
            
            weak_words = sum(1 for word in content.split() if word.lower() in self.weak_words)
            if weak_words > 0:
                suggestions.append("💡 Replace weak words like 'maybe', 'possibly' with stronger language")
        
        # Engagement suggestions
        if metrics.engagement_potential < 70:
            if '?' not in content:
                suggestions.append("🎯 Add a question to encourage engagement")
            
            if not any(keyword in content.lower() for keyword in self.engagement_keywords):
                suggestions.append("🎯 Include engagement words like 'tips', 'secrets', or 'how to'")
            
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
            if emoji_count == 0:
                suggestions.append("🎯 Add 1-2 relevant emojis to increase engagement")
        
        # Hashtag suggestions
        if metrics.hashtag_quality < 70:
            hashtags = re.findall(r'#\w+', content)
            if len(hashtags) > settings.brand.max_hashtags:
                suggestions.append(f"#️⃣ Reduce hashtags to {settings.brand.max_hashtags} or fewer")
            elif len(hashtags) == 0:
                suggestions.append("#️⃣ Add 1-2 relevant hashtags from your preferred topics")
            
            # Check relevance
            relevant_count = 0
            for hashtag in hashtags:
                hashtag_clean = hashtag.lower().replace('#', '')
                if any(topic.lower() in hashtag_clean for topic in settings.brand.preferred_topics):
                    relevant_count += 1
            
            if hashtags and relevant_count / len(hashtags) < 0.5:
                topics = ", ".join(settings.brand.preferred_topics)
                suggestions.append(f"#️⃣ Use hashtags more relevant to your topics: {topics}")
        
        # Length suggestions
        if metrics.length_optimization < 70:
            length = len(content)
            if length < 71:
                suggestions.append("📏 Content is too short - add more detail or context")
            elif length > 250:
                suggestions.append("📏 Content is too long - consider splitting into a thread")
        
        # Emotional appeal suggestions
        if metrics.emotional_appeal < 70:
            if not any(any(word in content.lower() for word in words) for words in self.emotional_words.values()):
                suggestions.append("❤️ Add emotional words to create stronger connection")
            
            personal_pronouns = ['i', 'me', 'my', 'we', 'us', 'our', 'you', 'your']
            if not any(pronoun in content.lower().split() for pronoun in personal_pronouns):
                suggestions.append("❤️ Use personal pronouns (I, you, we) to increase relatability")
        
        # Call-to-action suggestions
        if metrics.call_to_action_score < 70:
            if '?' not in content:
                suggestions.append("📢 End with a question to encourage responses")
            else:
                suggestions.append("📢 Add a clear call-to-action like 'Share your thoughts' or 'What's your experience?'")
        
        # Originality suggestions
        if metrics.originality_score < 70:
            suggestions.append("✨ Add specific details, numbers, or personal experiences to make content more unique")
        
        return suggestions
    
    async def analyze_content_performance_potential(self, content: str, content_type: str = "tweet") -> Dict[str, Any]:
        """Comprehensive analysis of content's performance potential"""
        metrics = await self.score_content(content, content_type)
        suggestions = await self.get_improvement_suggestions(content, metrics)
        
        # Predict engagement level
        engagement_level = "Low"
        if metrics.overall_score >= 80:
            engagement_level = "High"
        elif metrics.overall_score >= 65:
            engagement_level = "Medium"
        
        # Identify strengths and weaknesses
        scores_dict = metrics.to_dict()
        strengths = [key for key, value in scores_dict.items() if value >= 80 and key != 'overall_score']
        weaknesses = [key for key, value in scores_dict.items() if value < 60 and key != 'overall_score']
        
        # Content analysis
        hashtags = re.findall(r'#\w+', content)
        mentions = re.findall(r'@\w+', content)
        word_count = len(content.split())
        char_count = len(content)
        
        return {
            'metrics': scores_dict,
            'suggestions': suggestions,
            'engagement_prediction': engagement_level,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'content_analysis': {
                'word_count': word_count,
                'character_count': char_count,
                'hashtag_count': len(hashtags),
                'mention_count': len(mentions),
                'hashtags': hashtags,
                'mentions': mentions
            },
            'optimization_priority': self._get_optimization_priority(scores_dict)
        }
    
    def _get_optimization_priority(self, scores: Dict[str, float]) -> List[str]:
        """Get prioritized list of areas to optimize"""
        # Exclude overall score and sort by impact and current score
        optimization_areas = {k: v for k, v in scores.items() if k != 'overall_score'}
        
        # Weight by importance and room for improvement
        weights = {
            'engagement_potential': 3.0,
            'call_to_action_score': 2.5,
            'emotional_appeal': 2.0,
            'readability_score': 2.0,
            'hashtag_quality': 1.5,
            'length_optimization': 1.0,
            'originality_score': 1.0,
            'timing_score': 0.5
        }
        
        # Calculate priority score (lower is higher priority)
        priority_scores = {}
        for area, score in optimization_areas.items():
            room_for_improvement = 100 - score
            weight = weights.get(area, 1.0)
            priority_scores[area] = score / weight  # Lower score = higher priority
        
        # Sort by priority (lowest score first)
        sorted_areas = sorted(priority_scores.items(), key=lambda x: x[1])
        
        return [area for area, _ in sorted_areas if optimization_areas[area] < 70]

# Brand voice checker
class BrandVoiceChecker:
    """Checks content compliance with brand guidelines"""
    
    def __init__(self):
        self.brand_settings = settings.brand
    
    async def check_compliance(self, content: str) -> Dict[str, Any]:
        """Check if content complies with brand guidelines"""
        compliance_score = 100.0
        issues = []
        recommendations = []
        
        # Check tone compliance
        tone_score = self._check_tone_compliance(content)
        compliance_score = (compliance_score + tone_score) / 2
        
        if tone_score < 70:
            issues.append(f"Content tone doesn't match brand tone: {self.brand_settings.brand_voice_tone}")
            recommendations.append(f"Adjust language to be more {self.brand_settings.brand_voice_tone}")
        
        # Check for avoided topics
        avoided_topics_found = []
        content_lower = content.lower()
        for topic in self.brand_settings.avoid_topics:
            if topic.lower() in content_lower:
                avoided_topics_found.append(topic)
                compliance_score -= 20
        
        if avoided_topics_found:
            issues.append(f"Contains avoided topics: {', '.join(avoided_topics_found)}")
            recommendations.append("Remove or rephrase content related to avoided topics")
        
        # Check hashtag compliance
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > self.brand_settings.max_hashtags:
            issues.append(f"Too many hashtags ({len(hashtags)} > {self.brand_settings.max_hashtags})")
            recommendations.append(f"Reduce to {self.brand_settings.max_hashtags} hashtags maximum")
            compliance_score -= 10
        
        # Check for preferred topics
        preferred_found = any(
            topic.lower() in content_lower 
            for topic in self.brand_settings.preferred_topics
        )
        
        if not preferred_found and hashtags:
            # Check if hashtags relate to preferred topics
            preferred_in_hashtags = any(
                any(topic.lower() in hashtag.lower() for topic in self.brand_settings.preferred_topics)
                for hashtag in hashtags
            )
            if not preferred_in_hashtags:
                recommendations.append(f"Consider including topics: {', '.join(self.brand_settings.preferred_topics)}")
        
        return {
            'compliance_score': max(0, min(100, compliance_score)),
            'issues': issues,
            'recommendations': recommendations,
            'tone_match': tone_score,
            'topic_alignment': preferred_found
        }
    
    def _check_tone_compliance(self, content: str) -> float:
        """Check if content matches brand tone"""
        content_lower = content.lower()
        
        tone_keywords = {
            'professional': {
                'positive': ['expertise', 'experience', 'professional', 'quality', 'reliable', 'efficient'],
                'negative': ['casual', 'whatever', 'dunno', 'gonna', 'wanna']
            },
            'casual': {
                'positive': ['hey', 'awesome', 'cool', 'fun', 'easy', 'simple'],
                'negative': ['furthermore', 'therefore', 'subsequently', 'nevertheless']
            },
            'friendly': {
                'positive': ['welcome', 'help', 'support', 'thanks', 'appreciate', 'community'],
                'negative': ['demand', 'require', 'must', 'should', 'need to']
            },
            'authoritative': {
                'positive': ['proven', 'research', 'studies', 'data', 'evidence', 'expert'],
                'negative': ['maybe', 'possibly', 'perhaps', 'might', 'could']
            }
        }
        
        target_tone = self.brand_settings.brand_voice_tone.lower()
        if target_tone not in tone_keywords:
            return 75.0  # Neutral score for unknown tones
        
        keywords = tone_keywords[target_tone]
        
        positive_matches = sum(1 for word in keywords['positive'] if word in content_lower)
        negative_matches = sum(1 for word in keywords['negative'] if word in content_lower)
        
        # Calculate tone score
        base_score = 75.0
        base_score += positive_matches * 10
        base_score -= negative_matches * 15
        
        return max(0, min(100, base_score))

# Testing function
async def test_content_scoring():
    """Test the content scoring system"""
    scorer = ContentScorer()
    brand_checker = BrandVoiceChecker()
    
    test_content = """
    🧠 AI Development tip: Always validate your training data first! 
    
    I learned this the hard way when my model started making weird predictions. 
    Turns out there were duplicates and errors in my dataset.
    
    What's your biggest AI development mistake? Share below! 👇
    
    #MachineLearning #AI #DataScience
    """
    
    print("Testing content scoring...")
    print(f"Content: {test_content}")
    print("-" * 50)
    
    # Get quality metrics
    metrics = await scorer.score_content(test_content, "tweet")
    print("Quality Metrics:")
    for key, value in metrics.to_dict().items():
        print(f"  {key}: {value}")
    
    print("-" * 50)
    
    # Get improvement suggestions
    suggestions = await scorer.get_improvement_suggestions(test_content, metrics)
    print("Improvement Suggestions:")
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("-" * 50)
    
    # Check brand compliance
    compliance = await brand_checker.check_compliance(test_content)
    print("Brand Compliance:")
    print(f"  Score: {compliance['compliance_score']}")
    print(f"  Issues: {compliance['issues']}")
    print(f"  Recommendations: {compliance['recommendations']}")
    
    print("-" * 50)
    
    # Full analysis
    analysis = await scorer.analyze_content_performance_potential(test_content, "tweet")
    print("Performance Analysis:")
    print(f"  Engagement Prediction: {analysis['engagement_prediction']}")
    print(f"  Strengths: {analysis['strengths']}")
    print(f"  Weaknesses: {analysis['weaknesses']}")
    print(f"  Optimization Priority: {analysis['optimization_priority']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_content_scoring())