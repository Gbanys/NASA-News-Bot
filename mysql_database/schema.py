import mysql.connector
import os

mysql_database = mysql.connector.connect(
  host="localhost",
  user="root",
  password=os.environ['MYSQL_ROOT_PASSWORD']
)

cursor = mysql_database.cursor()

cursor.execute(
    """
    CREATE DATABASE IF NOT EXISTS nasa;
    USE nasa;
    CREATE TABLE user (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        name VARCHAR(255), 
        email VARCHAR(255)
    );
    CREATE TABLE conversation (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        user_id INT,
        FOREIGN KEY (user_id) REFERENCES user(id)
    );
    CREATE TABLE question (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        question VARCHAR(255), 
        conversation_id INT,
        FOREIGN KEY (conversation_id) REFERENCES conversation(id)
    );
    CREATE TABLE answer (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        answer MEDIUMTEXT, 
        feedback VARCHAR(255),
        thumbs_value INT,
        question_id INT,
        FOREIGN KEY (question_id) REFERENCES question(id)
    );
""")
