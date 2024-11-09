from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mysql_database.message_history import get_message_history, get_questions_and_answers_from_database
from nasa_answer_generator import query
from mysql_database.database import add_conversation, add_conversation_with_specific_id, add_feedback_to_answer, add_user, delete_conversation, get_answers_by_id, get_answers_by_question, get_conversation_by_conversation_id, get_conversation_by_user, get_questions_by_conversation, get_user_by_name, update_thumbs_value_in_database
import json

class User(BaseModel):
    name: str
    email: str

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
    while True:
        data = await websocket.receive_json()
        if data["type"] == "retrieve_ai_response":
            new_message_history = await retrieve_ai_response(int(data["user_id"]), data["content"], int(data["conversation_id"]))
            conversations = await get_conversation_from_database(int(data["user_id"]))
            await websocket.send_json(
                {
                    "type": data["type"],
                    "message_history": json.dumps(new_message_history),
                    "conversations" : json.dumps(conversations),
                }
            )
        elif data["type"] == "get_questions_and_answers":
            message_history = await get_questions_and_answers(int(data["conversation_id"]))
            conversations = await get_conversation_from_database(int(data["user_id"]))
            await websocket.send_json(
                {
                    "type" : "get_questions_and_answers",
                    "message_history" : json.dumps(message_history),
                }
            )
        elif data["type"] == "add_conversation":
            await add_conversation_to_database(int(data["user_id"]))
            conversations = await get_conversation_from_database(int(data["user_id"]))
            await websocket.send_json(
                {
                    "type" : "get_all_conversations",
                    "conversations" : json.dumps(conversations)
                }
            )
        elif data["type"] == "delete_conversation":
            await delete_conversation_from_database(data["delete_conversation_id"])
            conversations = await get_conversation_from_database(int(data["user_id"]))
            message_history = await get_questions_and_answers(int(data["first_conversation_id"]))
            await websocket.send_json(
                {
                    "type" : "delete_conversation",
                    "conversations" : json.dumps(conversations),
                    "message_history" : json.dumps(message_history),
                    "first_conversation_id" : data["first_conversation_id"],
                    "delete_conversation_id" : data["delete_conversation_id"]
                }
            )
        elif data["type"] == "update_thumbs_value":
            answer = await get_answers_by_answer_id_in_database(int(data["answer_id"]))
            if answer[0][3] == data["thumbs_value"]:
                thumbs_value = 0
            else:
                thumbs_value = int(data["thumbs_value"])
            await update_thumbs_value(data["answer_id"], thumbs_value)
            message_history = await get_questions_and_answers(int(data["conversation_id"]))
            conversations = await get_conversation_from_database(int(data["user_id"]))
            await websocket.send_json(
                {
                    "type" : "update_thumbs_value",
                    "message_history" : json.dumps(message_history),
                    "conversation_id" : int(data["conversation_id"]),
                    "answer_id" : int(data["answer_id"]),
                    "conversations" : conversations
                }
            )
        elif data["type"] == "submit_feedback":
            await add_feedback(answer_id=int(data["answer_id"]), feedback=data["feedback"])



async def retrieve_ai_response(user_id: int, userInput: str, conversation_id: int) -> list:
    conversation = get_conversation_by_conversation_id(conversation_id)
    if not conversation:
        add_conversation_with_specific_id(user_id, conversation_id)
    message_history = query(userInput, conversation_id)
    return message_history



@app.post("/users")
async def retrieve_user_info_from_database(user: User):
    retrieved_user_from_database = get_user_by_name(user.name)
    if not retrieved_user_from_database:
        add_user(user.name, user.email)
        retrieved_user_from_database = get_user_by_name(user.name)
    return retrieved_user_from_database


@app.get("/get_conversations/{user_id}")
async def get_conversation_from_database(user_id: int) -> None:
    conversations = get_conversation_by_user(user_id)
    conversations_dicts = []
    for conversation in conversations:
        conversation_dict = {
            "id": conversation[0],
            "user_id": conversation[1],
            "timestamp": conversation[2].isoformat() if isinstance(conversation[2], datetime) else conversation[2],
        }
        conversations_dicts.append(conversation_dict)
    return conversations_dicts

async def get_questions_and_answers(conversation_id: int):
    list_of_messages = get_questions_and_answers_from_database(conversation_id)
    return list_of_messages

@app.post("/add_conversation/{user_id}")
async def add_conversation_to_database(user_id: int) -> None:
    add_conversation(user_id)

async def add_conversation_with_specific_id_to_database(user_id: int, conversation_id: int) -> None:
    add_conversation_with_specific_id(user_id, conversation_id)

async def delete_conversation_from_database(conversation_id: int) -> None:
    delete_conversation(conversation_id)

async def update_thumbs_value(answer_id: int, thumbs_value: int) -> None:
    update_thumbs_value_in_database(answer_id, thumbs_value)

async def get_answers_by_answer_id_in_database(answer_id: int):
    return get_answers_by_id(answer_id)

async def add_feedback(answer_id: int, feedback: str) -> None:
    add_feedback_to_answer(answer_id, feedback)
