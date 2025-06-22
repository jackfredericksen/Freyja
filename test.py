#!/usr/bin/env python3
"""Disable the problematic auto-publishing to get dashboard working"""

def disable_auto_publishing():
    """Remove the problematic startup event and background task"""
    
    with open("review_system/approval_dashboard/web_interface.py", "r", encoding='utf-8') as f:
        content = f.read()
    
    # Remove the startup event that's causing issues
    lines = content.split('\n')
    new_lines = []
    skip_lines = False
    
    for line in lines:
        # Skip the problematic auto-publish function and startup event
        if 'async def auto_publish_approved_content():' in line:
            skip_lines = True
            continue
        elif skip_lines and line.startswith('async def ') and 'auto_publish' not in line:
            skip_lines = False
            new_lines.append(line)
        elif skip_lines:
            continue
        elif '@app.on_event("startup")' in line:
            skip_lines = True
            continue
        elif 'async def startup_event():' in line:
            skip_lines = True
            continue
        elif skip_lines and line.startswith('@app.') or (skip_lines and line.startswith('async def ') and 'startup' not in line):
            skip_lines = False
            new_lines.append(line)
        elif not skip_lines:
            new_lines.append(line)
    
    # Write back the cleaned content
    with open("review_system/approval_dashboard/web_interface.py", "w", encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Disabled auto-publishing background task")
    print("✅ Dashboard should start normally now")

if __name__ == "__main__":
    disable_auto_publishing()
    print("\n🔄 Now restart your dashboard:")
    print("python run_dashboard.py")
    print("\n📝 Note: Manual publishing still works!")
    print("   - Approve content normally")
    print("   - Click 'Publish' button to publish manually")