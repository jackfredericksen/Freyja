"""
Freyja - Review Dashboard Web Interface
FastAPI-based dashboard for content approval and quality control
"""

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

from config import get_settings
from review_system.content_scoring.quality_scorer import ContentScorer
from review_system.brand_guidelines.voice_checker import BrandVoiceChecker
from review_system.approval_dashboard.approval_queue import ApprovalQueue, ContentItem, ContentStatus

settings = get_settings()
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Freyja Review Dashboard",
    description="Content approval and quality control dashboard",
    version="1.0.0"
)

# Setup templates and static files
templates_dir = Path("review_system/approval_dashboard/templates")
static_dir = Path("review_system/approval_dashboard/static")

# Create directories if they don't exist
templates_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize components
content_scorer = ContentScorer()
brand_checker = BrandVoiceChecker()
approval_queue = ApprovalQueue()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard homepage"""
    try:
        # Get queue statistics
        pending_count = await approval_queue.get_pending_count()
        approved_count = await approval_queue.get_approved_count()
        rejected_count = await approval_queue.get_rejected_count()
        
        # Get recent items
        recent_items = await approval_queue.get_recent_items(limit=5)
        
        stats = {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "total": pending_count + approved_count + rejected_count
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_items": recent_items,
            "brand_settings": settings.brand
        })
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading dashboard")

@app.get("/queue", response_class=HTMLResponse)
async def review_queue(request: Request, status: Optional[str] = "pending"):
    """Display content review queue"""
    try:
        if status == "pending":
            items = await approval_queue.get_pending_items()
        elif status == "approved":
            items = await approval_queue.get_approved_items()
        elif status == "rejected":
            items = await approval_queue.get_rejected_items()
        else:
            items = await approval_queue.get_all_items()
        
        return templates.TemplateResponse("queue.html", {
            "request": request,
            "items": items,
            "current_status": status,
            "brand_settings": settings.brand
        })
        
    except Exception as e:
        logger.error(f"Error loading queue: {e}")
        raise HTTPException(status_code=500, detail="Error loading queue")

@app.get("/review/{item_id}", response_class=HTMLResponse)
async def review_item(request: Request, item_id: str):
    """Review individual content item"""
    try:
        item = await approval_queue.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Content item not found")
        
        # Get quality scores
        quality_scores = await content_scorer.score_content(item.content, item.content_type)
        
        # Check brand compliance
        brand_compliance = await brand_checker.check_compliance(item.content)
        
        # Get suggestions for improvement
        suggestions = await content_scorer.get_improvement_suggestions(item.content, quality_scores)
        
        return templates.TemplateResponse("review_item.html", {
            "request": request,
            "item": item,
            "quality_scores": quality_scores,
            "brand_compliance": brand_compliance,
            "suggestions": suggestions,
            "brand_settings": settings.brand
        })
        
    except Exception as e:
        logger.error(f"Error loading review item: {e}")
        raise HTTPException(status_code=500, detail="Error loading review item")

@app.post("/approve/{item_id}")
async def approve_content(item_id: str, feedback: Optional[str] = Form(None)):
    """Approve content item"""
    try:
        success = await approval_queue.approve_item(item_id, feedback)
        if success:
            logger.info(f"Content item {item_id} approved")
            return RedirectResponse(url="/queue", status_code=303)
        else:
            raise HTTPException(status_code=404, detail="Content item not found")
            
    except Exception as e:
        logger.error(f"Error approving item: {e}")
        raise HTTPException(status_code=500, detail="Error approving content")

@app.post("/reject/{item_id}")
async def reject_content(item_id: str, reason: str = Form(...)):
    """Reject content item"""
    try:
        success = await approval_queue.reject_item(item_id, reason)
        if success:
            logger.info(f"Content item {item_id} rejected: {reason}")
            return RedirectResponse(url="/queue", status_code=303)
        else:
            raise HTTPException(status_code=404, detail="Content item not found")
            
    except Exception as e:
        logger.error(f"Error rejecting item: {e}")
        raise HTTPException(status_code=500, detail="Error rejecting content")

@app.post("/edit/{item_id}")
async def edit_content(
    item_id: str, 
    edited_content: str = Form(...),
    edit_notes: Optional[str] = Form(None)
):
    """Edit and resubmit content item"""
    try:
        success = await approval_queue.edit_item(item_id, edited_content, edit_notes)
        if success:
            logger.info(f"Content item {item_id} edited and resubmitted")
            return RedirectResponse(url=f"/review/{item_id}", status_code=303)
        else:
            raise HTTPException(status_code=404, detail="Content item not found")
            
    except Exception as e:
        logger.error(f"Error editing item: {e}")
        raise HTTPException(status_code=500, detail="Error editing content")

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics and insights dashboard"""
    try:
        # Get approval analytics
        analytics = await approval_queue.get_analytics()
        
        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "analytics": analytics,
            "brand_settings": settings.brand
        })
        
    except Exception as e:
        logger.error(f"Error loading analytics: {e}")
        raise HTTPException(status_code=500, detail="Error loading analytics")

@app.get("/api/queue/stats")
async def get_queue_stats():
    """API endpoint for queue statistics"""
    try:
        stats = {
            "pending": await approval_queue.get_pending_count(),
            "approved": await approval_queue.get_approved_count(),
            "rejected": await approval_queue.get_rejected_count()
        }
        stats["total"] = sum(stats.values())
        return stats
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting queue stats")

@app.post("/api/content/submit")
async def submit_content(
    content: str = Form(...),
    content_type: str = Form(...),
    source: str = Form("manual"),
    metadata: Optional[str] = Form(None)
):
    """API endpoint to submit new content for review"""
    try:
        metadata_dict = json.loads(metadata) if metadata else {}
        
        item_id = await approval_queue.add_item(
            content=content,
            content_type=content_type,
            source=source,
            metadata=metadata_dict
        )
        
        return {"success": True, "item_id": item_id}
        
    except Exception as e:
        logger.error(f"Error submitting content: {e}")
        raise HTTPException(status_code=500, detail="Error submitting content")

@app.get("/api/content/{item_id}/preview")
async def preview_content(item_id: str):
    """API endpoint to preview how content will look when posted"""
    try:
        item = await approval_queue.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Content item not found")
        
        # Generate preview based on content type
        preview = await generate_content_preview(item)
        
        return {"preview": preview, "item": item.dict()}
        
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail="Error generating preview")

async def generate_content_preview(item: ContentItem) -> dict:
    """Generate preview of how content will appear when posted"""
    preview = {
        "content": item.content,
        "content_type": item.content_type,
        "character_count": len(item.content),
        "hashtags": extract_hashtags(item.content),
        "mentions": extract_mentions(item.content),
        "estimated_reach": "Calculating...",
        "best_posting_time": "Based on your audience data"
    }
    
    return preview

def extract_hashtags(content: str) -> List[str]:
    """Extract hashtags from content"""
    import re
    return re.findall(r'#\w+', content)

def extract_mentions(content: str) -> List[str]:
    """Extract mentions from content"""
    import re
    return re.findall(r'@\w+', content)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 404,
        "error_message": "Page not found"
    })

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_code": 500,
        "error_message": "Internal server error"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)