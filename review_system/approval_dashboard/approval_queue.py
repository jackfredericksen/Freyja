"""
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
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

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
    

    async def get_pending_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all pending approval items"""
        return await self._get_items_by_status(ContentStatus.PENDING, limit)
    
    async def get_approved_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all approved items"""
        return await self._get_items_by_status(ContentStatus.APPROVED, limit)
    
    async def get_rejected_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all rejected items"""
        return await self._get_items_by_status(ContentStatus.REJECTED, limit)
    
    async def get_all_items(self, limit: int = 100) -> List[ContentItem]:
        """Get all items regardless of status"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM content_items ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_content_item(row) for row in rows]
    
    async def _get_items_by_status(self, status: ContentStatus, limit: int) -> List[ContentItem]:
        """Helper method to get items by status"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM content_items 
                WHERE status = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (status.value, limit)) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_content_item(row) for row in rows]


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
