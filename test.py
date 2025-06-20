# test_approval_queue.py
import asyncio
from review_system.approval_dashboard.approval_queue import ApprovalQueue

async def test_queue():
    queue = ApprovalQueue()
    
    # Add test content
    item_id = await queue.add_item(
        content="This is a test tweet! #testing",
        content_type="tweet",
        source="manual"
    )
    
    print(f"Added item: {item_id}")
    
    # Get pending items
    pending = await queue.get_pending_items()
    print(f"Pending items: {len(pending)}")
    
    # Approve the item
    await queue.approve_item(item_id, "Looks good!")
    print("Item approved!")

if __name__ == "__main__":
    asyncio.run(test_queue())