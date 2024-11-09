from typing import Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from jose import jwt
import os
import requests
import boto3
import json
import requests
from starlette.templating import _TemplateResponse

app = FastAPI()

secret_name = "nasa_chatbot_cognito_secrets"
region_name = "eu-west-2"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


if os.environ["ENVIRONMENT"] == "PRODUCTION":

    ssm_client = boto3.client('ssm', region_name=region_name)
    def get_parameter(param_name, with_decryption=True) -> Any:
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']

    app.add_middleware(SessionMiddleware, secret_key=get_parameter('/nasa_chatbot/secret_key'))

    COGNITO_DOMAIN = get_parameter('/nasa_chatbot/cognito_domain')
    COGNITO_CLIENT_ID = get_parameter('/nasa_chatbot/cognito_app_client_id')
    COGNITO_CLIENT_SECRET = get_parameter('/nasa_chatbot/cognito_app_client_secret')
    REDIRECT_URI = f"http://{os.environ["REDIRECT_URI"]}/callback"

    # The URL to redirect users to for authentication
    @app.get("/login")
    def login():
        cognito_login_url = (
            f"https://{COGNITO_DOMAIN}/login?"
            f"client_id={COGNITO_CLIENT_ID}&"
            f"response_type=code&"
            f"scope=email+openid+profile&"
            f"redirect_uri={REDIRECT_URI}"
        )
        return RedirectResponse(url=cognito_login_url)

    # Callback endpoint to handle redirection from Cognito after login
    @app.get("/callback")
    async def callback(request: Request, code: str) -> RedirectResponse:
        token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": COGNITO_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
        auth = (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

        # Exchange authorization code for access and ID tokens
        response = requests.post(token_url, data=data, auth=auth)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve tokens")

        tokens = response.json()
        id_token = tokens.get("id_token")
        jwks_url = get_parameter('/nasa_chatbot/token_signing_key_url')

        # Fetch the JWKS data
        jwks_response = requests.get(jwks_url)
        jwks = jwks_response.json()

        decoded_token = jwt.decode(id_token, jwks, audience=COGNITO_CLIENT_ID, algorithms=["RS256"], options={"verify_at_hash": False})

        username = decoded_token.get("cognito:username")
        email = decoded_token.get("email")

        request.session["username"] = username
        request.session["email"] = email
        request.session["id_token"] = id_token

        return RedirectResponse(url="/")

# Root endpoint, which requires authentication
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    if os.environ["ENVIRONMENT"] == "PRODUCTION":
        if "id_token" not in request.session:
            return RedirectResponse(url="/login") 
        data = {"name" : request.session["username"], "email" : request.session["email"]}
    else:
        data = {"name" : "johndoe", "email" : "johndoe123@gmail.com"}

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