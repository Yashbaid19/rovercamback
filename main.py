from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

latest_frame = None

import os

@app.get("/api/config/camera-feeds")
def get_camera_feed():
    return {
        "rover_feed_url": os.getenv("ROVER_FEED_URL")
    }

@app.get("/")
def home():
    return {"status": "Server running 🚀"}


@app.post("/upload-frame")
async def upload_frame(request: Request):
    global latest_frame
    latest_frame = await request.body()
    return {"status": "frame received"}


def mjpeg_generator():
    global latest_frame
    while True:
        if latest_frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                latest_frame +
                b"\r\n"
            )
        asyncio.sleep(0.1)


@app.get("/stream")
def stream():
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )