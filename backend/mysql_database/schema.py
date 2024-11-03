import mysql.connector
import os

mysql_database = mysql.connector.connect(
  host=os.environ["DB_HOSTNAME"],
  user=os.environ["DB_USER"],
  password=os.environ['MYSQL_ROOT_PASSWORD']
)

cursor = mysql_database.cursor()

try:
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
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        );
        CREATE TABLE question (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            question VARCHAR(255), 
            conversation_id INT,
            FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
        );
        CREATE TABLE answer (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            answer MEDIUMTEXT, 
            feedback VARCHAR(255),
            thumbs_value INT,
            question_id INT,
            FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE
        );
    """)
except:
    print("MYSQL database already has the correct schema")