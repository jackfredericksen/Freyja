"""
AI Content Generator for Freyja
"""

import os
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """AI-powered content generation"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.openai_api_key:
            try:
                import openai
                openai.api_key = self.openai_api_key
                self.provider = "openai"
            except ImportError:
                self.provider = "simulation"
        elif self.anthropic_api_key:
            self.provider = "anthropic"
        else:
            self.provider = "simulation"
        
        logger.info(f"AI Content Generator initialized with provider: {self.provider}")
    
    async def generate_tweet(self, topic: str, tone: str = "professional", include_hashtags: bool = True) -> Dict:
        """Generate a tweet about a specific topic"""
        try:
            if self.provider == "openai":
                return await self._generate_with_openai(topic, tone, include_hashtags)
            else:
                return self._generate_simulation(topic, tone, include_hashtags)
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": f"Error generating content about {topic}"
            }
    
    async def generate_thread(self, topic: str, num_tweets: int = 3, tone: str = "professional") -> Dict:
        """Generate a Twitter thread"""
        try:
            if self.provider == "openai":
                return await self._generate_thread_openai(topic, num_tweets, tone)
            else:
                return self._generate_thread_simulation(topic, num_tweets, tone)
                
        except Exception as e:
            logger.error(f"Error generating thread: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": [f"Error generating thread about {topic}"]
            }
    
    async def _generate_with_openai(self, topic: str, tone: str, include_hashtags: bool) -> Dict:
        """Generate content using OpenAI"""
        try:
            import openai
            
            hashtag_instruction = "Include 2-3 relevant hashtags." if include_hashtags else "Do not include hashtags."
            
            prompt = f"""Create a {tone} tweet about {topic}.
            
Requirements:
- Maximum 280 characters
- {tone.title()} tone
- Engaging and valuable
- {hashtag_instruction}
- No quotes around the content

Topic: {topic}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": content,
                "provider": "openai",
                "topic": topic,
                "tone": tone,
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return self._generate_simulation(topic, tone, include_hashtags)
    
    def _generate_simulation(self, topic: str, tone: str, include_hashtags: bool) -> Dict:
        """Generate simulated content when no AI provider is available"""
        
        templates = {
            "professional": [
                f"Exploring the impact of {topic} on modern business strategies.",
                f"Understanding {topic}: Key insights for implementation.",
                f"How {topic} is reshaping industry standards."
            ],
            "casual": [
                f"Just discovered something cool about {topic}!",
                f"Quick thoughts on {topic} and why it matters.",
                f"Breaking down {topic} in simple terms."
            ],
            "educational": [
                f"Let's dive into {topic}: Here are the fundamentals.",
                f"Key concepts in {topic} explained simply.",
                f"Understanding {topic} - a beginner's guide."
            ]
        }
        
        import random
        base_content = random.choice(templates.get(tone, templates["professional"]))
        
        if include_hashtags:
            topic_words = topic.lower().split()
            hashtags = []
            
            for word in topic_words[:2]:
                if len(word) > 2:
                    hashtags.append(f"#{word.capitalize()}")
            
            if len(hashtags) < 2:
                hashtags.extend(["#Innovation", "#Technology"])
            
            hashtag_str = " ".join(hashtags[:3])
            content = f"{base_content} {hashtag_str}"
        else:
            content = base_content
        
        if len(content) > 280:
            content = content[:277] + "..."
        
        return {
            "success": True,
            "content": content,
            "provider": "simulation",
            "topic": topic,
            "tone": tone,
            "character_count": len(content),
            "note": "Add OPENAI_API_KEY to .env for AI-generated content"
        }
    
    async def _generate_thread_openai(self, topic: str, num_tweets: int, tone: str) -> Dict:
        """Generate a Twitter thread using OpenAI"""
        try:
            import openai
            
            prompt = f"""Create a Twitter thread about {topic} with {num_tweets} tweets.

Requirements:
- {tone.title()} tone
- Each tweet max 280 characters
- First tweet should be engaging hook
- Use thread numbering (1/{num_tweets}, 2/{num_tweets}, etc.)
- Include relevant hashtags in the last tweet

Topic: {topic}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            tweets = content.split('\n\n')[:num_tweets]
            
            return {
                "success": True,
                "content": tweets,
                "provider": "openai",
                "topic": topic,
                "tone": tone,
                "tweet_count": len(tweets)
            }
            
        except Exception as e:
            logger.error(f"OpenAI thread generation error: {e}")
            return self._generate_thread_simulation(topic, num_tweets, tone)
    
    def _generate_thread_simulation(self, topic: str, num_tweets: int, tone: str) -> Dict:
        """Generate a simulated Twitter thread"""
        
        tweets = []
        for i in range(num_tweets):
            if i == 0:
                tweets.append(f"1/{num_tweets} Let's explore {topic} and why it matters.")
            elif i == num_tweets - 1:
                tweets.append(f"{i+1}/{num_tweets} Key takeaways on {topic}. #Innovation #Tech")
            else:
                tweets.append(f"{i+1}/{num_tweets} Important insight about {topic}.")
        
        return {
            "success": True,
            "content": tweets,
            "provider": "simulation",
            "topic": topic,
            "tone": tone,
            "tweet_count": len(tweets),
            "note": "Add OPENAI_API_KEY to .env for AI-generated threads"
        }
    
    def get_setup_instructions(self) -> Dict:
        """Get AI setup instructions"""
        return {
            "providers": {
                "OpenAI": {
                    "env_var": "OPENAI_API_KEY",
                    "cost": "$0.002 per 1K tokens",
                    "signup": "https://platform.openai.com/api-keys"
                },
                "Anthropic": {
                    "env_var": "ANTHROPIC_API_KEY", 
                    "cost": "$0.015 per 1K tokens",
                    "signup": "https://console.anthropic.com/"
                }
            },
            "setup_steps": [
                "1. Choose an AI provider (OpenAI recommended)",
                "2. Sign up and get API key",
                "3. Add to .env file: OPENAI_API_KEY=your_key_here",
                "4. Install dependencies: pip install openai",
                "5. Restart dashboard"
            ],
            "current_status": f"Running in {self.provider} mode"
        }

# Initialize the AI content generator
ai_generator = AIContentGenerator()
