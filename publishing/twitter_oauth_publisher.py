"""
Fixed Twitter OAuth Integration for Freyja Dashboard
Uses API v1.1 which works with FREE Twitter tier
"""

import tweepy
import os
import logging
from typing import Optional, Dict
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterOAuthPublisher:
    """Fixed Twitter OAuth integration - uses v1.1 API for free tier"""
    
    def __init__(self):
        # App-level credentials
        self.app_api_key = os.getenv('TWITTER_APP_KEY')
        self.app_api_secret = os.getenv('TWITTER_APP_SECRET')
        
        # User-specific tokens and info
        self.user_access_token = None
        self.user_access_secret = None
        self.user_info = None
        
        self.client = None  # This will be API v1.1 client
        self.auth_handler = None
        
        # Initialize OAuth handler
        self._init_oauth()
        
        # Try to load saved user tokens
        self._load_user_tokens()
    
    def _init_oauth(self):
        """Initialize OAuth handler"""
        try:
            if not self.app_api_key or not self.app_api_secret:
                logger.error("Twitter app credentials not found in environment variables")
                return
            
            callback_url = "http://localhost:8000/twitter/callback"
            
            self.auth_handler = tweepy.OAuth1UserHandler(
                consumer_key=self.app_api_key,
                consumer_secret=self.app_api_secret,
                callback=callback_url
            )
            
            logger.info(f"OAuth handler initialized with callback: {callback_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OAuth: {e}")
    
    def _load_user_tokens(self):
        """Load saved user tokens and info from file"""
        try:
            token_file = 'data/twitter_user_tokens.json'
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
                    self.user_access_token = tokens.get('access_token')
                    self.user_access_secret = tokens.get('access_token_secret')
                    self.user_info = tokens.get('user_info')
                    
                    if self.user_access_token and self.user_access_secret:
                        self._create_client()
                        logger.info("Loaded saved Twitter user tokens and info")
        except Exception as e:
            logger.error(f"Error loading user tokens: {e}")
    
    def _save_user_tokens(self, access_token: str, access_token_secret: str, user_info: Dict = None):
        """Save user tokens and info to file"""
        try:
            os.makedirs('data', exist_ok=True)
            tokens = {
                'access_token': access_token,
                'access_token_secret': access_token_secret,
                'user_info': user_info,
                'saved_at': datetime.now().isoformat()
            }
            
            with open('data/twitter_user_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
                
            logger.info("Saved Twitter user tokens and info")
        except Exception as e:
            logger.error(f"Error saving user tokens: {e}")
    
    def _create_client(self):
        """Create Twitter API v1.1 client (works with free tier)"""
        try:
            if not all([self.app_api_key, self.app_api_secret, self.user_access_token, self.user_access_secret]):
                logger.warning("Missing tokens for Twitter client creation")
                return False
            
            # Create OAuth 1.0a auth for API v1.1
            auth = tweepy.OAuth1UserHandler(
                consumer_key=self.app_api_key,
                consumer_secret=self.app_api_secret,
                access_token=self.user_access_token,
                access_token_secret=self.user_access_secret
            )
            
            # Use API v1.1 client (works with free tier)
            self.client = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test connection and get user info
            try:
                user = self.client.verify_credentials()
                self.user_info = {
                    'username': user.screen_name,
                    'name': user.name,
                    'followers': user.followers_count,
                    'following': user.friends_count,
                    'profile_image': user.profile_image_url_https,
                    'user_id': user.id_str
                }
                
                # Save updated user info
                self._save_user_tokens(
                    self.user_access_token, 
                    self.user_access_secret, 
                    self.user_info
                )
                
                logger.info(f"Twitter API v1.1 client connected for user: @{user.screen_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to verify Twitter credentials: {e}")
                self.client = None
                return False
                
        except Exception as e:
            logger.error(f"Error creating Twitter client: {e}")
            return False
    
    def get_authorization_url(self) -> Optional[str]:
        """Get Twitter authorization URL for OAuth flow"""
        try:
            if not self.auth_handler:
                logger.error("OAuth handler not initialized")
                return None
            
            if not self.app_api_key or not self.app_api_secret:
                logger.error("App credentials missing")
                return None
            
            # Get request token and authorization URL
            auth_url = self.auth_handler.get_authorization_url()
            
            # Save request token for callback
            self.request_token = self.auth_handler.request_token
            
            logger.info(f"Generated authorization URL: {auth_url}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            return None
    
    def complete_authorization(self, oauth_verifier: str) -> bool:
        """Complete OAuth authorization with verifier code"""
        try:
            if not self.auth_handler or not hasattr(self, 'request_token'):
                logger.error("Missing auth handler or request token")
                return False
            
            # Set the request token
            self.auth_handler.request_token = self.request_token
            
            # Get access token
            access_token, access_token_secret = self.auth_handler.get_access_token(oauth_verifier)
            
            # Save tokens
            self.user_access_token = access_token
            self.user_access_secret = access_token_secret
            
            # Create client and get user info
            success = self._create_client()
            
            return success
            
        except Exception as e:
            logger.error(f"Error completing authorization: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if user is connected to Twitter"""
        return self.client is not None and self.user_info is not None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get connected user information"""
        if self.user_info:
            return self.user_info
        
        # Try to get fresh user info if we have a client
        try:
            if self.client:
                user = self.client.verify_credentials()
                self.user_info = {
                    'username': user.screen_name,
                    'name': user.name,
                    'followers': user.followers_count,
                    'following': user.friends_count,
                    'profile_image': user.profile_image_url_https,
                    'user_id': user.id_str
                }
                return self.user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
        
        return None
    
    async def publish_tweet(self, content: str) -> Dict:
        """Publish a tweet using API v1.1 (works with FREE tier)"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Not connected to Twitter. Please login first.",
                    "message": "Twitter login required"
                }
            
            # Get user info to build correct URL
            user_info = self.get_user_info()
            if not user_info:
                return {
                    "success": False,
                    "error": "Cannot get user information",
                    "message": "Failed to get Twitter user info"
                }
            
            # Post tweet using API v1.1 (FREE TIER COMPATIBLE)
            logger.info(f"Posting tweet via API v1.1: {content[:50]}...")
            tweet = self.client.update_status(content)
            
            # Build correct URL using actual username
            username = user_info['username']
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            
            logger.info(f"Successfully posted tweet: {tweet.id} by @{username}")
            return {
                "success": True,
                "tweet_id": str(tweet.id),
                "url": tweet_url,
                "username": username,
                "message": f"Tweet posted to @{username}",
                "method": "api_v1.1"
            }
            
        except tweepy.TooManyRequests:
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "message": "Twitter API rate limit reached"
            }
        except tweepy.Forbidden as e:
            logger.error(f"Twitter API Forbidden error: {e}")
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
        """Disconnect from Twitter (clear tokens and user info)"""
        try:
            self.user_access_token = None
            self.user_access_secret = None
            self.user_info = None
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
            "api_version": "v1.1",
            "free_tier_compatible": True,
            "instructions": [
                "1. Click 'Login with Twitter' button",
                "2. Authorize Freyja on Twitter",
                "3. You'll be redirected back automatically",
                "4. Start publishing tweets!"
            ],
            "benefits": [
                "✅ Works with FREE Twitter API tier",
                "✅ No monthly fees required", 
                "✅ One-click setup",
                "✅ Secure OAuth flow",
                "✅ Real tweet posting"
            ],
            "troubleshooting": [
                "• Make sure your Twitter app has OAuth 1.0a enabled",
                "• Verify callback URL: http://localhost:8000/twitter/callback",
                "• Check that app permissions include 'Read and Write'",
                "• Ensure TWITTER_APP_KEY and TWITTER_APP_SECRET are correct"
            ],
            "note": "Uses Twitter's API v1.1 via OAuth - compatible with Essential (free) access tier"
        }

# Initialize OAuth publisher
twitter_oauth_publisher = TwitterOAuthPublisher()