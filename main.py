"""
Freyja - AI-Powered Social Media Assistant
Main application entry point and testing hub
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import logging

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
        
        # Check if API keys are configured
        api_status = []
        if settings.ai.openai_api_key:
            api_status.append("OpenAI ✅")
        else:
            api_status.append("OpenAI ❌")
            
        if settings.ai.anthropic_api_key:
            api_status.append("Anthropic ✅")
        else:
            api_status.append("Anthropic ❌")
            
        if settings.research.news_api_key:
            api_status.append("News API ✅")
        else:
            api_status.append("News API ❌")
            
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

async def test_ai_connection():
    """Test AI service connections"""
    try:
        print("\n🤖 AI Services Test:")
        
        from config import get_settings
        settings = get_settings()
        
        # Test OpenAI
        if settings.ai.openai_api_key and settings.ai.openai_api_key != "your_openai_api_key_here":
            try:
                import openai
                client = openai.OpenAI(api_key=settings.ai.openai_api_key)
                
                # Simple test call
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print("   ✅ OpenAI connection successful")
            except Exception as e:
                print(f"   ❌ OpenAI Error: {e}")
        else:
            print("   ⚠️  OpenAI API key not configured")
        
        # Test Anthropic
        if settings.ai.anthropic_api_key and settings.ai.anthropic_api_key != "your_anthropic_api_key_here":
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=settings.ai.anthropic_api_key)
                print("   ✅ Anthropic client initialized")
            except Exception as e:
                print(f"   ❌ Anthropic Error: {e}")
        else:
            print("   ⚠️  Anthropic API key not configured")
            
        return True
        
    except Exception as e:
        print(f"   ❌ AI Services Error: {e}")
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
    
    # Test 3: Trend Monitoring
    if dir_check and config_test:
        trend_test = await test_trend_monitoring()
        test_results.append(("Trend Monitoring", trend_test))
    else:
        test_results.append(("Trend Monitoring", False))
    
    # Test 4: AI Services
    if config_test:
        ai_test = await test_ai_connection()
        test_results.append(("AI Services", ai_test))
    else:
        test_results.append(("AI Services", False))
    
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
        print("\n🎉 FREYJA IS READY TO GO!")
        print("All systems operational. Ready to build amazing features!")
    elif passed >= 2:
        print("\n⚠️  FREYJA IS PARTIALLY READY")
        print("Core functionality works. Some features may need configuration.")
    else:
        print("\n❌ FREYJA NEEDS SETUP")
        print("Please check the failed tests and fix configuration issues.")
    
    print("\n💡 NEXT STEPS:")
    print("1. Fix any failed tests above")
    print("2. Configure API keys in .env file")
    print("3. Test individual components")
    print("4. Start building new features!")
    
    print("=" * 60)

async def interactive_mode():
    """Interactive mode for testing specific components"""
    while True:
        print("\n🎛️  FREYJA INTERACTIVE MODE")
        print("1. Run full system test")
        print("2. Test trend monitoring only")
        print("3. Test AI services only")
        print("4. Check configuration")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            await run_full_test()
        elif choice == "2":
            await test_trend_monitoring()
        elif choice == "3":
            await test_ai_connection()
        elif choice == "4":
            await test_configuration()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")

async def main():
    """Main application entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_mode()
    else:
        await run_full_test()

if __name__ == "__main__":
    asyncio.run(main())