"""
Complete Twitter Authentication Fix with all imports
"""

import asyncio
import aiohttp
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TwitterDirectAPI:
    """Direct Twitter API v2 integration with fixed OAuth 1.0a"""
    
    def __init__(self, bearer_token: str, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com/2"
    
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
    
    async def authenticate(self) -> bool:
        """Test authentication with simplified approach"""
        try:
            # Use a simpler endpoint for testing
            url = f"{self.base_url}/users/me"
            
            auth_header = self._create_auth_header("GET", url)
            
            headers = {
                "Authorization": auth_header
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        username = user_data.get('data', {}).get('username', 'unknown')
                        logger.info(f"Twitter authentication successful: @{username}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Twitter authentication failed: HTTP {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Twitter authentication error: {e}")
            return False
    
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
                        return await response.json()
                    else:
                        error = await response.text()
                        return {"error": f"HTTP {response.status}: {error}"}
                        
        except Exception as e:
            return {"error": str(e)}

# Test function for the fixed authentication
async def test_twitter_auth_fix():
    """Test the fixed Twitter authentication"""
    print("🐦 Testing Fixed Twitter Authentication...")
    
    try:
        from config import get_settings
        settings = get_settings()
        
        # Check if we have the required keys
        if not all([
            settings.scheduling.twitter_bearer_token,
            settings.scheduling.twitter_api_key,
            settings.scheduling.twitter_api_secret,
            settings.scheduling.twitter_access_token,
            settings.scheduling.twitter_access_token_secret
        ]):
            print("❌ Missing Twitter API keys")
            return False
        
        twitter_api = TwitterDirectAPI(
            bearer_token=settings.scheduling.twitter_bearer_token,
            api_key=settings.scheduling.twitter_api_key,
            api_secret=settings.scheduling.twitter_api_secret,
            access_token=settings.scheduling.twitter_access_token,
            access_token_secret=settings.scheduling.twitter_access_token_secret
        )
        
        print("🔄 Testing authentication...")
        success = await twitter_api.authenticate()
        
        if success:
            print("✅ Fixed Twitter authentication successful!")
            user_info = await twitter_api.get_user_info()
            if 'data' in user_info:
                username = user_info['data'].get('username', 'unknown')
                print(f"📱 Connected as: @{username}")
        else:
            print("❌ Fixed Twitter authentication still failing")
            print("💡 This might be due to Twitter API permissions or key configuration")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing Twitter auth: {e}")
        import traceback
        traceback.print_exc()
        return False

# Simple test without OAuth for comparison
async def test_simple_twitter():
    """Test with just the bearer token (won't work for user endpoints but shows if keys are valid)"""
    print("\n🧪 Testing Bearer Token Authentication...")
    
    try:
        from config import get_settings
        settings = get_settings()
        
        url = "https://api.twitter.com/2/tweets/search/recent?query=hello&max_results=10"
        headers = {
            "Authorization": f"Bearer {settings.scheduling.twitter_bearer_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    print("✅ Bearer token is valid (can access public endpoints)")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Bearer token test failed: HTTP {response.status}")
                    print(f"Error: {error}")
                    return False
                    
    except Exception as e:
        print(f"❌ Bearer token test error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Twitter Authentication Debug & Test")
    print("=" * 50)
    
    # Run both tests
    asyncio.run(test_simple_twitter())
    asyncio.run(test_twitter_auth_fix())
    
    print("\n💡 Note: Twitter API v2 with free tier has limitations.")
    print("   User authentication might require elevated access.")