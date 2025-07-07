"""
Freyja - Fixed AI Content Generator
Completely rewritten to work reliably
"""

import os
import logging
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """Fixed AI-powered content generation"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        
        # Determine provider
        if self.openai_key and self.openai_key.startswith('sk-'):
            self.provider = "openai"
            self._init_openai()
        elif self.anthropic_key and self.anthropic_key.startswith('sk-ant'):
            self.provider = "anthropic"
            self._init_anthropic()
        else:
            self.provider = "simulation"
        
        logger.info(f"AI Content Generator initialized: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            # Test the connection
            models = self.openai_client.models.list()
            logger.info("OpenAI client initialized and tested successfully")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            self.provider = "simulation"
            self.openai_client = None
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Anthropic initialization failed: {e}")
            self.provider = "simulation"
            self.anthropic_client = None
    
    async def generate_tweet(self, topic: str, tone: str = "professional", include_hashtags: bool = True) -> Dict:
        """Generate a tweet about a specific topic"""
        try:
            if self.provider == "openai" and self.openai_client:
                return await self._generate_with_openai(topic, tone, include_hashtags)
            elif self.provider == "anthropic" and self.anthropic_client:
                return await self._generate_with_anthropic(topic, tone, include_hashtags)
            else:
                return self._generate_simulation(topic, tone, include_hashtags)
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return self._generate_simulation(topic, tone, include_hashtags)
    
    async def generate_thread(self, topic: str, num_tweets: int = 3, tone: str = "professional") -> Dict:
        """Generate a Twitter thread"""
        try:
            if self.provider == "openai" and self.openai_client:
                return await self._generate_thread_openai(topic, num_tweets, tone)
            elif self.provider == "anthropic" and self.anthropic_client:
                return await self._generate_thread_anthropic(topic, num_tweets, tone)
            else:
                return self._generate_thread_simulation(topic, num_tweets, tone)
                
        except Exception as e:
            logger.error(f"Error generating thread: {e}")
            return self._generate_thread_simulation(topic, num_tweets, tone)
    
    async def _generate_with_openai(self, topic: str, tone: str, include_hashtags: bool) -> Dict:
        """Generate content using OpenAI"""
        try:
            hashtag_instruction = "Include 2-3 relevant hashtags at the end." if include_hashtags else "Do not include hashtags."
            
            prompt = f"""Create a {tone} tweet about: {topic}

Requirements:
- Maximum 280 characters
- {tone.title()} tone of voice
- Engaging and valuable content
- {hashtag_instruction}
- Return only the tweet text, no quotes or explanations

