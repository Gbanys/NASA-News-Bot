from typing import Any
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from mysql_database.database import add_answer, add_question, get_answers_by_question, get_questions_by_conversation

class MessageHistoryFromMySQL:
    session_id: str
    messages: list[str]

    def __init__(self, session_id: str, messages: list[str]) -> None:
        self.session_id = session_id
        self.messages = messages

    def get_session_history(self, session_id: str) -> list[str]:
        return self.messages
    
    def add_messages(self, new_messages: list[Any]) -> None:
        print(new_messages)
        for message in new_messages:
            if isinstance(message, HumanMessage):
                print(message)
                add_question(message.content, conversation_id=self.session_id)
            elif isinstance(message, AIMessage):
                final_question = get_questions_by_conversation(conversation_id=self.session_id)[-1]
                add_answer(message.content, question_id=final_question[0])
        self.messages += new_messages
        

def get_message_history(session_id: int) -> MessageHistoryFromMySQL:
    questions = get_questions_by_conversation(conversation_id=session_id)
    messages = []
    for question in questions:
        messages.append(HumanMessage(content=question[1], additional_kwargs={}, response_metadata={}))
        answers = get_answers_by_question(question_id=question[0])
        for answer in answers:
            messages.append(AIMessage(content=answer[1], additional_kwargs={}, response_metadata={}))
    return MessageHistoryFromMySQL(session_id=session_id, messages=messages)


def get_questions_and_answers_from_database(session_id: int) -> list:
    questions = get_questions_by_conversation(conversation_id=session_id)
    messages = []
    for question in questions:
        messages.append({"id" : question[0], "chat-bubble user" : question[1]})
        answers = get_answers_by_question(question_id=question[0])
        for answer in answers:
            messages.append({"id" : answer[0], "chat-bubble ai" : answer[1]})
    return messages