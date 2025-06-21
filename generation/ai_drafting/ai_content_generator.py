"""
Freyja - AI Content Generator
Claude-powered content generation system
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class ClaudeContentGenerator:
    """Claude-powered content generation"""
    
    def __init__(self):
        self.api_key = settings.ai.anthropic_api_key
        self.model = "claude-3-5-sonnet-20241022"
    
    async def generate_content(self, prompt: str, content_type: str = "tweet") -> str:
        """Generate content using Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            system_prompt = f"""You are a social media content creator for {settings.brand.brand_name}. 
            Create engaging {content_type} content that is:
            - {settings.brand.brand_voice_tone} in tone
            - {settings.brand.brand_voice_style} in style
            - {settings.brand.brand_personality} in personality
            - Focused on topics: {', '.join(settings.brand.preferred_topics) if hasattr(settings.brand, 'preferred_topics') else 'general topics'}
            - Maximum {settings.brand.max_hashtags} hashtags
            """
            
            response = client.messages.create(
                model=self.model,
                max_tokens=settings.ai.max_tokens,
                temperature=settings.ai.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            logger.info(f"Generated {content_type} content successfully")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content with Claude: {e}")
            return f"Error generating content: {e}"
    
    async def generate_tweet(self, topic: str) -> str:
        """Generate a tweet about a specific topic"""
        prompt = f"Create an engaging tweet about {topic}. Make it informative and include relevant hashtags."
        return await self.generate_content(prompt, "tweet")
    
    async def generate_thread(self, topic: str, thread_length: int = 3) -> List[str]:
        """Generate a Twitter thread"""
        prompt = f"Create a {thread_length}-part Twitter thread about {topic}. Each part should be engaging and under 280 characters."
        
        content = await self.generate_content(prompt, "thread")
        
        # Split into thread parts (basic implementation)
        parts = content.split('\n\n')
        return parts[:thread_length]

async def test_content_generation() -> bool:
    """Test Claude content generation functionality"""
    try:
        if not settings.ai.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return False
        
        generator = ClaudeContentGenerator()
        
        # Test basic content generation
        test_prompt = "Create a short tweet about the importance of AI ethics in technology development."
        
        content = await generator.generate_content(test_prompt, "tweet")
        
        if content and len(content) > 10 and not content.startswith("Error"):
            logger.info("Claude content generation test successful")
            return True
        else:
            logger.error("Claude content generation test failed")
            return False
            
    except ImportError:
        logger.error("Anthropic library not installed. Run: pip install anthropic")
        return False
    except Exception as e:
        logger.error(f"Content generation test error: {e}")
        return False

# Usage example
async def generate_sample_content():
    """Generate some sample content"""
    generator = ClaudeContentGenerator()
    
    # Generate a tweet
    tweet = await generator.generate_tweet("artificial intelligence trends")
    print("Generated Tweet:")
    print(tweet)
    
    # Generate a thread
    thread = await generator.generate_thread("productivity tips for developers", 3)
    print("\nGenerated Thread:")
    for i, part in enumerate(thread, 1):
        print(f"{i}/ {part}")

if __name__ == "__main__":
    asyncio.run(test_content_generation())