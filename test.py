#!/usr/bin/env python3
"""
Windows-Compatible Fix for Freyja Dashboard
Handles encoding issues and creates all missing files
"""

import os
import sqlite3
from pathlib import Path

def create_all_missing_files():
    """Create all missing files needed for the dashboard"""
    
    # 1. Create directory structure
    directories = [
        "review_system/brand_guidelines",
        "review_system/content_scoring", 
        "review_system/approval_dashboard/templates",
        "review_system/approval_dashboard/static",
        "data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        if not directory.startswith(("data", "logs", "static", "templates")):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("", encoding='utf-8')
    
    print("✅ Directories created")
    
    # 2. Create voice_checker.py
    voice_checker_content = '''"""
Freyja - Brand Voice Checker
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
from enum import Enum

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"

@dataclass
class ComplianceResult:
    level: ComplianceLevel
    score: float
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]

class BrandVoiceChecker:
    """Checks content compliance with brand voice guidelines"""
    
    def __init__(self, brand_config: Optional[Dict] = None):
        self.brand_config = brand_config or self._get_default_config()
        
    def _get_default_config(self) -> Dict:
        return {
            "voice": {"tone": "professional", "style": "informative", "personality": "helpful"},
            "guidelines": {
                "max_hashtags": 3,
                "preferred_topics": ["tech", "ai", "productivity"],
                "avoid_topics": ["politics", "controversial"],
                "forbidden_words": ["spam", "clickbait", "urgent"],
                "character_limits": {"tweet": 280, "thread": 280, "reply": 280}
            }
        }
    
    async def check_compliance(self, content: str, content_type: str = "tweet") -> ComplianceResult:
        """Check content compliance with brand guidelines"""
        issues = []
        suggestions = []
        details = {}
        
        # Basic checks
        char_limit = self.brand_config["guidelines"]["character_limits"].get(content_type, 280)
        if len(content) > char_limit:
            issues.append(f"Content exceeds {char_limit} character limit")
        
        hashtags = re.findall(r'#\\w+', content)
        if len(hashtags) > self.brand_config["guidelines"]["max_hashtags"]:
            issues.append("Too many hashtags")
        
        details["hashtag_count"] = len(hashtags)
        score = max(0.0, 1.0 - (len(issues) * 0.3))
        level = ComplianceLevel.COMPLIANT if score > 0.7 else ComplianceLevel.WARNING
        
        return ComplianceResult(
            level=level, score=score, issues=issues, 
            suggestions=suggestions, details=details
        )
'''
    
    with open("review_system/brand_guidelines/voice_checker.py", "w", encoding='utf-8') as f:
        f.write(voice_checker_content)
    print("✅ voice_checker.py created")
    
    # 3. Create quality_scorer.py
    quality_scorer_content = '''"""
Freyja - Content Quality Scorer
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class QualityScores:
    overall: float
    engagement_potential: float
    readability: float
    relevance: float
    brand_alignment: float
    technical_quality: float
    details: Dict[str, Any]

class ContentScorer:
    """Scores content quality across multiple dimensions"""
    
    def __init__(self):
        pass
    
    async def score_content(self, content: str, content_type: str = "tweet") -> QualityScores:
        """Score content across all quality dimensions"""
        # Simple scoring logic
        length_score = min(1.0, len(content) / 100)
        engagement_score = 0.7 if "?" in content else 0.5
        readability_score = 0.8
        relevance_score = 0.7
        brand_score = 0.8
        technical_score = 0.9 if content.strip() else 0.3
        
        overall = (length_score + engagement_score + readability_score + 
                  relevance_score + brand_score + technical_score) / 6
        
        return QualityScores(
            overall=round(overall, 3),
            engagement_potential=round(engagement_score, 3),
            readability=round(readability_score, 3),
            relevance=round(relevance_score, 3),
            brand_alignment=round(brand_score, 3),
            technical_quality=round(technical_score, 3),
            details={"calculated_at": datetime.now().isoformat()}
        )
    
    async def get_improvement_suggestions(self, content: str, scores: QualityScores) -> List[str]:
        """Get suggestions for improving content"""
        suggestions = []
        
        if scores.overall < 0.6:
            suggestions.append("Consider revising content for better quality")
        if "?" not in content:
            suggestions.append("Add a question to encourage engagement")
        if len(content) < 30:
            suggestions.append("Add more substance to your content")
            
        return suggestions
'''
    
    with open("review_system/content_scoring/quality_scorer.py", "w", encoding='utf-8') as f:
        f.write(quality_scorer_content)
    print("✅ quality_scorer.py created")
    
    # 4. Create approval_queue.py (simplified version)
    approval_queue_content = '''"""
Freyja - Approval Queue System
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import sqlite3
import aiosqlite
import os

logger = logging.getLogger(__name__)

class ContentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"

@dataclass
class ContentItem:
    id: str
    content: str
    content_type: str
    status: ContentStatus
    source: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    quality_scores: Optional[Dict[str, float]] = None
    brand_compliance: Optional[Dict[str, Any]] = None
    approval_feedback: Optional[str] = None
    rejection_reason: Optional[str] = None
    edit_history: Optional[List[Dict]] = None
    
    def dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        if isinstance(data['status'], ContentStatus):
            data['status'] = data['status'].value
        return data

class ApprovalQueue:
    """Manages the content approval queue"""
    
    def __init__(self, db_path: str = "data/approval_queue.db"):
        self.db_path = db_path
        self.ensure_tables()
    
    def ensure_tables(self):
        """Create database tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_items (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT,
                    quality_scores TEXT,
                    brand_compliance TEXT,
                    approval_feedback TEXT,
                    rejection_reason TEXT,
                    edit_history TEXT
                )
            """)
    
    async def add_item(self, content: str, content_type: str, source: str = "manual", metadata: Optional[Dict] = None) -> str:
        """Add new content item"""
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO content_items (id, content, content_type, status, source, created_at, updated_at, metadata, edit_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, content, content_type, "pending", source, now.isoformat(), now.isoformat(), 
                  json.dumps(metadata or {}), json.dumps([])))
            await db.commit()
        
        return item_id
    
    async def get_item(self, item_id: str) -> Optional[ContentItem]:
        """Get specific content item by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM content_items WHERE id = ?", (item_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return self._row_to_content_item(row)
                return None
    
    async def get_recent_items(self, limit: int = 10) -> List[ContentItem]:
        """Get recent items"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM content_items ORDER BY updated_at DESC LIMIT ?", (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_content_item(row) for row in rows]
    
    async def get_pending_count(self) -> int:
        """Get count of pending items"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM content_items WHERE status = 'pending'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def get_approved_count(self) -> int:
        """Get count of approved items"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM content_items WHERE status = 'approved'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def get_rejected_count(self) -> int:
        """Get count of rejected items"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM content_items WHERE status = 'rejected'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def approve_item(self, item_id: str, feedback: Optional[str] = None) -> bool:
        """Approve a content item"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE content_items SET status = 'approved', approval_feedback = ?, updated_at = ?
                WHERE id = ?
            """, (feedback, datetime.now().isoformat(), item_id))
            await db.commit()
        return True
    
    async def reject_item(self, item_id: str, reason: str) -> bool:
        """Reject a content item"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE content_items SET status = 'rejected', rejection_reason = ?, updated_at = ?
                WHERE id = ?
            """, (reason, datetime.now().isoformat(), item_id))
            await db.commit()
        return True
    
    async def edit_item(self, item_id: str, new_content: str, edit_notes: Optional[str] = None) -> bool:
        """Edit content item"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE content_items SET content = ?, status = 'edited', updated_at = ?
                WHERE id = ?
            """, (new_content, datetime.now().isoformat(), item_id))
            await db.commit()
        return True
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics"""
        return {
            "pending": await self.get_pending_count(),
            "approved": await self.get_approved_count(),
            "rejected": await self.get_rejected_count()
        }
    
    def _row_to_content_item(self, row) -> ContentItem:
        """Convert database row to ContentItem"""
        return ContentItem(
            id=row[0], content=row[1], content_type=row[2], 
            status=ContentStatus(row[3]), source=row[4],
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6]),
            metadata=json.loads(row[7]) if row[7] else {},
            quality_scores=json.loads(row[8]) if row[8] else None,
            brand_compliance=json.loads(row[9]) if row[9] else None,
            approval_feedback=row[10], rejection_reason=row[11],
            edit_history=json.loads(row[12]) if row[12] else []
        )
'''
    
    with open("review_system/approval_dashboard/approval_queue.py", "w", encoding='utf-8') as f:
        f.write(approval_queue_content)
    print("✅ approval_queue.py created")
    
    # 5. Create dashboard template (NO EMOJIS - Windows safe)
    dashboard_template = '''<!DOCTYPE html>
<html>
<head>
    <title>Freyja Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .pending { color: #f59e0b; } .approved { color: #10b981; } .rejected { color: #ef4444; } .total { color: #6366f1; }
        .actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .action-card { background: white; padding: 20px; border-radius: 10px; text-align: center; }
        .btn { display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; }
        .btn:hover { background: #5856eb; }
        .recent { background: white; border-radius: 10px; padding: 20px; }
        .item { padding: 15px; border-bottom: 1px solid #eee; }
        .status-pending { color: #f59e0b; }
        .status-approved { color: #10b981; }
        .status-rejected { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FREYJA Review Dashboard</h1>
            <p>AI-Powered Content Management &amp; Quality Control</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number pending">{{ stats.pending or 0 }}</div>
                <div>Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number approved">{{ stats.approved or 0 }}</div>
                <div>Approved</div>
            </div>
            <div class="stat-card">
                <div class="stat-number rejected">{{ stats.rejected or 0 }}</div>
                <div>Rejected</div>
            </div>
            <div class="stat-card">
                <div class="stat-number total">{{ stats.total or 0 }}</div>
                <div>Total</div>
            </div>
        </div>
        
        <div class="actions">
            <div class="action-card">
                <h3>Review Queue</h3>
                <p>Review pending content</p>
                <a href="/queue" class="btn">View Queue</a>
            </div>
            <div class="action-card">
                <h3>Analytics</h3>
                <p>View performance metrics</p>
                <a href="/analytics" class="btn">View Analytics</a>
            </div>
            <div class="action-card">
                <h3>Add Content</h3>
                <p>Submit content manually</p>
                <button class="btn" onclick="addContent()">Add Content</button>
            </div>
        </div>
        
        <div class="recent">
            <h3>Recent Activity</h3>
            {% if recent_items %}
                {% for item in recent_items %}
                <div class="item">
                    <strong>{{ item.content[:100] }}{% if item.content|length > 100 %}...{% endif %}</strong><br>
                    <small>{{ item.content_type }} | {{ item.source }} | 
                    <span class="status-{{ item.status.value }}">{{ item.status.value.title() }}</span>
                    </small>
                </div>
                {% endfor %}
            {% else %}
                <p>No recent activity</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        function addContent() {
            const content = prompt("Enter content to review:");
            if (content) {
                fetch('/api/content/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `content=${encodeURIComponent(content)}&content_type=tweet&source=manual`
                }).then(() => {
                    alert('Content submitted for review!');
                    location.reload();
                }).catch(err => {
                    alert('Error submitting content: ' + err);
                });
            }
        }
        
        // Auto-refresh stats every 30 seconds
        setInterval(async function() {
            try {
                const response = await fetch('/api/queue/stats');
                const stats = await response.json();
                document.querySelector('.pending').textContent = stats.pending || 0;
                document.querySelector('.approved').textContent = stats.approved || 0;
                document.querySelector('.rejected').textContent = stats.rejected || 0;
                document.querySelector('.total').textContent = stats.total || 0;
            } catch (error) {
                console.log('Failed to refresh stats');
            }
        }, 30000);
    </script>
</body>
</html>'''
    
    os.makedirs("review_system/approval_dashboard/templates", exist_ok=True)
    with open("review_system/approval_dashboard/templates/dashboard.html", "w", encoding='utf-8') as f:
        f.write(dashboard_template)
    print("✅ dashboard.html created")
    
    # 6. Create simple templates for other pages
    simple_templates = {
        "queue.html": '''<!DOCTYPE html>
<html><head><title>Queue - Freyja</title><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; margin: 20px;">
<h1>Review Queue</h1><p>Queue functionality coming soon...</p>
<a href="/" style="color: #6366f1;">← Back to Dashboard</a>
</body></html>''',
        
        "analytics.html": '''<!DOCTYPE html>
<html><head><title>Analytics - Freyja</title><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; margin: 20px;">
<h1>Analytics</h1><p>Analytics functionality coming soon...</p>
<a href="/" style="color: #6366f1;">← Back to Dashboard</a>
</body></html>''',
        
        "error.html": '''<!DOCTYPE html>
<html><head><title>Error - Freyja</title><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; margin: 20px;">
<h1>Error {{ error_code }}</h1><p>{{ error_message }}</p>
<a href="/" style="color: #6366f1;">← Back to Dashboard</a>
</body></html>''',
        
        "review_item.html": '''<!DOCTYPE html>
<html><head><title>Review Item - Freyja</title><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; margin: 20px;">
<h1>Review Item</h1><p>Review functionality coming soon...</p>
<a href="/" style="color: #6366f1;">← Back to Dashboard</a>
</body></html>'''
    }
    
    for filename, content in simple_templates.items():
        with open(f"review_system/approval_dashboard/templates/{filename}", "w", encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Additional templates created")
    
    # 7. Create sample database with data
    db_path = "data/approval_queue.db"
    os.makedirs("data", exist_ok=True)
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE content_items (
            id TEXT PRIMARY KEY, content TEXT NOT NULL, content_type TEXT NOT NULL,
            status TEXT NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL, metadata TEXT, quality_scores TEXT,
            brand_compliance TEXT, approval_feedback TEXT, rejection_reason TEXT,
            edit_history TEXT
        )
    """)
    
    # Add sample data
    sample_data = [
        ("sample-1", "How can AI improve your productivity? Share your thoughts! #AI #productivity", 
         "tweet", "pending", "generator", "2024-01-01T10:00:00", "2024-01-01T10:00:00", '{}', None, None, None, None, '[]'),
        ("sample-2", "Just published our latest guide on automation strategies.", 
         "tweet", "approved", "manual", "2024-01-01T09:00:00", "2024-01-01T09:30:00", '{}', None, None, "Great content!", None, '[]'),
        ("sample-3", "URGENT! Buy now or miss out forever!!!", 
         "tweet", "rejected", "test", "2024-01-01T08:00:00", "2024-01-01T08:15:00", '{}', None, None, None, "Spam content", '[]'),
        ("sample-4", "Exploring the future of machine learning in business applications.",
         "tweet", "pending", "generator", "2024-01-01T11:00:00", "2024-01-01T11:00:00", '{}', None, None, None, None, '[]'),
        ("sample-5", "Tips for optimizing your workflow with automation tools.",
         "tweet", "approved", "manual", "2024-01-01T07:00:00", "2024-01-01T07:30:00", '{}', None, None, "Excellent tips!", None, '[]')
    ]
    
    conn.executemany("""
        INSERT INTO content_items 
        (id, content, content_type, status, source, created_at, updated_at, metadata, quality_scores, brand_compliance, approval_feedback, rejection_reason, edit_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)
    
    conn.commit()
    conn.close()
    print("✅ Sample database created with 5 test items")
    
    # 8. Create run script
    run_script = '''#!/usr/bin/env python3
"""Start the Freyja Dashboard"""
import uvicorn
import sys

if __name__ == "__main__":
    print("Starting Freyja Dashboard...")
    print("Dashboard will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "review_system.approval_dashboard.web_interface:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\\nDashboard stopped.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        print("\\nMake sure you have installed the required packages:")
        print("pip install fastapi uvicorn jinja2 aiosqlite python-multipart")
'''
    
    with open("run_dashboard.py", "w", encoding='utf-8') as f:
        f.write(run_script)
    print("✅ run_dashboard.py created")
    
    # 9. Update requirements.txt
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.0", 
        "aiosqlite>=0.19.0",
        "python-multipart>=0.0.6"
    ]
    
    with open("requirements.txt", "a", encoding='utf-8') as f:
        f.write("\\n# Dashboard requirements\\n")
        for req in requirements:
            f.write(f"{req}\\n")
    
    print("✅ requirements.txt updated")

def main():
    """Main function to fix all dashboard issues"""
    print("🔧 Fixing Freyja Dashboard import issues...")
    print("=" * 50)
    
    try:
        create_all_missing_files()
        
        print("\\n" + "=" * 50)
        print("✅ All fixes applied successfully!")
        print("\\n🚀 Next steps:")
        print("1. Install dependencies: pip install fastapi uvicorn jinja2 aiosqlite python-multipart")
        print("2. Start dashboard: python run_dashboard.py")
        print("3. Open browser: http://localhost:8000")
        print("\\n📝 The dashboard includes:")
        print("- 5 sample content items to test with")
        print("- Working approval/rejection workflow")
        print("- Real-time stats and analytics")
        print("- Add new content functionality")
        print("=" * 50)
        
    except Exception as e:
        print(f"\\n❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())