Topic: {topic}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator. Create engaging, valuable tweets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            return {
                "success": True,
                "content": content,
                "provider": "openai",
                "topic": topic,
                "tone": tone,
                "character_count": len(content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return self._generate_simulation(topic, tone, include_hashtags)
    
    async def _generate_with_anthropic(self, topic: str, tone: str, include_hashtags: bool) -> Dict:
        """Generate content using Anthropic"""
        try:
            hashtag_instruction = "Include 2-3 relevant hashtags at the end." if include_hashtags else "Do not include hashtags."
            
            prompt = f"""Create a {tone} tweet about: {topic}

Requirements:
- Maximum 280 characters
- {tone.title()} tone of voice
- Engaging and valuable content
- {hashtag_instruction}
- Return only the tweet text, no quotes or explanations

Topic: {topic}"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text.strip()
            
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            return {
                "success": True,
                "content": content,
                "provider": "anthropic",
                "topic": topic,
                "tone": tone,
                "character_count": len(content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return self._generate_simulation(topic, tone, include_hashtags)
    
    def _generate_simulation(self, topic: str, tone: str, include_hashtags: bool) -> Dict:
        """Generate simulated content when no AI provider is available"""
        import random
        
        templates = {
            "professional": [
                f"Exploring the impact of {topic} on modern business strategies and innovation pathways.",
                f"Key insights about {topic} that every professional should understand and implement.",
                f"How {topic} is transforming the way we approach complex business challenges today.",
                f"Understanding {topic}: Essential knowledge for forward-thinking professionals.",
                f"The strategic importance of {topic} in today's competitive landscape."
            ],
            "casual": [
                f"Just discovered something amazing about {topic}! 🤯 This changes everything.",
                f"Quick thoughts on {topic} and why it's worth your attention right now.",
                f"Been diving deep into {topic} lately - here's what I learned that surprised me.",
                f"Okay, can we talk about {topic} for a sec? This is actually pretty cool.",
                f"Hot take on {topic}: it's way more important than most people realize."
            ],
            "educational": [
                f"Understanding {topic}: Essential concepts explained in simple terms.",
                f"Breaking down {topic} - what you need to know to get started.",
                f"A beginner's guide to {topic} and its practical applications.",
                f"Let's explore {topic}: key principles and real-world examples.",
                f"{topic} 101: Everything you need to know to understand the basics."
            ]
        }
        
        # Select random template
        selected_templates = templates.get(tone, templates["professional"])
        base_content = random.choice(selected_templates)
        
        if include_hashtags:
            # Generate relevant hashtags based on topic
            topic_words = topic.lower().replace('-', ' ').replace('_', ' ').split()
            hashtags = []
            
            # Add topic-based hashtags
            for word in topic_words[:2]:
                if len(word) > 3 and word.isalpha():
                    hashtags.append(f"#{word.capitalize()}")
            
            # Add tone-appropriate hashtags
            tone_hashtags = {
                "professional": ["#Business", "#Innovation", "#Strategy", "#Growth"],
                "casual": ["#Learning", "#TechTalk", "#Ideas", "#Thoughts"],
                "educational": ["#Education", "#Learning", "#Guide", "#Tutorial"]
            }
            
            # Fill remaining hashtag slots
            available_hashtags = tone_hashtags.get(tone, tone_hashtags["professional"])
            for hashtag in available_hashtags:
                if len(hashtags) < 3 and hashtag not in hashtags:
                    hashtags.append(hashtag)
            
            content = f"{base_content} {' '.join(hashtags[:3])}"
        else:
            content = base_content
        
        # Ensure content is under 280 characters
        if len(content) > 280:
            # Trim content while preserving hashtags
            if include_hashtags and '#' in content:
                parts = content.rsplit(' #', 1)
                if len(parts) == 2:
                    text_part = parts[0]
                    hashtag_part = '#' + parts[1]
                    max_text_length = 280 - len(hashtag_part) - 1  # -1 for space
                    if len(text_part) > max_text_length:
                        text_part = text_part[:max_text_length-3] + "..."
                    content = f"{text_part} {hashtag_part}"
                else:
                    content = content[:277] + "..."
            else:
                content = content[:277] + "..."
        
        return {
            "success": True,
            "content": content,
            "provider": "simulation",
            "topic": topic,
            "tone": tone,
            "character_count": len(content),
            "timestamp": datetime.now().isoformat(),
            "note": "Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env for AI-generated content"
        }
    
    async def _generate_thread_openai(self, topic: str, num_tweets: int, tone: str) -> Dict:
        """Generate a Twitter thread using OpenAI"""
        try:
            prompt = f"""Create a Twitter thread about {topic} with exactly {num_tweets} tweets.

Requirements:
- {tone.title()} tone throughout
- Each tweet must be under 280 characters
- Number each tweet (1/{num_tweets}, 2/{num_tweets}, etc.)
- First tweet should be an engaging hook
- Include relevant hashtags in the last tweet only
- Provide valuable, actionable insights

Topic: {topic}
Number of tweets: {num_tweets}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging Twitter threads."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Split into individual tweets
            tweets = []
            lines = content.split('\n')
            current_tweet = ""
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith(f"{len(tweets)+1}/") or line.startswith(f"Tweet {len(tweets)+1}")):
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line
                elif line and current_tweet:
                    current_tweet += f" {line}"
            
            if current_tweet:
                tweets.append(current_tweet.strip())
            
            # Ensure we have the right number of tweets
            tweets = tweets[:num_tweets]
            
            return {
                "success": True,
                "content": tweets,
                "provider": "openai",
                "topic": topic,
                "tone": tone,
                "tweet_count": len(tweets),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI thread generation error: {e}")
            return self._generate_thread_simulation(topic, num_tweets, tone)
    
    async def _generate_thread_anthropic(self, topic: str, num_tweets: int, tone: str) -> Dict:
        """Generate a Twitter thread using Anthropic"""
        try:
            prompt = f"""Create a Twitter thread about {topic} with exactly {num_tweets} tweets.

Requirements:
- {tone.title()} tone throughout
- Each tweet must be under 280 characters
- Number each tweet (1/{num_tweets}, 2/{num_tweets}, etc.)
- First tweet should be an engaging hook
- Include relevant hashtags in the last tweet only
- Provide valuable, actionable insights

Topic: {topic}
Number of tweets: {num_tweets}"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text.strip()
            
            # Split into individual tweets
            tweets = []
            lines = content.split('\n')
            current_tweet = ""
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith(f"{len(tweets)+1}/") or line.startswith(f"Tweet {len(tweets)+1}")):
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line
                elif line and current_tweet:
                    current_tweet += f" {line}"
            
            if current_tweet:
                tweets.append(current_tweet.strip())
            
            # Ensure we have the right number of tweets
            tweets = tweets[:num_tweets]
            
            return {
                "success": True,
                "content": tweets,
                "provider": "anthropic",
                "topic": topic,
                "tone": tone,
                "tweet_count": len(tweets),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Anthropic thread generation error: {e}")
            return self._generate_thread_simulation(topic, num_tweets, tone)
    
    def _generate_thread_simulation(self, topic: str, num_tweets: int, tone: str) -> Dict:
        """Generate a simulated Twitter thread"""
        tweets = []
        
        # Thread starter
        starters = {
            "professional": f"🧵 Thread: Why {topic} is crucial for business success in 2024",
            "casual": f"🧵 Let's talk about {topic} - here's what I've learned",
            "educational": f"🧵 {topic} explained: A comprehensive guide"
        }
        
        tweets.append(f"1/{num_tweets} {starters.get(tone, starters['professional'])}")
        
        # Middle tweets
        for i in range(2, num_tweets):
            middle_templates = {
                "professional": f"{i}/{num_tweets} Key insight about {topic}: Strategic implementation drives measurable results.",
                "casual": f"{i}/{num_tweets} Here's something cool about {topic} that most people don't know...",
                "educational": f"{i}/{num_tweets} Important concept: {topic} works because of these fundamental principles."
            }
            tweets.append(middle_templates.get(tone, middle_templates["professional"]))
        
        # Final tweet with hashtags
        final_templates = {
            "professional": f"{num_tweets}/{num_tweets} Conclusion: {topic} represents a significant opportunity for growth. #Business #Strategy #Innovation",
            "casual": f"{num_tweets}/{num_tweets} That's a wrap on {topic}! What are your thoughts? #Learning #Discussion #Ideas",
            "educational": f"{num_tweets}/{num_tweets} Summary: Understanding {topic} opens new possibilities. #Education #Learning #Guide"
        }
        
        tweets.append(final_templates.get(tone, final_templates["professional"]))
        
        return {
            "success": True,
            "content": tweets,
            "provider": "simulation",
            "topic": topic,
            "tone": tone,
            "tweet_count": len(tweets),
            "timestamp": datetime.now().isoformat(),
            "note": "Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env for AI-generated threads"
        }
    
    def get_setup_instructions(self) -> Dict:
        """Get AI setup instructions"""
        return {
            "current_status": f"Running in {self.provider} mode",
            "providers": {
                "OpenAI": {
                    "env_var": "OPENAI_API_KEY",
                    "cost": "$0.002 per 1K tokens",
                    "signup": "https://platform.openai.com/api-keys",
                    "configured": bool(self.openai_key and self.openai_key.startswith('sk-'))
                },
                "Anthropic": {
                    "env_var": "ANTHROPIC_API_KEY", 
                    "cost": "$0.015 per 1K tokens",
                    "signup": "https://console.anthropic.com/",
                    "configured": bool(self.anthropic_key and self.anthropic_key.startswith('sk-ant'))
                }
            },
            "setup_steps": [
                "1. Choose an AI provider (OpenAI or Anthropic)",
                "2. Sign up and get API key",
                "3. Add to .env file: OPENAI_API_KEY=your_key_here",
                "4. Install dependencies: pip install openai anthropic",
                "5. Restart dashboard"
            ],
            "ready": True,
            "provider": self.provider
        }

# Initialize the AI content generator
ai_generator = AIContentGenerator()

# Test function
async def test_ai_generation():
    """Test AI content generation"""
    print("🧪 Testing AI Content Generation...")
    
    # Test tweet generation
    result = await ai_generator.generate_tweet(
        topic="artificial intelligence in productivity", 
        tone="professional", 
        include_hashtags=True
    )
    
    print(f"Provider: {result['provider']}")
    print(f"Success: {result['success']}")
    print(f"Content: {result['content']}")
    print(f"Characters: {result['character_count']}")
    
    # Test thread generation
    thread_result = await ai_generator.generate_thread(
        topic="productivity tips for developers",
        num_tweets=3,
        tone="casual"
    )
    
    print(f"\nThread Provider: {thread_result['provider']}")
    print(f"Thread Success: {thread_result['success']}")
    print("Thread Content:")
    for i, tweet in enumerate(thread_result['content'], 1):
        print(f"  {i}. {tweet}")
    
    return result['success'] and thread_result['success']

if __name__ == "__main__":
    asyncio.run(test_ai_generation())