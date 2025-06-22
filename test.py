#!/usr/bin/env python3
"""Fix OAuth import issues"""

import os

def fix_oauth_imports():
    """Fix common OAuth import issues"""
    
    # 1. Ensure publishing directory has __init__.py
    os.makedirs("publishing", exist_ok=True)
    with open("publishing/__init__.py", "w") as f:
        f.write("")
    
    # 2. Add OAuth import to web interface
    web_interface_path = "review_system/approval_dashboard/web_interface.py"
    
    if os.path.exists(web_interface_path):
        with open(web_interface_path, "r") as f:
            content = f.read()
        
        # Check if OAuth import already exists
        if "twitter_oauth_publisher" not in content:
            # Add import after existing imports
            import_line = """
# Import OAuth publisher
try:
    import sys
    sys.path.append('.')
    from publishing.twitter_oauth_publisher import twitter_oauth_publisher
    print("✅ OAuth publisher imported successfully")
except ImportError as e:
    print(f"❌ OAuth import error: {e}")
    twitter_oauth_publisher = None
except Exception as e:
    print(f"❌ OAuth initialization error: {e}")
    twitter_oauth_publisher = None
"""
            
            # Find a good place to insert the import
            lines = content.split('\n')
            insert_index = -1
            
            for i, line in enumerate(lines):
                if 'from config import get_settings' in line:
                    insert_index = i + 1
                    break
            
            if insert_index != -1:
                lines.insert(insert_index, import_line)
                
                with open(web_interface_path, "w") as f:
                    f.write('\n'.join(lines))
                
                print("✅ Added OAuth import to web interface")
            else:
                print("❌ Could not find insertion point in web interface")
        else:
            print("✅ OAuth import already exists")
    else:
        print("❌ Web interface file not found")

if __name__ == "__main__":
    fix_oauth_imports()