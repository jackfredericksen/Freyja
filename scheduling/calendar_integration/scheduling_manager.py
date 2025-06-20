"""
Freyja - Scheduling Integration System
Integrates with Buffer, Hootsuite, and other scheduling platforms
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging
from urllib.parse import urlencode

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

class SchedulingPlatform(ABC):
    """Abstract base class for scheduling platforms"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def schedule_post(self, content: str, scheduled_time: datetime, **kwargs) -> str:
        """Schedule a post and return the platform post ID"""
        pass
    
    @abstractmethod
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        pass
    
    @abstractmethod
    async def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts"""
        pass
    
    @abstractmethod
    async def update_post(self, post_id: str, content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post"""
        pass

class BufferIntegration(SchedulingPlatform):
    """Buffer API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.scheduling.buffer_api_key
        self.base_url = "https://api.bufferapp.com/1"
        self.session = None
        self.profiles = {}
    
    async def authenticate(self) -> bool:
        """Authenticate with Buffer API"""
        try:
            if not self.api_key:
                logger.error("Buffer API key not configured")
                return False
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/user.json"
                params = {"access_token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Buffer authentication successful for user: {user_data.get('id')}")
                        
                        # Get profiles (social media accounts)
                        await self._load_profiles()
                        return True
                    else:
                        logger.error(f"Buffer authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Buffer authentication error: {e}")
            return False
    
    async def _load_profiles(self):
        """Load user's social media profiles"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/profiles.json"
                params = {"access_token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        profiles_data = await response.json()
                        self.profiles = {
                            profile['service']: profile['id'] 
                            for profile in profiles_data 
                            if profile.get('service') in ['twitter', 'linkedin', 'facebook']
                        }
                        logger.info(f"Loaded Buffer profiles: {list(self.profiles.keys())}")
                    else:
                        logger.error(f"Failed to load Buffer profiles: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error loading Buffer profiles: {e}")
    
    async def schedule_post(self, content: str, scheduled_time: datetime, 
                           platform: str = "twitter", media_urls: List[str] = None, **kwargs) -> str:
        """Schedule a post on Buffer"""
        try:
            profile_id = self.profiles.get(platform)
            if not profile_id:
                raise ValueError(f"No {platform} profile found in Buffer")
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/updates/create.json"
                
                data = {
                    "access_token": self.api_key,
                    "profile_ids[]": profile_id,
                    "text": content,
                    "scheduled_at": int(scheduled_time.timestamp())
                }
                
                # Add media if provided
                if media_urls:
                    for i, media_url in enumerate(media_urls):
                        data[f"media[link][{i}]"] = media_url
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        post_id = result.get('id')
                        logger.info(f"Post scheduled on Buffer: {post_id}")
                        return post_id
                    else:
                        error_text = await response.text()
                        logger.error(f"Buffer scheduling failed: {response.status} - {error_text}")
                        raise Exception(f"Buffer API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error scheduling post on Buffer: {e}")
            raise
    
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post on Buffer"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/updates/{post_id}/destroy.json"
                data = {"access_token": self.api_key}
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        logger.info(f"Post cancelled on Buffer: {post_id}")
                        return True
                    else:
                        logger.error(f"Failed to cancel Buffer post: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error cancelling Buffer post: {e}")
            return False
    
    async def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get scheduled posts from Buffer"""
        try:
            scheduled_posts = []
            
            for platform, profile_id in self.profiles.items():
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_url}/profiles/{profile_id}/updates/pending.json"
                    params = {"access_token": self.api_key}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            updates = await response.json()
                            
                            for update in updates.get('updates', []):
                                scheduled_post = ScheduledPost(
                                    id=update['id'],
                                    content=update['text'],
                                    scheduled_time=datetime.fromtimestamp(update['due_at']),
                                    platform=platform,
                                    status='scheduled',
                                    platform_post_id=update['id'],
                                    created_at=datetime.fromtimestamp(update['created_at']),
                                    metadata={
                                        'buffer_profile_id': profile_id,
                                        'buffer_update_type': update.get('update_type', 'text')
                                    }
                                )
                                scheduled_posts.append(scheduled_post)
            
            return scheduled_posts
            
        except Exception as e:
            logger.error(f"Error getting Buffer scheduled posts: {e}")
            return []
    
    async def update_post(self, post_id: str, content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post on Buffer"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/updates/{post_id}/update.json"
                
                data = {
                    "access_token": self.api_key,
                    "text": content,
                    "scheduled_at": int(scheduled_time.timestamp())
                }
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        logger.info(f"Post updated on Buffer: {post_id}")
                        return True
                    else:
                        logger.error(f"Failed to update Buffer post: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error updating Buffer post: {e}")
            return False

class HootsuiteIntegration(SchedulingPlatform):
    """Hootsuite API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.scheduling.hootsuite_api_key
        self.base_url = "https://platform.hootsuite.com/v1"
        self.social_profiles = {}
    
    async def authenticate(self) -> bool:
        """Authenticate with Hootsuite API"""
        try:
            if not self.api_key:
                logger.error("Hootsuite API key not configured")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/me"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Hootsuite authentication successful for: {user_data.get('id')}")
                        
                        # Load social profiles
                        await self._load_social_profiles()
                        return True
                    else:
                        logger.error(f"Hootsuite authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Hootsuite authentication error: {e}")
            return False
    
    async def _load_social_profiles(self):
        """Load social media profiles"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/socialProfiles"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        profiles_data = await response.json()
                        
                        for profile in profiles_data.get('data', []):
                            profile_type = profile.get('type', '').lower()
                            if profile_type in ['twitter', 'linkedin', 'facebook']:
                                self.social_profiles[profile_type] = profile['id']
                        
                        logger.info(f"Loaded Hootsuite profiles: {list(self.social_profiles.keys())}")
                    else:
                        logger.error(f"Failed to load Hootsuite profiles: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error loading Hootsuite profiles: {e}")
    
    async def schedule_post(self, content: str, scheduled_time: datetime, 
                           platform: str = "twitter", media_urls: List[str] = None, **kwargs) -> str:
        """Schedule a post on Hootsuite"""
        try:
            profile_id = self.social_profiles.get(platform)
            if not profile_id:
                raise ValueError(f"No {platform} profile found in Hootsuite")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": content,
                "socialProfileIds": [profile_id],
                "scheduledSendTime": scheduled_time.isoformat() + "Z"
            }
            
            # Add media if provided
            if media_urls:
                payload["media"] = [{"url": url} for url in media_urls]
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/messages"
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        post_id = result.get('data', {}).get('id')
                        logger.info(f"Post scheduled on Hootsuite: {post_id}")
                        return post_id
                    else:
                        error_text = await response.text()
                        logger.error(f"Hootsuite scheduling failed: {response.status} - {error_text}")
                        raise Exception(f"Hootsuite API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error scheduling post on Hootsuite: {e}")
            raise
    
    async def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post on Hootsuite"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/messages/{post_id}"
                
                async with session.delete(url, headers=headers) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Post cancelled on Hootsuite: {post_id}")
                        return True
                    else:
                        logger.error(f"Failed to cancel Hootsuite post: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error cancelling Hootsuite post: {e}")
            return False
    
    async def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get scheduled posts from Hootsuite"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            scheduled_posts = []
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/messages"
                params = {"state": "SCHEDULED"}
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        messages_data = await response.json()
                        
                        for message in messages_data.get('data', []):
                            # Determine platform from social profile
                            platform = "unknown"
                            for prof_type, prof_id in self.social_profiles.items():
                                if prof_id in message.get('socialProfileIds', []):
                                    platform = prof_type
                                    break
                            
                            scheduled_post = ScheduledPost(
                                id=message['id'],
                                content=message['text'],
                                scheduled_time=datetime.fromisoformat(message['scheduledSendTime'].rstrip('Z')),
                                platform=platform,
                                status='scheduled',
                                platform_post_id=message['id'],
                                metadata={
                                    'hootsuite_state': message.get('state'),
                                    'hootsuite_profile_ids': message.get('socialProfileIds', [])
                                }
                            )
                            scheduled_posts.append(scheduled_post)
            
            return scheduled_posts
            
        except Exception as e:
            logger.error(f"Error getting Hootsuite scheduled posts: {e}")
            return []
    
    async def update_post(self, post_id: str, content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post on Hootsuite"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": content,
                "scheduledSendTime": scheduled_time.isoformat() + "Z"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/messages/{post_id}"
                
                async with session.put(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Post updated on Hootsuite: {post_id}")
                        return True
                    else:
                        logger.error(f"Failed to update Hootsuite post: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error updating Hootsuite post: {e}")
            return False

class SchedulingManager:
    """Unified scheduling manager that works with multiple platforms"""
    
    def __init__(self):
        self.platforms = {}
        self._initialize_platforms()
    
    def _initialize_platforms(self):
        """Initialize available scheduling platforms"""
        if settings.scheduling.buffer_api_key:
            self.platforms['buffer'] = BufferIntegration()
        
        if settings.scheduling.hootsuite_api_key:
            self.platforms['hootsuite'] = HootsuiteIntegration()
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all configured platforms"""
        results = {}
        
        for platform_name, platform in self.platforms.items():
            try:
                results[platform_name] = await platform.authenticate()
            except Exception as e:
                logger.error(f"Error authenticating {platform_name}: {e}")
                results[platform_name] = False
        
        return results
    
    async def schedule_post(self, content: str, scheduled_time: datetime, 
                           platform_name: str, social_platform: str = "twitter", 
                           media_urls: List[str] = None, **kwargs) -> str:
        """Schedule a post on a specific platform"""
        if platform_name not in self.platforms:
            raise ValueError(f"Platform {platform_name} not configured")
        
        platform = self.platforms[platform_name]
        return await platform.schedule_post(
            content=content,
            scheduled_time=scheduled_time,
            platform=social_platform,
            media_urls=media_urls,
            **kwargs
        )
    
    async def cancel_post(self, platform_name: str, post_id: str) -> bool:
        """Cancel a scheduled post"""
        if platform_name not in self.platforms:
            return False
        
        platform = self.platforms[platform_name]
        return await platform.cancel_post(post_id)
    
    async def get_all_scheduled_posts(self) -> Dict[str, List[ScheduledPost]]:
        """Get scheduled posts from all platforms"""
        all_posts = {}
        
        for platform_name, platform in self.platforms.items():
            try:
                posts = await platform.get_scheduled_posts()
                all_posts[platform_name] = posts
            except Exception as e:
                logger.error(f"Error getting posts from {platform_name}: {e}")
                all_posts[platform_name] = []
        
        return all_posts
    
    async def update_post(self, platform_name: str, post_id: str, 
                         content: str, scheduled_time: datetime) -> bool:
        """Update a scheduled post"""
        if platform_name not in self.platforms:
            return False
        
        platform = self.platforms[platform_name]
        return await platform.update_post(post_id, content, scheduled_time)
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available scheduling platforms"""
        return list(self.platforms.keys())
    
    async def batch_schedule(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Schedule multiple posts across platforms"""
        results = []
        
        for post_data in posts:
            try:
                post_id = await self.schedule_post(**post_data)
                results.append({
                    "success": True,
                    "post_id": post_id,
                    "platform": post_data.get("platform_name"),
                    "content": post_data.get("content")[:50] + "..."
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "platform": post_data.get("platform_name"),
                    "content": post_data.get("content")[:50] + "..."
                })
        
        return results

# Utility functions for optimal timing
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

# Usage example
async def main():
    """Example usage of the scheduling system"""
    manager = SchedulingManager()
    
    # Authenticate with all platforms
    auth_results = await manager.authenticate_all()
    print("Authentication results:", auth_results)
    
    # Schedule a test post
    if any(auth_results.values()):
        platform_name = next(name for name, success in auth_results.items() if success)
        
        try:
            post_id = await manager.schedule_post(
                content="Test post from Freyja! 🚀 #Testing #Automation",
                scheduled_time=calculate_next_optimal_time(),
                platform_name=platform_name,
                social_platform="twitter"
            )
            print(f"Post scheduled: {post_id}")
            
            # Get all scheduled posts
            all_posts = await manager.get_all_scheduled_posts()
            print(f"Total scheduled posts: {sum(len(posts) for posts in all_posts.values())}")
            
        except Exception as e:
            print(f"Error scheduling post: {e}")

if __name__ == "__main__":
    asyncio.run(main())