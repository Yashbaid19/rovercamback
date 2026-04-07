from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

latest_frame = None


# 📤 ESP32 uploads frame
@app.post("/upload-frame")
async def upload_frame(request: Request):
    global latest_frame
    latest_frame = await request.body()
    return {"status": "frame received"}


# 🔴 MJPEG STREAM
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


# ⚡ WEBSOCKET STREAM
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global latest_frame

    while True:
        if latest_frame:
            await websocket.send_bytes(latest_frame)
        await asyncio.sleep(0.1)