"""
Real Twitter API Integration for Freyja
FIXED VERSION - No more "yourhandle" placeholders
"""

import tweepy
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class TwitterPublisher:
    """Real Twitter API integration using Tweepy with proper username handling"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        self.client = None
        self.user_info = None
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
                
                # Get user info for URL generation
                self._fetch_user_info()
                logger.info("Twitter API client initialized successfully")
            else:
                logger.warning("Twitter API credentials not found - using simulation mode")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
    
    def _fetch_user_info(self):
        """Fetch user information for proper URL generation"""
        try:
            if self.client:
                # Get authenticated user info
                me = self.client.get_me()
                if me.data:
                    self.user_info = {
                        'username': me.data.username,
                        'name': me.data.name,
                        'id': me.data.id
                    }
                    logger.info(f"Fetched user info for @{me.data.username}")
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
    
    async def publish_tweet(self, content: str) -> dict:
        """Publish a tweet to Twitter with correct URL generation"""
        try:
            if self.client and self.user_info:
                # Post tweet using API v2
                response = self.client.create_tweet(text=content)
                tweet_id = response.data['id']
                
                # Generate correct URL using actual username
                username = self.user_info['username']
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                
                logger.info(f"Successfully posted tweet: {tweet_id} by @{username}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "username": username,
                    "message": f"Tweet posted to @{username}"
                }
            
            elif self.client:
                # Client exists but no user info - try to post anyway
                response = self.client.create_tweet(text=content)
                tweet_id = response.data['id']
                
                # Try to get username from the response or use placeholder
                username = "twitter_user"  # Better fallback than "yourhandle"
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                
                logger.info(f"Posted tweet {tweet_id} (username unknown)")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "url": tweet_url,
                    "username": username,
                    "message": "Tweet posted successfully"
                }
            
            else:
                # Simulation mode with better handling
                import uuid
                fake_id = str(uuid.uuid4())[:10]
                username = "demo_user"  # Better than "yourhandle"
                fake_url = f"https://twitter.com/{username}/status/{fake_id}"
                
                logger.info("Posted tweet in simulation mode")
                return {
                    "success": True,
                    "tweet_id": fake_id,
                    "url": fake_url,
                    "username": username,
                    "message": "Tweet posted (simulation mode)",
                    "simulation": True
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
        connected = self.client is not None
        username = self.user_info.get('username') if self.user_info else None
        
        return {
            "connected": connected,
            "username": username,
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
            "note": f"Currently {'connected' if connected else 'not connected'}",
            "current_user": f"@{username}" if username else "No user info"
        }

# Initialize the Twitter publisher
twitter_publisher = TwitterPublisher()