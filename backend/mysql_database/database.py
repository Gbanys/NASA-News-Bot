import mysql.connector
import os
from datetime import datetime

mysql_database = mysql.connector.connect(
  host=os.environ["DB_HOSTNAME"],
  user=os.environ["DB_USER"],
  password=os.environ['MYSQL_ROOT_PASSWORD'],
  database="nasa",
  port="3306"
)

cursor = mysql_database.cursor()

def add_user(username: str, email: str) -> None:
    sql = "INSERT INTO user (name, email) VALUES (%s, %s)"
    val = (username, email)
    cursor.execute(sql, val)
    mysql_database.commit()


def delete_user(user_id: int) -> None:
    sql = f"DELETE FROM user WHERE id = {user_id}"
    cursor.execute(sql)
    mysql_database.commit()


def get_users():
    sql= f"SELECT * FROM user;"
    cursor.execute(sql)
    return cursor.fetchall()


def get_user_by_name(name: str):
    sql = "SELECT * FROM user WHERE name = %s;"
    cursor.execute(sql, (name,))
    return cursor.fetchall()


def add_conversation(user_id: int) -> None:
    sql = "INSERT INTO conversation (user_id, timestamp) VALUES (%s, %s)"
    timestamp = datetime.now()
    val = (user_id, timestamp)
    cursor.execute(sql, val)
    mysql_database.commit()


def add_conversation_with_specific_id(user_id: int, conversation_id: int):
    sql = "INSERT INTO conversation (id, user_id, timestamp) VALUES (%s, %s, %s)"
    timestamp = datetime.now()
    val = (conversation_id, user_id, timestamp)
    cursor.execute(sql, val)
    mysql_database.commit()


def delete_conversation(conversation_id: int) -> None:
    sql = f"DELETE FROM conversation WHERE id = {conversation_id}"
    cursor.execute(sql)
    mysql_database.commit()


def get_conversation_by_user(user_id: int) -> None:
    sql = f"SELECT * FROM conversation WHERE user_id = {user_id} ORDER BY timestamp ASC;"
    cursor.execute(sql)
    return cursor.fetchall()


def get_conversation_by_conversation_id(conversation_id: int) -> None:
    sql = f"SELECT * FROM conversation WHERE id = {conversation_id} ORDER BY timestamp ASC;"
    cursor.execute(sql)
    return cursor.fetchall()


def add_question(question: str, conversation_id: int):
    sql = "INSERT INTO question (question, conversation_id) VALUES (%s, %s)"
    val = (question, conversation_id)
    cursor.execute(sql, val)
    mysql_database.commit()

    
def get_questions_by_conversation(conversation_id: int):
    sql= f"SELECT * FROM question WHERE conversation_id = {conversation_id};"
    cursor.execute(sql)
    return cursor.fetchall()


def add_answer(answer: str, question_id: int):
    sql = "INSERT INTO answer (answer, question_id) VALUES (%s, %s)"
    val = (answer,question_id)
    cursor.execute(sql, val)
    mysql_database.commit()


def add_feedback_to_answer(answer_id: int, feedback: str):
    print("Hellloooooooooo")
    print(feedback)
    sql = "UPDATE answer SET feedback = %s WHERE id = %s;"
    cursor.execute(sql, (feedback, answer_id))
    mysql_database.commit()


def get_answers_by_question(question_id: int):
    sql= f"SELECT * FROM answer WHERE question_id = {question_id};"
    cursor.execute(sql)
    return cursor.fetchall()


def get_answers_by_id(answer_id: int):
    sql= f"SELECT * FROM answer WHERE id = {answer_id};"
    cursor.execute(sql)
    return cursor.fetchall()


def update_thumbs_value_in_database(answer_id: int, thumbs_value: int):
    sql= f"UPDATE answer SET thumbs_value = {thumbs_value} WHERE id = {answer_id};"
    cursor.execute(sql)
    mysql_database.commit()