"""
Real Twitter API Integration for Freyja
"""

import tweepy
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TwitterPublisher:
    """Real Twitter API integration using Tweepy"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twitter API client"""
        try:
            if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter API client initialized successfully")
            else:
                logger.warning("Twitter API credentials not found - using simulation mode")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
    
    async def publish_tweet(self, content: str) -> dict:
        """Publish a tweet to Twitter"""
        try:
            if self.client:
                response = self.client.create_tweet(text=content)
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                logger.info(f"Successfully posted tweet: {tweet_id}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "message": "Tweet posted successfully"
                }
            else:
                import uuid
                fake_id = str(uuid.uuid4())[:10]
                fake_url = f"https://twitter.com/yourhandle/status/{fake_id}"
                
                logger.info("Posted tweet in simulation mode")
                return {
                    "success": True,
                    "tweet_id": fake_id,
                    "url": fake_url,
                    "message": "Tweet posted (simulation mode)"
                }
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post tweet"
            }
    
    def get_setup_instructions(self) -> dict:
        """Get instructions for setting up Twitter API"""
        return {
            "steps": [
                "1. Go to https://developer.twitter.com/en/portal/dashboard",
                "2. Create a new app or use existing app",
                "3. Generate API keys and tokens",
                "4. Add these to your .env file:",
                "   TWITTER_API_KEY=your_api_key",
                "   TWITTER_API_SECRET=your_api_secret", 
                "   TWITTER_ACCESS_TOKEN=your_access_token",
                "   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret",
                "   TWITTER_BEARER_TOKEN=your_bearer_token",
                "5. Install tweepy: pip install tweepy",
                "6. Restart your dashboard"
            ],
            "cost": "Twitter API v2 Basic: $100/month for posting tweets",
            "note": "Without credentials, system runs in simulation mode"
        }

# Initialize the Twitter publisher
twitter_publisher = TwitterPublisher()
