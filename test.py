"""
Debug script to test config import
"""

import sys
from pathlib import Path

print("🔍 Debugging Freyja Config Import")
print("=" * 40)

# Show current working directory
print(f"Current directory: {Path.cwd()}")

# Show Python path
print("\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Check if config.py exists
config_file = Path("config.py")
print(f"\nconfig.py exists in root: {config_file.exists()}")
if config_file.exists():
    print(f"config.py size: {config_file.stat().st_size} bytes")

# Check config directory
config_dir = Path("config")
print(f"config/ directory exists: {config_dir.exists()}")
if config_dir.exists():
    config_init = config_dir / "__init__.py"
    print(f"config/__init__.py exists: {config_init.exists()}")
    if config_init.exists():
        print(f"config/__init__.py size: {config_init.stat().st_size} bytes")

# Try to import
print("\n🧪 Testing import...")
try:
    import config
    print(f"✅ Import successful!")
    print(f"Config module location: {config.__file__}")
    
    # Try to get the function
    if hasattr(config, 'get_settings'):
        print("✅ get_settings function found!")
        settings = config.get_settings()
        print(f"✅ Settings loaded: {settings.app_name}")
    else:
        print("❌ get_settings function not found!")
        print(f"Available functions: {[attr for attr in dir(config) if not attr.startswith('_')]}")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("=" * 40)