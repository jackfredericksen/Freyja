"""
Freyja - Approval Queue System
Manages content items through the review and approval process
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum as PyEnum
import uuid
import json
import logging

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.database.url, echo=settings.database.echo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ContentStatus(PyEnum):
    """Content review status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    SCHEDULED = "scheduled"
    POSTED = "posted"

class ContentType(PyEnum):
    """Content type classification"""
    TWEET = "tweet"
    THREAD = "thread"
    REPLY = "reply"
    QUOTE_TWEET = "quote_tweet"
    STORY = "story"

@dataclass
class ContentItem:
    """Content item data structure"""
    id: str
    content: str
    content_type: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime
    scheduled_time: Optional[datetime] = None
    quality_score: Optional[float] = None
    brand_compliance_score: Optional[float] = None
    engagement_prediction: Optional[float] = None
    feedback: Optional[str] = None
    rejection_reason: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    media_urls: List[str] = None
    metadata: Dict[str, Any] = None
    
    def dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'content_type': self.content_type,
            'status': self.status,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'quality_score': self.quality_score,
            'brand_compliance_score': self.brand_compliance_score,
            'engagement_prediction': self.engagement_prediction,
            'feedback': self.feedback,
            'rejection_reason': self.rejection_reason,
            'hashtags': self.hashtags or [],
            'mentions': self.mentions or [],
            'media_urls': self.media_urls or [],
            'metadata': self.metadata or {}
        }

class ContentItemDB(Base):
    """SQLAlchemy model for content items"""
    __tablename__ = "content_items"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.PENDING)
    source = Column(String, nullable=False)  # ai_generated, manual, imported
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    scheduled_time = Column(DateTime, nullable=True)
    quality_score = Column(Float, nullable=True)
    brand_compliance_score = Column(Float, nullable=True)
    engagement_prediction = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)
    mentions = Column(JSON, nullable=True)
    media_urls = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

