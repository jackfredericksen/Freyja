#!/usr/bin/env python3
"""
Freyja - Fixed Dashboard Runner
Starts the web dashboard with proper error handling
"""

import sys
import os
import asyncio
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_startup_banner():
    """Print startup information"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                    FREYJA DASHBOARD                       ║
    ║              AI-Powered Content Management                ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check required packages
    required_packages = [
        "fastapi", "uvicorn", "jinja2", "aiosqlite", 
        "python-multipart", "pydantic", "pydantic-settings"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == "python-multipart":
                import multipart
            elif package == "pydantic-settings":
                import pydantic_settings
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages. Install with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Check directory structure
    required_dirs = [
        "review_system/approval_dashboard/templates",
        "data",
        "logs"
    ]
    
    for directory in required_dirs:
        path = Path(directory)
        if not path.exists():
            print(f"   🔧 Creating directory: {directory}")
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"   ✅ {directory}")
    
    return True

def check_configuration():
    """Check configuration status"""
    print("\n🔧 Checking configuration...")
    
    try:
        from config import get_settings, validate_configuration
        settings = get_settings()
        
        # Validate configuration
        issues = validate_configuration()
        
        if issues:
            print("   ⚠️ Configuration issues found:")
            for issue in issues:
                print(f"      - {issue}")
            print("   💡 Dashboard will still start, but some features may be limited")
        else:
            print("   ✅ Configuration is valid")
        
        # Show API key status
        ai_configured = bool(settings.ai.openai_api_key or settings.ai.anthropic_api_key)
        twitter_configured = bool(
            settings.scheduling.twitter_api_key and 
            settings.scheduling.twitter_api_secret and
            settings.scheduling.twitter_access_token and
            settings.scheduling.twitter_access_token_secret
        )
        
        print(f"   🤖 AI Generation: {'✅ Configured' if ai_configured else '⚠️ Simulation mode'}")
        print(f"   🐦 Twitter Publishing: {'✅ Configured' if twitter_configured else '⚠️ Simulation mode'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        print("   💡 Dashboard will start with default settings")
        return False

async def test_components():
    """Quick test of core components"""
    print("\n🧪 Testing core components...")
    
    try:
        # Test web interface import
        from review_system.approval_dashboard.web_interface import app, ai_generator, twitter_publisher, approval_queue
        print("   ✅ Web interface loaded")
        
        # Test database
        try:
            count = await approval_queue.get_count_by_status("pending")
            print(f"   ✅ Database connected (pending items: {count})")
        except Exception as e:
            print(f"   ⚠️ Database issue: {e}")
        
        # Test AI generator
        status = ai_generator.get_status()
        print(f"   ✅ AI Generator: {status['provider']} mode")
        
        # Test Twitter publisher
        twitter_status = twitter_publisher.get_status()
        print(f"   ✅ Twitter Publisher: {twitter_status['mode']} mode")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return False

def start_dashboard():
    """Start the dashboard server"""
    try:
        import uvicorn
        from review_system.approval_dashboard.web_interface import app
        
        print("\n🚀 Starting Freyja Dashboard...")
        print("=" * 50)
        print("📍 Dashboard URL: http://localhost:8000")
        print("🔍 Review Queue: http://localhost:8000/queue")
        print("📊 Analytics: http://localhost:8000/analytics")
        print("💊 Health Check: http://localhost:8000/health")
        print("=" * 50)
        print("✨ Dashboard Features:")
        print("   • AI Content Generation")
        print("   • Content Review & Approval")
        print("   • Twitter Publishing")
        print("   • Analytics & Insights")
        print("   • Quality Scoring")
        print("=" * 50)
        print("⚠️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload for production-like behavior
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start dashboard: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if port 8000 is available")
        print("2. Verify all dependencies are installed")
        print("3. Run: python main.py --quick")
        return False
    
    return True

def show_help():
    """Show help information"""
    print("""
Freyja Dashboard Runner

Usage:
    python run_dashboard.py              # Start dashboard
    python run_dashboard.py --check      # Check requirements only
    python run_dashboard.py --test       # Test components only
    python run_dashboard.py --help       # Show this help

Environment Setup:
    1. Create .env file with your API keys:
       OPENAI_API_KEY=your_openai_key
       ANTHROPIC_API_KEY=your_anthropic_key
       TWITTER_API_KEY=your_twitter_key
       TWITTER_API_SECRET=your_twitter_secret
       TWITTER_ACCESS_TOKEN=your_access_token
       TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

    2. Install dependencies:
       pip install -r requirements.txt

    3. Start dashboard:
       python run_dashboard.py

Dashboard URLs:
    Main Dashboard: http://localhost:8000
    Review Queue:   http://localhost:8000/queue
    Analytics:      http://localhost:8000/analytics
    Health Check:   http://localhost:8000/health

For more help, visit: https://github.com/jackfredericksen/Freyja
    """)

async def main():
    """Main function"""
    print_startup_banner()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--help":
            show_help()
            return
        elif arg == "--check":
            requirements_ok = check_requirements()
            config_ok = check_configuration()
            if requirements_ok and config_ok:
                print("\n✅ All checks passed! Ready to start dashboard.")
            else:
                print("\n⚠️ Some issues found. Dashboard may have limited functionality.")
            return
        elif arg == "--test":
            requirements_ok = check_requirements()
            if requirements_ok:
                components_ok = await test_components()
                if components_ok:
                    print("\n✅ All components working! Dashboard is ready.")
                else:
                    print("\n⚠️ Some component issues found.")
            return
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            return
    
    # Full startup sequence
    print("Step 1/3: Checking requirements...")
    requirements_ok = check_requirements()
    
    if not requirements_ok:
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return
    
    print("\nStep 2/3: Checking configuration...")
    check_configuration()  # Non-blocking
    
    print("\nStep 3/3: Testing components...")
    components_ok = await test_components()
    
    if not components_ok:
        print("\n⚠️ Some components have issues, but dashboard will still start.")
        print("💡 Check the logs and configuration for details.")
    
    # Start the dashboard
    start_dashboard()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        print("\n🔧 Try running: python main.py --quick")
        sys.exit(1)