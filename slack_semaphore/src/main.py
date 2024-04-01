from fastapi import FastAPI
from typing import List
import queue
import asyncio
import pync

# Initialize FastAPI
app = FastAPI()

# Initialize queue for notifications
notification_queue = queue.Queue()

# Endpoint to fetch notifications
@app.get("/notifications/", response_model=List[str])
async def get_notifications():
    notifications = []
    while not notification_queue.empty():
        notifications.append(notification_queue.get())
    return notifications

# Endpoint to serve static webpage
@app.get("/")
async def get_static_page():
    with open("static/index.html", "r") as file:
        return file.read()

# Function to capture Slack notifications from Mac OS notification center
def capture_slack_notifications():
    try:
        notifications = pync.get_notifications()
        for notification in notifications:
            if "slack" in notification.get('title', '').lower() or "slack" in notification.get('message', '').lower():
                notification_queue.put(notification['message'])
    except Exception as e:
        print(f"Error capturing notifications: {e}")

# Periodically capture Slack notifications from Mac OS
async def periodic_task():
    while True:
        capture_slack_notifications()
        await asyncio.sleep(60)  # Capture notifications every minute

# Start the periodic task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
