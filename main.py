#!/usr/bin/env python3
"""
Freyja - Fixed Main Testing Script
Tests all components and provides system diagnostics
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import requests
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/freyja.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print Freyja banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                      FREYJA - FIXED                       ║
    ║              AI-Powered Social Media Assistant            ║
    ║                                                           ║
    ║  🔧 All Critical Issues Resolved                         ║
    ║  🔍 Research & Trend Monitoring                          ║
    ║  ✨ AI Content Generation                                ║
    ║  📋 Manual Review & Quality Control                      ║
    ║  📅 Compliant Scheduling                                 ║
    ║  📊 Growth Coaching & Analytics                          ║
    ║  🐦 Twitter Publishing                                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

async def test_configuration():
    """Test configuration loading"""
    try:
        from config import get_settings, validate_configuration
        settings = get_settings()
        
        print("🔧 Configuration Test:")
        print(f"   ✅ App Name: {settings.app_name}")
        print(f"   ✅ Version: {settings.version}")
        print(f"   ✅ Database URL: {settings.database.url}")
        print(f"   ✅ Data Directory: {settings.data_dir}")
        
        # Check API keys with proper validation
        api_status = []
        
        # OpenAI check
        if settings.ai.openai_api_key and settings.ai.openai_api_key.startswith('sk-'):
            api_status.append("OpenAI ✅")
        else:
            api_status.append("OpenAI ❌")
        
        # Anthropic check    
        if settings.ai.anthropic_api_key and settings.ai.anthropic_api_key.startswith('sk-ant'):
            api_status.append("Anthropic ✅")
        else:
            api_status.append("Anthropic ❌")
            
        # News API check
        if settings.research.news_api_key:
            api_status.append("News API ✅")
        else:
            api_status.append("News API ❌")
        
        # Twitter API check
        twitter_keys = [
            settings.scheduling.twitter_api_key,
            settings.scheduling.twitter_api_secret,
            settings.scheduling.twitter_access_token,
            settings.scheduling.twitter_access_token_secret
        ]
        
        if all(twitter_keys):
            api_status.append("Twitter ✅")
        else:
            api_status.append("Twitter ❌")
            
        print(f"   🔑 API Keys: {' | '.join(api_status)}")
        
        # Validate configuration
        issues = validate_configuration()
        if issues:
            print("   ⚠️ Configuration Issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Configuration validation passed")
        
        return True
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return False

async def test_database():
    """Test database functionality"""
    try:
        print("\n💾 Database Test:")
        
        # Import the fixed approval queue
        from review_system.approval_dashboard.web_interface import approval_queue
        
        # Test database creation and basic operations
        test_content = "This is a test tweet for database verification"
        item_id = await approval_queue.add_item(test_content, "tweet", "test")
        print(f"   ✅ Created test item: {item_id}")
        
        # Test retrieval
        item = await approval_queue.get_item(item_id)
        if item and item['content'] == test_content:
            print("   ✅ Item retrieval successful")
        else:
            print("   ❌ Item retrieval failed")
            return False
        
        # Test status counts
        pending_count = await approval_queue.get_count_by_status("pending")
        print(f"   ✅ Pending items count: {pending_count}")
        
        # Test approval workflow
        await approval_queue.approve_item(item_id, "Test approval")
        approved_item = await approval_queue.get_item(item_id)
        if approved_item['status'].value == "approved":
            print("   ✅ Approval workflow works")
        else:
            print("   ❌ Approval workflow failed")
            return False
        
        print("   ✅ Database test completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False

async def test_ai_content_generation():
    """Test AI content generation"""
    try:
        print("\n🤖 AI Content Generation Test:")
        
        # Import the fixed AI generator
        from review_system.approval_dashboard.web_interface import ai_generator
        
        # Test basic tweet generation
        result = await ai_generator.generate_tweet(
            topic="artificial intelligence productivity tools",
            tone="professional",
            include_hashtags=True
        )
        
        if result['success']:
            print(f"   ✅ AI Generation successful ({result['provider']})")
            print(f"   📝 Content: {result['content'][:50]}...")
            print(f"   📊 Characters: {result['character_count']}")
            
            # Test different tones
            casual_result = await ai_generator.generate_tweet(
                topic="coding tips",
                tone="casual",
                include_hashtags=False
            )
            
            if casual_result['success']:
                print(f"   ✅ Multiple tones working")
            else:
                print(f"   ⚠️ Tone variation issues: {casual_result.get('error')}")
            
            return True
        else:
            print(f"   ❌ AI Generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ AI Generation Error: {e}")
        return False

async def test_twitter_integration():
    """Test Twitter integration"""
    try:
        print("\n🐦 Twitter Integration Test:")
        
        # Import the fixed Twitter publisher
        from review_system.approval_dashboard.web_interface import twitter_publisher
        
        # Get status
        status = twitter_publisher.get_status()
        print(f"   📊 Connection Status: {status['mode']}")
        print(f"   🔧 Configured: {status['configured']}")
        
        if status['configured']:
            print(f"   ✅ API Keys Present: {status['credentials_present']}")
        
        # Test tweet publishing (simulation or real)
        test_content = "Test tweet from Freyja system verification 🚀 #testing"
        result = await twitter_publisher.publish_tweet(test_content)
        
        if result['success']:
            print(f"   ✅ Tweet publishing works ({status['mode']})")
            print(f"   🔗 URL: {result['url']}")
            return True
        else:
            print(f"   ❌ Tweet publishing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Twitter Integration Error: {e}")
        return False

async def test_web_dashboard():
    """Test web dashboard endpoints"""
    try:
        print("\n🌐 Web Dashboard Test:")
        
        # Test if we can import the web interface
        from review_system.approval_dashboard.web_interface import app
        print("   ✅ Web interface imports successfully")
        
        # Check if we can start the server programmatically
        import uvicorn
        from multiprocessing import Process
        import time
        
        def start_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="critical")
        
        # Start server in background
        server_process = Process(target=start_server)
        server_process.start()
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        try:
            # Test basic endpoints
            base_url = "http://127.0.0.1:8001"
            
            # Test health endpoint
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
                health_data = response.json()
                print(f"   📊 System Status: {health_data['status']}")
            else:
                print(f"   ⚠️ Health endpoint returned {response.status_code}")
            
            # Test AI status endpoint
            response = requests.get(f"{base_url}/api/ai/status", timeout=5)
            if response.status_code == 200:
                print("   ✅ AI status endpoint working")
            else:
                print(f"   ⚠️ AI status endpoint returned {response.status_code}")
            
            # Test Twitter status endpoint
            response = requests.get(f"{base_url}/api/twitter/status", timeout=5)
            if response.status_code == 200:
                print("   ✅ Twitter status endpoint working")
            else:
                print(f"   ⚠️ Twitter status endpoint returned {response.status_code}")
            
            print("   ✅ Web dashboard test completed")
            success = True
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Dashboard not accessible: {e}")
            success = False
        
        finally:
            # Clean up server process
            server_process.terminate()
            server_process.join()
        
        return success
        
    except Exception as e:
        print(f"   ❌ Web Dashboard Error: {e}")
        return False

async def test_content_workflow():
    """Test complete content workflow"""
    try:
        print("\n🔄 Content Workflow Test:")
        
        from review_system.approval_dashboard.web_interface import approval_queue, ai_generator, twitter_publisher
        
        # Step 1: Generate content
        print("   1️⃣ Generating AI content...")
        ai_result = await ai_generator.generate_tweet(
            topic="productivity automation",
            tone="professional",
            include_hashtags=True
        )
        
        if not ai_result['success']:
            print(f"   ❌ AI generation failed: {ai_result.get('error')}")
            return False
        
        content = ai_result['content']
        print(f"   ✅ Generated: {content[:50]}...")
        
        # Step 2: Submit to review queue
        print("   2️⃣ Submitting to review queue...")
        item_id = await approval_queue.add_item(content, "tweet", "ai_generated")
        print(f"   ✅ Submitted with ID: {item_id}")
        
        # Step 3: Approve content
        print("   3️⃣ Approving content...")
        await approval_queue.approve_item(item_id, "Automated test approval")
        
        # Verify approval
        item = await approval_queue.get_item(item_id)
        if item['status'].value != "approved":
            print("   ❌ Approval failed")
            return False
        print("   ✅ Content approved")
        
        # Step 4: Publish content
        print("   4️⃣ Publishing content...")
        publish_result = await twitter_publisher.publish_tweet(content)
        
        if publish_result['success']:
            print(f"   ✅ Published successfully ({twitter_publisher.get_status()['mode']})")
            print(f"   🔗 URL: {publish_result['url']}")
            
            # Mark as published in database
            await approval_queue.publish_item(item_id, publish_result['url'])
            
            # Verify published status
            final_item = await approval_queue.get_item(item_id)
            if final_item['status'].value == "published":
                print("   ✅ Complete workflow successful")
                return True
            else:
                print("   ⚠️ Status update issue")
                return False
        else:
            print(f"   ❌ Publishing failed: {publish_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Workflow Error: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n🌍 Environment Check:")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"   ⚠️ Python {python_version.major}.{python_version.minor} (3.8+ recommended)")
    
    # Check critical directories
    directories = ["data", "logs", "review_system", "generation", "research"]
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"   ✅ Directory: {directory}")
        else:
            print(f"   ❌ Missing directory: {directory}")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   🔧 Created directory: {directory}")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ Environment file exists")
        
        # Count configured keys
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        configured_keys = []
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()
                if value and value != "your_key_here":
                    configured_keys.append(key)
        
        print(f"   🔑 Configured keys: {len(configured_keys)}")
        if configured_keys:
            print(f"   📋 Keys: {', '.join(configured_keys[:3])}{'...' if len(configured_keys) > 3 else ''}")
    else:
        print("   ⚠️ No .env file found")
        print("   💡 Create .env file with your API keys")
    
    # Check required packages
    required_packages = ["fastapi", "uvicorn", "aiosqlite", "jinja2", "python-multipart"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ Package: {package}")
        except ImportError:
            print(f"   ❌ Missing package: {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"   💡 Install missing packages: pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

async def run_comprehensive_test():
    """Run comprehensive system test"""
    print_banner()
    
    print(f"🚀 Starting Comprehensive Freyja System Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    test_results = {}
    
    # Test 1: Environment Check
    env_check = check_environment()
    test_results["Environment"] = env_check
    
    # Test 2: Configuration
    config_test = await test_configuration()
    test_results["Configuration"] = config_test
    
    # Test 3: Database
    if config_test:
        db_test = await test_database()
        test_results["Database"] = db_test
    else:
        test_results["Database"] = False
    
    # Test 4: AI Content Generation
    if config_test:
        ai_test = await test_ai_content_generation()
        test_results["AI Generation"] = ai_test
    else:
        test_results["AI Generation"] = False
    
    # Test 5: Twitter Integration
    if config_test:
        twitter_test = await test_twitter_integration()
        test_results["Twitter Integration"] = twitter_test
    else:
        test_results["Twitter Integration"] = False
    
    # Test 6: Web Dashboard
    if config_test and env_check:
        dashboard_test = await test_web_dashboard()
        test_results["Web Dashboard"] = dashboard_test
    else:
        test_results["Web Dashboard"] = False
    
    # Test 7: Complete Workflow
    if all([config_test, db_test, ai_test]):
        workflow_test = await test_content_workflow()
        test_results["Complete Workflow"] = workflow_test
    else:
        test_results["Complete Workflow"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{len(test_results)}")
    
    # Status determination
    if passed == len(test_results):
        print("\n🎉 FREYJA IS FULLY OPERATIONAL!")
        print("   All systems working perfectly. Ready for production use!")
        status = "FULLY_OPERATIONAL"
    elif passed >= 5:
        print("\n✅ FREYJA IS READY TO GO!")
        print("   Core functionality works. Some advanced features may need configuration.")
        status = "READY"
    elif passed >= 3:
        print("\n⚠️ FREYJA IS PARTIALLY READY")
        print("   Basic functionality works. Some features need configuration.")
        status = "PARTIAL"
    else:
        print("\n❌ FREYJA NEEDS SETUP")
        print("   Please check the failed tests and fix configuration issues.")
        status = "NEEDS_SETUP"
    
    # Next steps
    print("\n💡 NEXT STEPS:")
    if status == "FULLY_OPERATIONAL":
        print("1. 🚀 Start the dashboard: python run_dashboard.py")
        print("2. 🌐 Open http://localhost:8000 in your browser")
        print("3. 🎨 Generate and publish content")
        print("4. 📊 Monitor analytics and performance")
    elif status in ["READY", "PARTIAL"]:
        print("1. 🔧 Fix any failed tests above")
        print("2. 🔑 Add missing API keys to .env file")
        print("3. 🚀 Start the dashboard: python run_dashboard.py")
        print("4. 🧪 Test individual components")
    else:
        print("1. 📋 Review failed tests above")
        print("2. 🔑 Configure API keys in .env file")
        print("3. 📦 Install missing packages")
        print("4. 🔄 Run this test again")
    
    print("\n🔗 USEFUL COMMANDS:")
    print("   Dashboard:    python run_dashboard.py")
    print("   Health Check: curl http://localhost:8000/health")
    print("   Test Again:   python main.py")
    
    print("=" * 60)
    
    return status

async def quick_test():
    """Quick system test for development"""
    print("⚡ Quick Freyja Test...")
    
    try:
        # Test imports
        from config import get_settings
        from review_system.approval_dashboard.web_interface import app, ai_generator, twitter_publisher
        
        print("✅ All imports successful")
        
        # Test AI generation
        result = await ai_generator.generate_tweet("test topic", "casual", True)
        print(f"✅ AI Generation: {result['success']} ({result['provider']})")
        
        # Test Twitter status
        twitter_status = twitter_publisher.get_status()
        print(f"✅ Twitter Status: {twitter_status['mode']}")
        
        print("⚡ Quick test completed - system appears functional")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

async def interactive_mode():
    """Interactive mode for testing specific components"""
    while True:
        print("\n🎛️ FREYJA INTERACTIVE TEST MODE")
        print("=" * 40)
        print("1. Run comprehensive system test")
        print("2. Test AI content generation only")
        print("3. Test Twitter integration only")
        print("4. Test database operations only")
        print("5. Test web dashboard only")
        print("6. Quick system check")
        print("7. Check environment setup")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        try:
            if choice == "1":
                await run_comprehensive_test()
            elif choice == "2":
                await test_ai_content_generation()
            elif choice == "3":
                await test_twitter_integration()
            elif choice == "4":
                await test_database()
            elif choice == "5":
                await test_web_dashboard()
            elif choice == "6":
                await quick_test()
            elif choice == "7":
                check_environment()
            elif choice == "8":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-8.")
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        except Exception as e:
            print(f"❌ Test error: {e}")

async def main():
    """Main application entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            await interactive_mode()
        elif sys.argv[1] == "--quick":
            await quick_test()
        elif sys.argv[1] == "--env":
            check_environment()
        else:
            print("Usage: python main.py [--interactive|--quick|--env]")
    else:
        await run_comprehensive_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)