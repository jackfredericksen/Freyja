#!/usr/bin/env python3
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
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        print("\nMake sure you have installed the required packages:")
        print("pip install fastapi uvicorn jinja2 aiosqlite python-multipart")