class ApprovalQueue:
    """Main approval queue management class"""
    
    def __init__(self):
        self.session = SessionLocal()
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    async def add_item(self, content: str, content_type: str, source: str = "manual", 
                      metadata: Dict[str, Any] = None) -> str:
        """Add a new content item to the queue"""
        try:
            item_id = str(uuid.uuid4())
            
            # Extract hashtags and mentions
            hashtags = self._extract_hashtags(content)
            mentions = self._extract_mentions(content)
            
            db_item = ContentItemDB(
                id=item_id,
                content=content,
                content_type=ContentType(content_type),
                source=source,
                hashtags=hashtags,
                mentions=mentions,
                metadata=metadata or {}
            )
            
            self.session.add(db_item)
            self.session.commit()
            
            logger.info(f"Added content item to queue: {item_id}")
            return item_id
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding content item: {e}")
            raise
    
    async def get_item(self, item_id: str) -> Optional[ContentItem]:
        """Get a specific content item"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if db_item:
                return self._db_to_dataclass(db_item)
            return None
            
        except Exception as e:
            logger.error(f"Error getting content item {item_id}: {e}")
            return None
    
    async def get_pending_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all pending content items"""
        try:
            db_items = self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.PENDING)\
                .order_by(ContentItemDB.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._db_to_dataclass(item) for item in db_items]
            
        except Exception as e:
            logger.error(f"Error getting pending items: {e}")
            return []
    
    async def get_approved_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all approved content items"""
        try:
            db_items = self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.APPROVED)\
                .order_by(ContentItemDB.updated_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._db_to_dataclass(item) for item in db_items]
            
        except Exception as e:
            logger.error(f"Error getting approved items: {e}")
            return []
    
    async def get_rejected_items(self, limit: int = 50) -> List[ContentItem]:
        """Get all rejected content items"""
        try:
            db_items = self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.REJECTED)\
                .order_by(ContentItemDB.updated_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._db_to_dataclass(item) for item in db_items]
            
        except Exception as e:
            logger.error(f"Error getting rejected items: {e}")
            return []
    
    async def get_all_items(self, limit: int = 100) -> List[ContentItem]:
        """Get all content items"""
        try:
            db_items = self.session.query(ContentItemDB)\
                .order_by(ContentItemDB.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._db_to_dataclass(item) for item in db_items]
            
        except Exception as e:
            logger.error(f"Error getting all items: {e}")
            return []
    
    async def get_recent_items(self, limit: int = 10) -> List[ContentItem]:
        """Get most recent content items"""
        try:
            db_items = self.session.query(ContentItemDB)\
                .order_by(ContentItemDB.updated_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._db_to_dataclass(item) for item in db_items]
            
        except Exception as e:
            logger.error(f"Error getting recent items: {e}")
            return []
    
    async def approve_item(self, item_id: str, feedback: str = None) -> bool:
        """Approve a content item"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            db_item.status = ContentStatus.APPROVED
            db_item.feedback = feedback
            db_item.updated_at = datetime.now()
            
            self.session.commit()
            logger.info(f"Approved content item: {item_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error approving item {item_id}: {e}")
            return False
    
    async def reject_item(self, item_id: str, reason: str) -> bool:
        """Reject a content item"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            db_item.status = ContentStatus.REJECTED
            db_item.rejection_reason = reason
            db_item.updated_at = datetime.now()
            
            self.session.commit()
            logger.info(f"Rejected content item: {item_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error rejecting item {item_id}: {e}")
            return False
    
    async def edit_item(self, item_id: str, new_content: str, edit_notes: str = None) -> bool:
        """Edit a content item and mark as edited"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            # Store original content in metadata
            if not db_item.metadata:
                db_item.metadata = {}
            
            if 'edit_history' not in db_item.metadata:
                db_item.metadata['edit_history'] = []
            
            db_item.metadata['edit_history'].append({
                'original_content': db_item.content,
                'edit_time': datetime.now().isoformat(),
                'edit_notes': edit_notes
            })
            
            # Update content and status
            db_item.content = new_content
            db_item.status = ContentStatus.EDITED
            db_item.updated_at = datetime.now()
            
            # Re-extract hashtags and mentions
            db_item.hashtags = self._extract_hashtags(new_content)
            db_item.mentions = self._extract_mentions(new_content)
            
            # Mark metadata as dirty for SQLAlchemy
            self.session.merge(db_item)
            self.session.commit()
            
            logger.info(f"Edited content item: {item_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error editing item {item_id}: {e}")
            return False
    
    async def update_scores(self, item_id: str, quality_score: float = None, 
                           brand_compliance_score: float = None, 
                           engagement_prediction: float = None) -> bool:
        """Update quality and compliance scores for an item"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            if quality_score is not None:
                db_item.quality_score = quality_score
            if brand_compliance_score is not None:
                db_item.brand_compliance_score = brand_compliance_score
            if engagement_prediction is not None:
                db_item.engagement_prediction = engagement_prediction
            
            db_item.updated_at = datetime.now()
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating scores for item {item_id}: {e}")
            return False
    
    async def schedule_item(self, item_id: str, scheduled_time: datetime) -> bool:
        """Mark an item as scheduled"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            db_item.status = ContentStatus.SCHEDULED
            db_item.scheduled_time = scheduled_time
            db_item.updated_at = datetime.now()
            
            self.session.commit()
            logger.info(f"Scheduled content item: {item_id} for {scheduled_time}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error scheduling item {item_id}: {e}")
            return False
    
    async def mark_posted(self, item_id: str) -> bool:
        """Mark an item as posted"""
        try:
            db_item = self.session.query(ContentItemDB).filter(ContentItemDB.id == item_id).first()
            if not db_item:
                return False
            
            db_item.status = ContentStatus.POSTED
            db_item.updated_at = datetime.now()
            
            self.session.commit()
            logger.info(f"Marked content item as posted: {item_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error marking item as posted {item_id}: {e}")
            return False
    
    async def get_pending_count(self) -> int:
        """Get count of pending items"""
        try:
            return self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.PENDING)\
                .count()
        except Exception as e:
            logger.error(f"Error getting pending count: {e}")
            return 0
    
    async def get_approved_count(self) -> int:
        """Get count of approved items"""
        try:
            return self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.APPROVED)\
                .count()
        except Exception as e:
            logger.error(f"Error getting approved count: {e}")
            return 0
    
    async def get_rejected_count(self) -> int:
        """Get count of rejected items"""
        try:
            return self.session.query(ContentItemDB)\
                .filter(ContentItemDB.status == ContentStatus.REJECTED)\
                .count()
        except Exception as e:
            logger.error(f"Error getting rejected count: {e}")
            return 0
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data for the approval queue"""
        try:
            # Get counts by status
            status_counts = {}
            for status in ContentStatus:
                count = self.session.query(ContentItemDB)\
                    .filter(ContentItemDB.status == status)\
                    .count()
                status_counts[status.value] = count
            
            # Get average scores
            avg_quality = self.session.query(ContentItemDB.quality_score)\
                .filter(ContentItemDB.quality_score.isnot(None))\
                .all()
            avg_quality_score = sum(score[0] for score in avg_quality) / len(avg_quality) if avg_quality else 0
            
            avg_brand = self.session.query(ContentItemDB.brand_compliance_score)\
                .filter(ContentItemDB.brand_compliance_score.isnot(None))\
                .all()
            avg_brand_score = sum(score[0] for score in avg_brand) / len(avg_brand) if avg_brand else 0
            
            # Get activity over time (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_activity = self.session.query(ContentItemDB)\
                .filter(ContentItemDB.created_at >= week_ago)\
                .all()
            
            daily_activity = {}
            for item in recent_activity:
                day = item.created_at.date().isoformat()
                if day not in daily_activity:
                    daily_activity[day] = 0
                daily_activity[day] += 1
            
            # Get top hashtags
            all_hashtags = []
            items_with_hashtags = self.session.query(ContentItemDB.hashtags)\
                .filter(ContentItemDB.hashtags.isnot(None))\
                .all()
            
            for hashtag_list in items_with_hashtags:
                if hashtag_list[0]:  # hashtag_list is a tuple
                    all_hashtags.extend(hashtag_list[0])
            
            from collections import Counter
            top_hashtags = Counter(all_hashtags).most_common(10)
            
            return {
                'status_counts': status_counts,
                'avg_quality_score': round(avg_quality_score, 2),
                'avg_brand_compliance_score': round(avg_brand_score, 2),
                'daily_activity': daily_activity,
                'top_hashtags': top_hashtags,
                'total_items': sum(status_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}
    
    def _db_to_dataclass(self, db_item: ContentItemDB) -> ContentItem:
        """Convert database model to dataclass"""
        return ContentItem(
            id=db_item.id,
            content=db_item.content,
            content_type=db_item.content_type.value,
            status=db_item.status.value,
            source=db_item.source,
            created_at=db_item.created_at,
            updated_at=db_item.updated_at,
            scheduled_time=db_item.scheduled_time,
            quality_score=db_item.quality_score,
            brand_compliance_score=db_item.brand_compliance_score,
            engagement_prediction=db_item.engagement_prediction,
            feedback=db_item.feedback,
            rejection_reason=db_item.rejection_reason,
            hashtags=db_item.hashtags or [],
            mentions=db_item.mentions or [],
            media_urls=db_item.media_urls or [],
            metadata=db_item.metadata or {}
        )
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        hashtags = re.findall(r'#(\w+)', content)
        return list(set(hashtags))  # Remove duplicates
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract mentions from content"""
        import re
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))  # Remove duplicates
    
    def __del__(self):
        """Close database session"""
        if hasattr(self, 'session'):
            self.session.close()

# Usage example and testing functions
async def test_approval_queue():
    """Test the approval queue functionality"""
    queue = ApprovalQueue()
    
    # Add test content
    item_id = await queue.add_item(
        content="This is a test tweet with #hashtag and @mention! 🚀",
        content_type="tweet",
        source="test",
        metadata={"test": True}
    )
    
    print(f"Added test item: {item_id}")
    
    # Get the item
    item = await queue.get_item(item_id)
    if item:
        print(f"Retrieved item: {item.content}")
        print(f"Hashtags: {item.hashtags}")
        print(f"Mentions: {item.mentions}")
    
    # Update scores
    await queue.update_scores(item_id, quality_score=85.5, brand_compliance_score=92.0)
    
    # Get pending items
    pending = await queue.get_pending_items()
    print(f"Pending items: {len(pending)}")
    
    # Approve the item
    await queue.approve_item(item_id, "Great content!")
    
    # Get analytics
    analytics = await queue.get_analytics()
    print(f"Analytics: {analytics}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_approval_queue())