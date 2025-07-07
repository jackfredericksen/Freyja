#!/usr/bin/env python3
"""
Twitter App Setup Diagnostic
Helps identify and fix Twitter OAuth setup issues
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_twitter_app_setup():
    """Comprehensive Twitter app setup check"""
    
    print("🐦 Twitter App Setup Diagnostic")
    print("=" * 50)
    
    # Check environment variables
    app_key = os.getenv('TWITTER_APP_KEY')
    app_secret = os.getenv('TWITTER_APP_SECRET')
    
    print("1. Environment Variables:")
    if app_key:
        print(f"   ✅ TWITTER_APP_KEY: {app_key[:10]}...")
    else:
        print("   ❌ TWITTER_APP_KEY: Not found")
    
    if app_secret:
        print(f"   ✅ TWITTER_APP_SECRET: {app_secret[:10]}...")
    else:
        print("   ❌ TWITTER_APP_SECRET: Not found")
    
    if not app_key or not app_secret:
        print("\n❌ Missing Twitter app credentials!")
        print_setup_instructions()
        return False
    
    # Check key format
    print("\n2. Key Format Validation:")
    if len(app_key) >= 20:
        print("   ✅ API Key length looks correct")
    else:
        print("   ❌ API Key seems too short")
    
    if len(app_secret) >= 40:
        print("   ✅ API Secret length looks correct")
    else:
        print("   ❌ API Secret seems too short")
    
    # Test basic Twitter API access
    print("\n3. Twitter API Basic Test:")
    try:
        import tweepy
        
        # Test OAuth handler creation
        auth = tweepy.OAuth1UserHandler(
            consumer_key=app_key,
            consumer_secret=app_secret,
            callback="http://localhost:8000/twitter/callback"
        )
        
        print("   ✅ OAuth handler created successfully")
        
        # Try to get request token (this will fail with 401 if credentials are wrong)
        try:
            request_token_url = auth.get_authorization_url()
            print("   ✅ Authorization URL generated successfully")
            print("   🎉 Your Twitter app credentials are working!")
            return True
            
        except tweepy.Unauthorized:
            print("   ❌ 401 Unauthorized - Invalid app credentials")
            print("   💡 Check your API Key and Secret in Twitter Developer Portal")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
            
    except ImportError:
        print("   ❌ Tweepy not installed: pip install tweepy")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def print_setup_instructions():
    """Print detailed setup instructions"""
    print("\n" + "=" * 50)
    print("🔧 TWITTER APP SETUP INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. Go to Twitter Developer Portal:")
    print("   https://developer.twitter.com/en/portal/dashboard")
    
    print("\n2. Create a new app (or use existing):")
    print("   • Click 'Create App' or select existing app")
    print("   • Give it a name (e.g., 'Freyja Social Media Assistant')")
    
    print("\n3. Configure App Settings:")
    print("   • App Type: Choose any type")
    print("   • Use Case: Describe your use case")
    
    print("\n4. CRITICAL: Set Authentication Settings:")
    print("   • Go to app Settings → Authentication settings")
    print("   • Enable 'OAuth 1.0a'")
    print("   • Set App permissions to 'Read and Write'")
    print("   • Add Callback URL: http://localhost:8000/twitter/callback")
    print("   • Website URL: http://localhost:8000 (or your domain)")
    
    print("\n5. Get Your Keys:")
    print("   • Go to 'Keys and Tokens' tab")
    print("   • Copy 'API Key' (Consumer Key)")
    print("   • Copy 'API Key Secret' (Consumer Secret)")
    
    print("\n6. Add to .env file:")
    print("   TWITTER_APP_KEY=your_api_key_here")
    print("   TWITTER_APP_SECRET=your_api_key_secret_here")
    
    print("\n7. Important Notes:")
    print("   • DON'T use Bearer Token for OAuth")
    print("   • DON'T use Access Token/Secret (those are for your personal account)")
    print("   • DO use API Key and API Key Secret")
    print("   • Make sure OAuth 1.0a is enabled, not just OAuth 2.0")
    
    print("\n💡 Common Issues:")
    print("   • Wrong credentials: Using user tokens instead of app tokens")
    print("   • Missing callback URL in Twitter app settings")
    print("   • OAuth 1.0a not enabled in app settings")
    print("   • Insufficient app permissions (need Read and Write)")

def check_app_permissions():
    """Check if app has correct permissions"""
    print("\n4. App Permissions Check:")
    print("   📋 Your Twitter app should have:")
    print("   • ✅ OAuth 1.0a enabled")
    print("   • ✅ Read and Write permissions")
    print("   • ✅ Callback URL: http://localhost:8000/twitter/callback")
    print("   • ✅ Website URL: http://localhost:8000")
    
    print("\n   🔍 To verify:")
    print("   1. Go to your app in Twitter Developer Portal")
    print("   2. Check 'Settings' → 'Authentication settings'")
    print("   3. Ensure OAuth 1.0a is enabled")
    print("   4. Ensure permissions are 'Read and Write'")

def test_oauth_flow():
    """Test the complete OAuth flow"""
    app_key = os.getenv('TWITTER_APP_KEY')
    app_secret = os.getenv('TWITTER_APP_SECRET')
    
    if not app_key or not app_secret:
        return False
    
    print("\n5. OAuth Flow Test:")
    try:
        import tweepy
        
        # Create auth handler
        auth = tweepy.OAuth1UserHandler(
            consumer_key=app_key,
            consumer_secret=app_secret,
            callback="http://localhost:8000/twitter/callback"
        )
        
        # Get authorization URL
        auth_url = auth.get_authorization_url()
        print(f"   ✅ Authorization URL: {auth_url[:50]}...")
        
        print("\n   🔄 To complete the flow:")
        print("   1. User visits the authorization URL")
        print("   2. User authorizes your app")
        print("   3. Twitter redirects to your callback URL with oauth_verifier")
        print("   4. Your app exchanges verifier for access tokens")
        
        return True
        
    except Exception as e:
        print(f"   ❌ OAuth flow test failed: {e}")
        return False

if __name__ == "__main__":
    success = check_twitter_app_setup()
    
    if success:
        test_oauth_flow()
        check_app_permissions()
        print("\n✅ Twitter app setup looks good!")
        print("🚀 Try the OAuth login in your dashboard")
    else:
        print_setup_instructions()
        print("\n❌ Please fix the issues above and run this script again")