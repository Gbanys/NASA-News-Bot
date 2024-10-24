from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="home.html",
        context={
            "websocket_url" : f"ws://{os.environ['BACKEND_LOAD_BALANCER_URL'].strip()}/websocket"
        }
    )

