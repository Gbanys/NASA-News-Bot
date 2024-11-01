import mysql.connector
import os

mysql_database = mysql.connector.connect(
  host="0.0.0.0",
  user="root",
  password="drakonas",
  database="nasa",
  port="3306"
)

cursor = mysql_database.cursor()

def add_user(username: str, email: str) -> None:
    sql = "INSERT INTO user (name, email) VALUES (%s, %s)"
    val = (username, email)
    cursor.execute(sql, val)


def delete_user(user_id: int) -> None:
    sql = f"DELETE FROM user WHERE id = {user_id}"
    cursor.execute(sql)


def get_users():
    sql= f"SELECT * FROM user;"
    cursor.execute(sql)
    return cursor.fetchall()


def add_conversation(user_id: int) -> None:
    sql = "INSERT INTO conversation (user_id) VALUES (%s)"
    val = (user_id,)
    cursor.execute(sql, val)


def get_conversation_by_user(user_id: int) -> None:
    sql = f"SELECT * FROM conversation WHERE user_id = {user_id}"
    cursor.execute(sql)
    return cursor.fetchall()


def add_question(question: str, conversation_id: int):
    sql = "INSERT INTO question (question, conversation_id) VALUES (%s, %s)"
    val = (question, conversation_id)
    cursor.execute(sql, val)

    
def get_questions_by_conversation(conversation_id: int):
    sql= f"SELECT * FROM question WHERE conversation_id = {conversation_id};"
    cursor.execute(sql)
    return cursor.fetchall()


def add_answer(answer: str, question_id: int):
    sql = "INSERT INTO answer (answer, question_id) VALUES (%s, %s)"
    val = (answer,question_id)
    cursor.execute(sql, val)


def get_answers_by_question(question_id: int):
    sql= f"SELECT * FROM answer WHERE question_id = {question_id};"
    cursor.execute(sql)
    return cursor.fetchall()