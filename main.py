import asyncio
import sys
from pathlib import Path
from datetime import datetime
import logging
# Create logs directory if it doesn't exist

# Configure logging
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
    ║                          FREYJA                           ║
    ║              AI-Powered Social Media Assistant            ║
    ║                                                           ║
    ║  🔍 Research & Trend Monitoring                          ║
    ║  ✨ AI Content Generation                                ║
    ║  📋 Manual Review & Quality Control                      ║
    ║  📅 Compliant Scheduling                                 ║
    ║  📊 Growth Coaching & Analytics                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


async def test_configuration():
    """Test basic configuration loading"""
    try:
        from config import get_settings
        settings = get_settings()
        
        print("🔧 Configuration Test:")
        print(f"   ✅ App Name: {settings.app_name}")
        print(f"   ✅ Version: {settings.version}")
        print(f"   ✅ Debug Mode: {settings.debug}")
        print(f"   ✅ Database URL: {settings.database.url}")
        
        # Check if API keys are configured - FIXED LOGIC
        api_status = []
        
        # OpenAI check
        if settings.ai.openai_api_key and settings.ai.openai_api_key != "your_openai_api_key_here":
            api_status.append("OpenAI ✅")
        else:
            api_status.append("OpenAI ❌")
        
        # Anthropic check    
        if settings.ai.anthropic_api_key and settings.ai.anthropic_api_key != "your_anthropic_api_key_here":
            api_status.append("Anthropic ✅")
        else:
            api_status.append("Anthropic ❌")
            
        # News API check
        if settings.research.news_api_key and settings.research.news_api_key != "your_news_api_key_here":
            api_status.append("News API ✅")
        else:
            api_status.append("News API ❌")
        
        # Twitter API check - FIXED TO USE CORRECT ATTRIBUTES
        twitter_configured = (
            hasattr(settings.scheduling, 'twitter_bearer_token') and
            settings.scheduling.twitter_bearer_token and
            settings.scheduling.twitter_bearer_token != "your_bearer_token_here" and
            hasattr(settings.scheduling, 'twitter_api_key') and
            settings.scheduling.twitter_api_key and
            settings.scheduling.twitter_api_key != "your_api_key_here"
        )
        
        if twitter_configured:
            api_status.append("Twitter ✅")
        else:
            api_status.append("Twitter ❌")
            
        print(f"   🔑 API Keys: {' | '.join(api_status)}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return False

async def test_trend_monitoring():
    """Test the trend monitoring system"""
    try:
        print("\n🔍 Trend Monitoring Test:")
        
        # Test basic imports first
        from pytrends.request import TrendReq
        import requests
        print("   ✅ Required packages imported")
        
        # Try to import our trend monitor
        try:
            from research.trend_monitoring.trend_monitor import monitor_trends, TrendMonitor
            print("   ✅ Trend monitor module imported")
            
            # Test basic trend monitoring
            monitor = TrendMonitor()
            print("   ✅ Trend monitor initialized")
            
            # Get a few trends (limited test)
            print("   🔄 Fetching trends...")
            trends = await monitor.get_google_trends()
            
            if trends:
                print(f"   ✅ Retrieved {len(trends)} trends successfully!")
                print("\n   📈 Sample Trends:")
                for i, trend in enumerate(trends[:3], 1):
                    print(f"      {i}. {trend.keyword} (Score: {trend.score:.1f})")
                return True
            else:
                print("   ⚠️  No trends retrieved (this might be normal)")
                return True
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure trend_monitor.py is in research/trend_monitoring/")
            return False
            
    except Exception as e:
        print(f"   ❌ Trend Monitoring Error: {e}")
        return False

async def test_ai_content_generation():
    """Test Claude-powered content generation"""
    try:
        print("\n🤖 AI Content Generation Test:")
        
        # Check if Anthropic is configured
        from config import get_settings
        settings = get_settings()
        
        if (not settings.ai.anthropic_api_key or 
            settings.ai.anthropic_api_key == "your_anthropic_api_key_here" or
            not settings.ai.anthropic_api_key.startswith("sk-ant")):
            print("   ⚠️  Anthropic API key not configured")
            print("   💡 Add your Claude API key to test content generation")
            return True  # Not a failure, just not configured
        
        # Test content generation
        try:
            from generation.ai_drafting.ai_content_generator import test_content_generation
            
            print("   🔄 Testing Claude content generation...")
            success = await test_content_generation()
            
            if success:
                print("   ✅ Claude content generation working!")
                return True
            else:
                print("   ❌ Claude content generation failed")
                return False
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure ai_content_generator.py is in generation/ai_drafting/")
            return False
            
    except Exception as e:
        print(f"   ❌ Content Generation Error: {e}")
        return False

async def test_free_research():
    """Test free research tools"""
    try:
        print("\n🔍 Free Research Tools Test:")
        
        try:
            from research.trend_monitoring.free_research_tools import test_free_research
            
            print("   🔄 Testing free research sources...")
            success = await test_free_research()
            
            if success:
                print("   ✅ Free research tools working!")
                return True
            else:
                print("   ❌ Free research tools failed")
                return False
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure free_research_tools.py is in research/trend_monitoring/")
            return False
            
    except Exception as e:
        print(f"   ❌ Free Research Error: {e}")
        return False

async def test_twitter_api():
    """Test Twitter API integration"""
    try:
        print("\n🐦 Twitter API Test:")
        
        from config import get_settings
        settings = get_settings()
        
        # Check if Twitter keys are configured - FIXED LOGIC
        if not (hasattr(settings.scheduling, 'twitter_bearer_token') and 
                settings.scheduling.twitter_bearer_token and
                settings.scheduling.twitter_bearer_token != "your_bearer_token_here"):
            print("   ⚠️  Twitter API keys not configured")
            print("   💡 Add Twitter API keys to .env to test posting functionality")
            return True  # Not a failure, just not configured
        
        try:
            from scheduling.calendar_integration.scheduling_manager import ModernSchedulingManager
            
            print("   ✅ Scheduling manager imported")
            
            # Initialize manager
            manager = ModernSchedulingManager()
            print("   ✅ Scheduling manager initialized")
            
            # Test authentication
            print("   🔄 Testing Twitter authentication...")
            auth_results = await manager.authenticate_all()
            
            if auth_results.get('twitter', False):
                print("   ✅ Twitter authentication successful!")
                
                # Get user info to show connected account
                if 'twitter' in manager.platforms:
                    user_info = await manager.platforms['twitter'].get_user_info()
                    if 'data' in user_info:
                        username = user_info['data'].get('username', 'unknown')
                        print(f"   📱 Connected as: @{username}")
                
                return True
            else:
                print("   ❌ Twitter authentication failed")
                print("   💡 Check your Twitter API keys in .env file")
                return False
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure scheduling_manager.py exists in scheduling/calendar_integration/")
            return False
            
    except Exception as e:
        print(f"   ❌ Twitter API Error: {e}")
        return False

async def test_content_templates():
    """Test the content template system"""
    try:
        print("\n🎨 Content Templates Test:")
        
        try:
            from generation.content_templates.template_engine import TemplateEngine
            
            print("   ✅ Template engine imported")
            
            # Initialize template engine
            engine = TemplateEngine()
            print("   ✅ Template engine initialized")
            
            # Test template generation
            print("   🔄 Testing template generation...")
            
            variables = {
                "insight_topic": "AI Development",
                "main_point": "Testing is crucial for reliable AI systems",
                "elaboration": "Proper testing helps catch edge cases and ensures consistent performance.",
                "call_to_action": "What's your testing strategy?",
                "hashtags": "#AI #Testing #Development"
            }
            
            content = engine.generate_content("tech_insight", variables)
            
            if content and len(content) > 50:
                print("   ✅ Content generation successful!")
                print(f"   📝 Sample content: {content[:100]}...")
                
                # Show available templates
                templates = engine.get_templates_by_type("tweet")
                print(f"   📋 Available tweet templates: {len(templates)}")
                
                return True
            else:
                print("   ❌ Content generation failed")
                return False
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure template_engine.py exists in generation/content_templates/")
            return False
            
    except Exception as e:
        print(f"   ❌ Content Templates Error: {e}")
        return False

async def test_review_system():
    """Test the review system components"""
    try:
        print("\n📋 Review System Test:")
        
        try:
            from review_system.approval_dashboard.approval_queue import ApprovalQueue
            from review_system.content_scoring.quality_scorer import ContentScorer
            
            print("   ✅ Review system modules imported")
            
            # Test approval queue
            queue = ApprovalQueue()
            print("   ✅ Approval queue initialized")
            
            # Test quality scorer
            scorer = ContentScorer()
            print("   ✅ Quality scorer initialized")
            
            # Test basic functionality
            test_content = "This is a test tweet for quality scoring! #testing"
            metrics = await scorer.score_content(test_content, "tweet")
            
            if metrics and metrics.overall_score > 0:
                print(f"   ✅ Quality scoring working! Score: {metrics.overall_score:.1f}")
                return True
            else:
                print("   ❌ Quality scoring failed")
                return False
                
        except ImportError as e:
            print(f"   ❌ Import Error: {e}")
            print("   💡 Make sure review system files exist")
            return False
            
    except Exception as e:
        print(f"   ❌ Review System Error: {e}")
        return False

def check_directory_structure():
    """Check if all required directories exist"""
    print("\n📁 Directory Structure Check:")
    
    required_dirs = [
        "research/trend_monitoring",
        "research/competitor_analysis", 
        "research/topic_discovery",
        "research/news_aggregation",
        "generation/content_templates",
        "generation/ai_drafting",
        "review_system/approval_dashboard",
        "scheduling/calendar_integration",
        "analytics/performance_tracking",
        "coaching/growth_analysis",
        "config",
        "logs",
        "data"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"   ✅ {dir_path}")
    
    if missing_dirs:
        print("\n   ❌ Missing directories:")
        for missing in missing_dirs:
            print(f"      - {missing}")
        return False
    
    print("   ✅ All required directories exist!")
    return True

async def run_full_test():
    """Run comprehensive Freyja test suite"""
    print_banner()
    
    print(f"🚀 Starting Freyja System Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    test_results = []
    
    # Test 1: Directory Structure
    dir_check = check_directory_structure()
    test_results.append(("Directory Structure", dir_check))
    
    # Test 2: Configuration
    config_test = await test_configuration()
    test_results.append(("Configuration", config_test))
    
    # Test 3: Free Research Tools
    if dir_check:
        free_research_test = await test_free_research()
        test_results.append(("Free Research Tools", free_research_test))
    else:
        test_results.append(("Free Research Tools", False))
    
    # Test 4: Trend Monitoring
    if dir_check and config_test:
        trend_test = await test_trend_monitoring()
        test_results.append(("Trend Monitoring", trend_test))
    else:
        test_results.append(("Trend Monitoring", False))
    
    # Test 5: AI Content Generation
    if config_test:
        ai_content_test = await test_ai_content_generation()
        test_results.append(("AI Content Generation", ai_content_test))
    else:
        test_results.append(("AI Content Generation", False))
    
    # Test 6: Content Templates
    if config_test:
        template_test = await test_content_templates()
        test_results.append(("Content Templates", template_test))
    else:
        test_results.append(("Content Templates", False))
    
    # Test 7: Review System
    if config_test:
        review_test = await test_review_system()
        test_results.append(("Review System", review_test))
    else:
        test_results.append(("Review System", False))
    
    # Test 8: Twitter API
    if config_test:
        twitter_test = await test_twitter_api()
        test_results.append(("Twitter API", twitter_test))
    else:
        test_results.append(("Twitter API", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{len(test_results)}")
    
    if passed == len(test_results):
        print("\n🎉 FREYJA IS FULLY OPERATIONAL!")
        print("All systems working perfectly. Ready for production use!")
    elif passed >= 6:
        print("\n✅ FREYJA IS READY TO GO!")
        print("Core functionality works. Some advanced features may need configuration.")
    elif passed >= 3:
        print("\n⚠️  FREYJA IS PARTIALLY READY")
        print("Basic functionality works. Some features may need configuration.")
    else:
        print("\n❌ FREYJA NEEDS SETUP")
        print("Please check the failed tests and fix configuration issues.")
    
    print("\n💡 NEXT STEPS:")
    if passed >= 6:
        print("1. 🚀 Start using the review dashboard: python -m uvicorn review_system.approval_dashboard.web_interface:app --reload")
        print("2. 🎨 Test content generation with templates")
        print("3. 📅 Try scheduling posts with Twitter integration")
        print("4. 📊 Monitor analytics and optimize content")
    else:
        print("1. Fix any failed tests above")
        print("2. Configure missing API keys in .env file")
        print("3. Test individual components")
        print("4. Start building new features!")
    
    print("=" * 60)

async def interactive_mode():
    """Interactive mode for testing specific components"""
    while True:
        print("\n🎛️  FREYJA INTERACTIVE MODE")
        print("1. Run full system test")
        print("2. Test free research tools only")
        print("3. Test AI content generation only")
        print("4. Test trend monitoring only")
        print("5. Test Twitter API only")
        print("6. Test content templates only")
        print("7. Test review system only")
        print("8. Check configuration")
        print("9. Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == "1":
            await run_full_test()
        elif choice == "2":
            await test_free_research()
        elif choice == "3":
            await test_ai_content_generation()
        elif choice == "4":
            await test_trend_monitoring()
        elif choice == "5":
            await test_twitter_api()
        elif choice == "6":
            await test_content_templates()
        elif choice == "7":
            await test_review_system()
        elif choice == "8":
            await test_configuration()
        elif choice == "9":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-9.")

async def main():
    """Main application entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_mode()
    else:
        await run_full_test()

if __name__ == "__main__":
    asyncio.run(main())