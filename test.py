#!/usr/bin/env python3
"""Fix the duplicate enum issue"""

def fix_content_status_enum():
    """Fix the ContentStatus enum by removing duplicates"""
    
    # Read the current file
    with open("review_system/approval_dashboard/approval_queue.py", "r", encoding='utf-8') as f:
        content = f.read()
    
    # Replace the duplicated enum with the correct one
    old_enum_pattern = '''class ContentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"'''
    
    correct_enum = '''class ContentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"'''
    
    # Find and replace any duplicate entries
    lines = content.split('\n')
    in_enum = False
    new_lines = []
    seen_enum_values = set()
    
    for line in lines:
        if 'class ContentStatus(Enum):' in line:
            in_enum = True
            new_lines.append(line)
            seen_enum_values.clear()
        elif in_enum and line.strip().startswith(('PENDING', 'APPROVED', 'REJECTED', 'EDITED', 'SCHEDULED', 'PUBLISHED')):
            # Extract the enum value name
            enum_name = line.strip().split('=')[0].strip()
            if enum_name not in seen_enum_values:
                new_lines.append(line)
                seen_enum_values.add(enum_name)
            # Skip duplicates
        elif in_enum and (line.strip() == '' or not line.startswith('    ')):
            in_enum = False
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Write the fixed content
    with open("review_system/approval_dashboard/approval_queue.py", "w", encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Fixed ContentStatus enum duplicates")

if __name__ == "__main__":
    fix_content_status_enum()
    print("Fixed! Try running your dashboard again:")
    print("python run_dashboard.py")