"""
Freyja - Complete Modern Scheduling Manager with Fixed Username Handling
FIXED VERSION - No more "yourhandle" placeholders
"""

import asyncio
import aiohttp
import json
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

@dataclass
class ScheduledPost:
    """Data structure for scheduled posts"""
    id: str
    content: str
    scheduled_time: datetime
    platform: str
    status: str  # scheduled, posted, failed, cancelled
    platform_post_id: Optional[str] = None
    media_urls: List[str] = None
    hashtags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.media_urls is None:
            self.media_urls = []
        if self.hashtags is None:
            self.hashtags = []
        if self.metadata is None:
            self.metadata = {}

class TwitterDirectAPI:
    """Direct Twitter API v2 integration with working OAuth 1.0a authentication"""
    
    def __init__(self, bearer_token: str, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com/2"
        self.user_info = None  # Store user info for URL generation
    
    def _create_oauth_signature(self, method: str, url: str, params: Dict = None) -> Dict[str, str]:
        """Create OAuth 1.0a signature for Twitter API"""
        if params is None:
            params = {}
        
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_token': self.access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': self._generate_nonce(),
            'oauth_version': '1.0'
        }
        
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Create parameter string
        sorted_params = sorted(all_params.items())
        param_string = '&'.join([
            f"{self._percent_encode(str(k))}={self._percent_encode(str(v))}"
            for k, v in sorted_params
        ])
        
        # Create signature base string
        base_string = '&'.join([
            method.upper(),
            self._percent_encode(url),
            self._percent_encode(param_string)
        ])
        
        # Create signing key
        signing_key = '&'.join([
            self._percent_encode(self.api_secret),
            self._percent_encode(self.access_token_secret)
        ])
        
        # Create signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode('utf-8'),
                base_string.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        oauth_params['oauth_signature'] = signature
        return oauth_params
    
    def _generate_nonce(self) -> str:
        """Generate a unique nonce"""
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _percent_encode(self, string: str) -> str:
        """Percent encode string according to RFC 3986"""
        return urllib.parse.quote(str(string), safe='')
    
    def _create_auth_header(self, method: str, url: str, params: Dict = None) -> str:
        """Create OAuth authorization header"""
        oauth_params = self._create_oauth_signature(method, url, params)
        
        auth_header = 'OAuth ' + ', '.join([
            f'{self._percent_encode(k)}="{self._percent_encode(v)}"'
            for k, v in sorted(oauth_params.items())
        ])
        
        return auth_header
    
    async def post_tweet(self, content: str, media_urls: List[str] = None, 
                        reply_to_id: str = None) -> Dict:
        """Post directly to Twitter/X with proper username handling"""
        try:
            url = f"{self.base_url}/tweets"
            
            payload = {"text": content}
            
            if reply_to_id:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}
            
            if media_urls:
                # For now, we'll handle text-only posts
                # Media upload would require additional API calls
                logger.warning("Media upload not yet implemented")
            
            # Use OAuth 1.0a for posting (required for write operations)
            auth_header = self._create_auth_header("POST", url)
            
            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_text = await response.text()
                    
                    if response.status == 201:
                        result = json.loads(response_text)
                        tweet_id = result.get('data', {}).get('id')
                        
                        # Get username for proper URL generation
                        username = await self._get_username()
                        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                        
                        logger.info(f"Tweet posted successfully: {tweet_id} by @{username}")
                        return {
                            "success": True,
                            "tweet_id": tweet_id,
                            "url": tweet_url,
                            "username": username,
                            "data": result
                        }
                    else:
                        logger.error(f"Twitter API error: {response.status} - {response_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_username(self) -> str:
        """Get the authenticated user's username"""
        if self.user_info and 'username' in self.user_info:
            return self.user_info['username']
        
        # Fetch user info if not cached
        user_info = await self.get_user_info()
        if user_info and not user_info.get('error'):
            username = user_info.get('data', {}).get('username', 'twitter_user')
            self.user_info = {'username': username}
            return username
        
        return 'twitter_user'  # Better fallback than 'yourhandle'
    
    async def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        try:
            url = f"{self.base_url}/users/me"
            auth_header = self._create_auth_header("GET", url)
            
            headers = {
                "Authorization": auth_header
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cache user info
                        if 'data' in data:
                            self.user_info = {
                                'username': data['data'].get('username'),
                                'name': data['data'].get('name'),
                                'id': data['data'].get('id')
                            }
                        return data
                    else:
                        error = await response.text()
                        return {"error": f"HTTP {response.status}: {error}"}
                        
        except Exception as e:
            return {"error": str(e)}
    
    async def authenticate(self) -> bool:
        """Test authentication"""
        user_info = await self.get_user_info()
        if "error" not in user_info:
            username = user_info.get('data', {}).get('username', 'unknown')
            logger.info(f"Twitter authentication successful: @{username}")
            return True
        else:
            logger.error(f"Twitter authentication failed: {user_info.get('error')}")
            return False

class SimpleScheduler:
    """File-based scheduler with JSON storage"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = settings.data_dir / "scheduled_posts.json"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.scheduled_posts = self._load_posts()
    
    def _load_posts(self) -> List[Dict]:
        """Load scheduled posts from file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.error("Corrupted schedule file, starting fresh")
            return []
    
    def _save_posts(self):
        """Save scheduled posts to file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.scheduled_posts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving scheduled posts: {e}")
    
    async def schedule_post(self, content: str, scheduled_time: datetime, 
                           platform: str = "twitter", metadata: Dict = None) -> str:
        """Schedule a post"""
        post_id = f"post_{len(self.scheduled_posts) + 1}_{int(datetime.now().timestamp())}"
        
        post = {
            "id": post_id,
            "content": content,
            "scheduled_time": scheduled_time.isoformat(),
            "platform": platform,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.scheduled_posts.append(post)
        self._save_posts()
        
        logger.info(f"Post scheduled: {post_id} for {scheduled_time}")
        return post_id
    
    async def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts as ScheduledPost objects"""
        scheduled_posts = []
        
        for post_data in self.scheduled_posts:
            if post_data.get("status") == "scheduled":
                scheduled_post = ScheduledPost(
                    id=post_data["id"],
                    content=post_data["content"],
                    scheduled_time=datetime.fromisoformat(post_data["scheduled_time"]),
                    platform=post_data["platform"],
                    status=post_data["status"],
                    platform_post_id=post_data.get("platform_post_id"),
                    metadata=post_data.get("metadata", {})
                )
                scheduled_posts.append(scheduled_post)
        
        return scheduled_posts
    
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        for post in self.scheduled_posts:
            if post["id"] == post_id and post["status"] == "scheduled":
                post["status"] = "cancelled"
                post["cancelled_at"] = datetime.now().isoformat()
                self._save_posts()
                logger.info(f"Post cancelled: {post_id}")
                return True
        return False
    
    async def update_post(self, post_id: str, content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post"""
        for post in self.scheduled_posts:
            if post["id"] == post_id and post["status"] == "scheduled":
                post["content"] = content
                post["scheduled_time"] = scheduled_time.isoformat()
                post["updated_at"] = datetime.now().isoformat()
                self._save_posts()
                logger.info(f"Post updated: {post_id}")
                return True
        return False
    
    def mark_posted(self, post_id: str, platform_post_id: str = None, username: str = None):
        """Mark a post as successfully posted"""
        for post in self.scheduled_posts:
            if post["id"] == post_id:
                post["status"] = "posted"
                post["posted_at"] = datetime.now().isoformat()
                if platform_post_id:
                    post["platform_post_id"] = platform_post_id
                if username:
                    post["username"] = username
                break
        self._save_posts()
    
    def mark_failed(self, post_id: str, error: str):
        """Mark a post as failed to post"""
        for post in self.scheduled_posts:
            if post["id"] == post_id:
                post["status"] = "failed"
                post["failed_at"] = datetime.now().isoformat()
                post["error"] = error
                break
        self._save_posts()

class ModernSchedulingManager:
    """Unified scheduling manager with multiple platform support"""
    
    def __init__(self):
        self.platforms = {}
        self.simple_scheduler = SimpleScheduler()
        self._initialize_platforms()
    
    def _initialize_platforms(self):
        """Initialize available scheduling platforms"""
        
        # Twitter Direct API (if configured)
        if (hasattr(settings.scheduling, 'twitter_bearer_token') and 
            settings.scheduling.twitter_bearer_token and
            hasattr(settings.scheduling, 'twitter_api_key') and
            settings.scheduling.twitter_api_key):
            
            self.platforms['twitter'] = TwitterDirectAPI(
                bearer_token=settings.scheduling.twitter_bearer_token,
                api_key=settings.scheduling.twitter_api_key,
                api_secret=settings.scheduling.twitter_api_secret,
                access_token=settings.scheduling.twitter_access_token,
                access_token_secret=settings.scheduling.twitter_access_token_secret
            )
            logger.info("Twitter Direct API initialized")
        
        # Always include simple scheduler as fallback
        self.platforms['simple'] = self.simple_scheduler
        logger.info(f"Scheduling platforms available: {list(self.platforms.keys())}")
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all configured platforms"""
        results = {}
        
        for platform_name, platform in self.platforms.items():
            if platform_name == 'simple':
                results[platform_name] = True  # Simple scheduler doesn't need auth
                continue
                
            try:
                if hasattr(platform, 'authenticate'):
                    results[platform_name] = await platform.authenticate()
                else:
                    results[platform_name] = True
            except Exception as e:
                logger.error(f"Error authenticating {platform_name}: {e}")
                results[platform_name] = False
        
        return results
    
    async def schedule_post(self, content: str, scheduled_time: datetime, 
                           platform_name: str = "simple", **kwargs) -> str:
        """Schedule a post on a specific platform"""
        
        # Always store in simple scheduler for tracking
        post_id = await self.simple_scheduler.schedule_post(
            content=content,
            scheduled_time=scheduled_time,
            platform=platform_name,
            metadata=kwargs
        )
        
        # If scheduled for immediate posting and platform supports it
        if (scheduled_time <= datetime.now() + timedelta(minutes=5) and 
            platform_name in self.platforms and 
            platform_name != 'simple'):
            
            return await self._post_immediately(post_id, content, platform_name, **kwargs)
        
        return post_id
    
    async def _post_immediately(self, post_id: str, content: str, 
                               platform_name: str, **kwargs) -> str:
        """Post immediately to the platform"""
        try:
            platform = self.platforms[platform_name]
            
            if platform_name == 'twitter':
                result = await platform.post_tweet(
                    content=content,
                    media_urls=kwargs.get('media_urls', [])
                )
                
                if result.get('success'):
                    username = result.get('username', 'twitter_user')
                    self.simple_scheduler.mark_posted(
                        post_id, 
                        result.get('tweet_id'),
                        username
                    )
                    logger.info(f"Posted immediately to Twitter: {result.get('tweet_id')} by @{username}")
                else:
                    self.simple_scheduler.mark_failed(post_id, result.get('error', 'Unknown error'))
                    logger.error(f"Failed to post to Twitter: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Error posting immediately to {platform_name}: {e}")
            self.simple_scheduler.mark_failed(post_id, str(e))
        
        return post_id
    
    async def post_now(self, content: str, platform_name: str = "twitter", **kwargs) -> Dict:
        """Post immediately to a platform"""
        if platform_name not in self.platforms:
            return {"success": False, "error": f"Platform {platform_name} not available"}
        
        platform = self.platforms[platform_name]
        
        if platform_name == 'twitter':
            return await platform.post_tweet(content, **kwargs)
        
        return {"success": False, "error": "Platform posting not implemented"}
    
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        return await self.simple_scheduler.cancel_post(post_id)
    
    async def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts"""
        return await self.simple_scheduler.get_scheduled_posts()
    
    async def update_post(self, post_id: str, content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post"""
        return await self.simple_scheduler.update_post(post_id, content, scheduled_time)
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self.platforms.keys())
    
    async def process_due_posts(self) -> List[Dict]:
        """Process posts that are due for posting"""
        results = []
        scheduled_posts = await self.get_scheduled_posts()
        now = datetime.now()
        
        for post in scheduled_posts:
            if post.scheduled_time <= now and post.platform in self.platforms:
                if post.platform == 'simple':
                    # Skip simple scheduler posts - they're for manual posting
                    continue
                
                result = await self._post_immediately(
                    post.id, 
                    post.content, 
                    post.platform
                )
                results.append({
                    "post_id": post.id,
                    "platform": post.platform,
                    "result": result
                })
        
        return results
    
    async def get_posting_reminders(self, hours_ahead: int = 2) -> List[Dict]:
        """Get posts that need manual posting soon"""
        scheduled_posts = await self.get_scheduled_posts()
        now = datetime.now()
        future_time = now + timedelta(hours=hours_ahead)
        
        reminders = []
        for post in scheduled_posts:
            if (post.platform == 'simple' and 
                now <= post.scheduled_time <= future_time):
                reminders.append({
                    "id": post.id,
                    "content": post.content,
                    "scheduled_time": post.scheduled_time,
                    "platform": post.platform
                })
        
        return sorted(reminders, key=lambda x: x["scheduled_time"])

# Utility functions
def get_optimal_posting_times(platform: str = "twitter", timezone: str = "UTC") -> List[str]:
    """Get optimal posting times for a platform"""
    optimal_times = {
        "twitter": ["09:00", "12:00", "15:00", "18:00"],
        "linkedin": ["08:00", "12:00", "17:00", "18:00"],
        "facebook": ["09:00", "13:00", "15:00"]
    }
    
    return optimal_times.get(platform, optimal_times["twitter"])

def calculate_next_optimal_time(platform: str = "twitter") -> datetime:
    """Calculate the next optimal posting time"""
    now = datetime.now()
    optimal_times = get_optimal_posting_times(platform)
    
    for time_str in optimal_times:
        hour, minute = map(int, time_str.split(':'))
        optimal_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if optimal_time > now:
            return optimal_time
    
    # If no more optimal times today, return first optimal time tomorrow
    tomorrow = now + timedelta(days=1)
    hour, minute = map(int, optimal_times[0].split(':'))
    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

# Testing and usage examples
async def test_twitter_posting():
    """Test Twitter posting functionality"""
    manager = ModernSchedulingManager()
    
    print("🐦 Testing Twitter Integration...")
    
    # Test authentication
    auth_results = await manager.authenticate_all()
    print(f"Authentication results: {auth_results}")
    
    if auth_results.get('twitter'):
        # Test immediate posting
        result = await manager.post_now(
            content="Test post from Freyja! 🚀 #testing #automation",
            platform_name="twitter"
        )
        
        if result.get('success'):
            username = result.get('username', 'unknown')
            print(f"✅ Posted to Twitter successfully: {result.get('tweet_id')} by @{username}")
        else:
            print(f"❌ Failed to post to Twitter: {result.get('error')}")
    
    # Test scheduling
    future_time = datetime.now() + timedelta(hours=1)
    post_id = await manager.schedule_post(
        content="This is a scheduled test post! 📅",
        scheduled_time=future_time,
        platform_name="simple"
    )
    
    print(f"📅 Scheduled post: {post_id}")
    
    # Show scheduled posts
    scheduled = await manager.get_scheduled_posts()
    print(f"📋 Total scheduled posts: {len(scheduled)}")

async def test_scheduling_workflow():
    """Test the complete scheduling workflow"""
    manager = ModernSchedulingManager()
    
    print("🔄 Testing Complete Scheduling Workflow...")
    
    # Schedule posts for different times
    posts = [
        {
            "content": "Morning motivation! 🌅 Start your day with purpose. #motivation #productivity",
            "time": datetime.now() + timedelta(hours=8),
            "platform": "twitter"
        },
        {
            "content": "Lunch break tip: Take 5 minutes to review your goals. 🎯 #productivity #goals",
            "time": datetime.now() + timedelta(hours=12),
            "platform": "simple"
        },
        {
            "content": "End of day reflection: What did you learn today? 🤔 #learning #growth",
            "time": datetime.now() + timedelta(hours=18),
            "platform": "simple"
        }
    ]
    
    scheduled_ids = []
    for post in posts:
        post_id = await manager.schedule_post(
            content=post["content"],
            scheduled_time=post["time"],
            platform_name=post["platform"]
        )
        scheduled_ids.append(post_id)
        print(f"✅ Scheduled: {post_id}")
    
    # Get posting reminders
    reminders = await manager.get_posting_reminders(hours_ahead=24)
    print(f"\n📋 Posts due in next 24 hours: {len(reminders)}")
    
    for reminder in reminders:
        print(f"   {reminder['id']}: {reminder['content'][:50]}...")
        print(f"   📅 Due: {reminder['scheduled_time'].strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    # Run tests
    print("🧪 Testing Modern Scheduling Manager...")
    
    # Test basic functionality
    asyncio.run(test_scheduling_workflow())
    
    # Test Twitter if configured
    if (hasattr(settings.scheduling, 'twitter_bearer_token') and 
        settings.scheduling.twitter_bearer_token):
        asyncio.run(test_twitter_posting())
    else:
        print("⚠️ Twitter API not configured - skipping Twitter tests")
        print("💡 Add Twitter API keys to .env to test direct posting")