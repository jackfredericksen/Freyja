"""
Twitter OAuth Integration for Freyja Dashboard
Allows users to login with Twitter instead of managing API keys
"""

import tweepy
import os
import logging
from typing import Optional, Dict
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterOAuthPublisher:
    """Twitter OAuth integration - no API keys needed from user"""
    
    def __init__(self):
        # App-level credentials (you only need these once for your app)
        self.app_api_key = os.getenv('TWITTER_APP_KEY', 'your_app_key_here')
        self.app_api_secret = os.getenv('TWITTER_APP_SECRET', 'your_app_secret_here')
        
        # User-specific tokens (obtained via OAuth)
        self.user_access_token = None
        self.user_access_secret = None
        
        self.client = None
        self.auth_handler = None
        
        # Initialize OAuth handler
        self._init_oauth()
        
        # Try to load saved user tokens
        self._load_user_tokens()
    
    def _init_oauth(self):
        """Initialize OAuth handler"""
        try:
            if self.app_api_key and self.app_api_secret:
                self.auth_handler = tweepy.OAuth1UserHandler(
                    self.app_api_key,
                    self.app_api_secret,
                    callback="http://localhost:8000/twitter/callback"
                )
                logger.info("OAuth handler initialized")
            else:
                logger.warning("App-level Twitter credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize OAuth: {e}")
    
    def _load_user_tokens(self):
        """Load saved user tokens from file"""
        try:
            if os.path.exists('data/twitter_user_tokens.json'):
                with open('data/twitter_user_tokens.json', 'r') as f:
                    tokens = json.load(f)
                    self.user_access_token = tokens.get('access_token')
                    self.user_access_secret = tokens.get('access_token_secret')
                    
                    if self.user_access_token and self.user_access_secret:
                        self._create_client()
                        logger.info("Loaded saved Twitter user tokens")
        except Exception as e:
            logger.error(f"Error loading user tokens: {e}")
    
    def _save_user_tokens(self, access_token: str, access_token_secret: str):
        """Save user tokens to file"""
        try:
            os.makedirs('data', exist_ok=True)
            tokens = {
                'access_token': access_token,
                'access_token_secret': access_token_secret,
                'saved_at': datetime.now().isoformat()
            }
            
            with open('data/twitter_user_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
                
            logger.info("Saved Twitter user tokens")
        except Exception as e:
            logger.error(f"Error saving user tokens: {e}")
    
    def _create_client(self):
        """Create Twitter client with user tokens"""
        try:
            if all([self.app_api_key, self.app_api_secret, self.user_access_token, self.user_access_secret]):
                # Create API v1.1 client for posting
                auth = tweepy.OAuth1UserHandler(
                    self.app_api_key,
                    self.app_api_secret,
                    self.user_access_token,
                    self.user_access_secret
                )
                
                self.client = tweepy.API(auth)
                
                # Test the connection
                try:
                    user = self.client.verify_credentials()
                    logger.info(f"Twitter client connected for user: @{user.screen_name}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to verify Twitter credentials: {e}")
                    self.client = None
                    return False
            else:
                logger.warning("Missing tokens for Twitter client creation")
                return False
        except Exception as e:
            logger.error(f"Error creating Twitter client: {e}")
            return False
    
    def get_authorization_url(self) -> Optional[str]:
        """Get Twitter authorization URL for OAuth flow"""
        try:
            if not self.auth_handler:
                return None
                
            # Get request token
            auth_url = self.auth_handler.get_authorization_url()
            
            # Save request token for later use
            self.request_token = self.auth_handler.request_token
            
            return auth_url
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            return None
    
    def complete_authorization(self, oauth_verifier: str) -> bool:
        """Complete OAuth authorization with verifier code"""
        try:
            if not self.auth_handler or not hasattr(self, 'request_token'):
                return False
            
            # Set the request token
            self.auth_handler.request_token = self.request_token
            
            # Get access token
            access_token, access_token_secret = self.auth_handler.get_access_token(oauth_verifier)
            
            # Save tokens
            self.user_access_token = access_token
            self.user_access_secret = access_token_secret
            
            # Save to file
            self._save_user_tokens(access_token, access_token_secret)
            
            # Create client
            return self._create_client()
            
        except Exception as e:
            logger.error(f"Error completing authorization: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if user is connected to Twitter"""
        return self.client is not None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get connected user information"""
        try:
            if self.client:
                user = self.client.verify_credentials()
                return {
                    'username': user.screen_name,
                    'name': user.name,
                    'followers': user.followers_count,
                    'following': user.friends_count,
                    'profile_image': user.profile_image_url_https
                }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
        return None
    
    async def publish_tweet(self, content: str) -> Dict:
        """Publish a tweet using OAuth"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Not connected to Twitter. Please login first.",
                    "message": "Twitter login required"
                }
            
            # Post tweet using API v1.1
            tweet = self.client.update_status(content)
            
            tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            
            logger.info(f"Successfully posted tweet: {tweet.id}")
            return {
                "success": True,
                "tweet_id": str(tweet.id),
                "url": tweet_url,
                "message": f"Tweet posted to @{tweet.user.screen_name}"
            }
            
        except tweepy.TooManyRequests:
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "message": "Twitter API rate limit reached"
            }
        except tweepy.Forbidden as e:
            return {
                "success": False,
                "error": f"Twitter API error: {str(e)}",
                "message": "Permission denied - check your Twitter app permissions"
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post tweet"
            }
    
    def disconnect(self):
        """Disconnect from Twitter (clear tokens)"""
        try:
            self.user_access_token = None
            self.user_access_secret = None
            self.client = None
            
            # Remove saved tokens
            if os.path.exists('data/twitter_user_tokens.json'):
                os.remove('data/twitter_user_tokens.json')
                
            logger.info("Disconnected from Twitter")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False
    
    def get_setup_instructions(self) -> Dict:
        """Get setup instructions for OAuth"""
        connected = self.is_connected()
        user_info = self.get_user_info() if connected else None
        
        return {
            "connected": connected,
            "user_info": user_info,
            "setup_type": "oauth",
            "instructions": [
                "1. Click 'Login with Twitter' button",
                "2. Authorize Freyja on Twitter",
                "3. You'll be redirected back automatically",
                "4. Start publishing tweets!"
            ],
            "benefits": [
                "✅ No API keys needed",
                "✅ Free to use", 
                "✅ One-click setup",
                "✅ Secure OAuth flow",
                "✅ Easy to disconnect"
            ],
            "note": "Uses Twitter's free OAuth - no paid API plan required"
        }

# Initialize OAuth publisher
twitter_oauth_publisher = TwitterOAuthPublisher()
