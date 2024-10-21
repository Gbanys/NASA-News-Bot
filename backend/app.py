from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/websocket")
async def main(websocket: WebSocket):
    await websocket.accept()
    print("Hello world")
    while True:
        data = await websocket.receive_json()
        await websocket.send_json(
            {
                "type": data["type"],
                "content": data["content"],
            }
        )
