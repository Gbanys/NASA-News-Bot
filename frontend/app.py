from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import requests
import boto3
import json
import requests

app = FastAPI()

secret_name = "nasa_chatbot_cognito_secrets"
region_name = "eu-west-2"

# session = boto3.session.Session(region_name=region_name)
# client = session.client(
#     service_name='secretsmanager',
#     region_name=region_name
# )

# secrets = json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])
# app.add_middleware(SessionMiddleware, secret_key=secrets["secret_key"])

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# COGNITO_DOMAIN = secrets["cognito_domain"]
# COGNITO_CLIENT_ID = secrets["cognito_app_client_id"]
# COGNITO_CLIENT_SECRET = secrets["cognito_app_client_secret"]
# REDIRECT_URI = "http://localhost:8000/callback"

# # The URL to redirect users to for authentication
# @app.get("/login")
# def login():
#     cognito_login_url = (
#         f"https://{COGNITO_DOMAIN}/login?"
#         f"client_id={COGNITO_CLIENT_ID}&"
#         f"response_type=code&"
#         f"scope=email+openid+profile&"
#         f"redirect_uri={REDIRECT_URI}"
#     )
#     return RedirectResponse(url=cognito_login_url)

# # Callback endpoint to handle redirection from Cognito after login
# @app.get("/callback")
# async def callback(request: Request, code: str):
#     token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
#     data = {
#         "grant_type": "authorization_code",
#         "client_id": COGNITO_CLIENT_ID,
#         "redirect_uri": REDIRECT_URI,
#         "code": code
#     }
#     auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

#     # Exchange authorization code for access and ID tokens
#     response = requests.post(token_url, data=data, auth=auth)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Failed to retrieve tokens")

#     tokens = response.json()
#     id_token = tokens.get("id_token")
    
#     # Now, you can store the ID token in a session or use it as needed
#     request.session["id_token"] = id_token  # Example of session management

#     return RedirectResponse(url="/")

# Root endpoint, which requires authentication
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Check if user is authenticated
    # if "id_token" not in request.session:
    #     return RedirectResponse(url="/login")
    data = {
        "name" : "test",
        "email" : "test@gmail.com"
    }
    response = requests.post(f"http://{os.environ['BACKEND_LOAD_BALANCER_URL']}/users", json=data)
    user_id = response.json()[0][0]
    response = requests.get(f"http://{os.environ['BACKEND_LOAD_BALANCER_URL']}/get_conversations/{user_id}")
    conversations = response.json()
    if not conversations:
        requests.post(f"http://{os.environ['BACKEND_LOAD_BALANCER_URL']}/add_conversation/{user_id}")
        response = requests.get(f"http://{os.environ['BACKEND_LOAD_BALANCER_URL']}/get_conversations/{user_id}")
        conversations = response.json()
    first_conversation_id = conversations[0]['id']

    return templates.TemplateResponse(
        name="home.html",
        context={
            "request": request,
            "websocket_url": f"ws://{os.environ['BACKEND_WEBSOCKET_URL'].strip()}/websocket",
            "user_id": user_id,
            "conversations": json.dumps(conversations),
            "first_conversation_id" : first_conversation_id
        }
    )