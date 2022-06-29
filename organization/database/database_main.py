import sqlite3
from sqlite3 import Error

class Database(object):
    def __init__(self, database):
        self.path = f"organization\database\{database}.sqlite"
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.path)
            print("Connection to SQLite DB successful")
            self.connection.row_factory = sqlite3.Row
        except Error as e:
            print(f"The error '{e}' occurred")
    
    # Insert to DB
    def create_user(self, username, usersurname, userage, useraccesslevel, userlastactivity, userkey):
        query = f"""
                INSERT INTO
                    users (name, surname, age, accesslevel, lastactivity, key)
                VALUES
                    ('{username}', '{usersurname}', {userage}, {useraccesslevel}, '{userlastactivity}', '{userkey}');
                """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    # Read from DB
    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
        
    def get_user_info(self, id):
        query = f"SELECT * FROM users WHERE id={id}"
        cursor = self.connection.cursor()
        user_info = None
        try:
            cursor.execute(query)
            user_info = cursor.fetchone()
            return user_info
        except Error as e:
            print(f"The error '{e}' occurred")
    
    def get_employers_list(self):
        query = f"SELECT id, name, surname FROM users"
        cursor = self.connection.cursor()
        emloyers_names = None
        try:
            cursor.execute(query)
            emloyers_names = cursor.fetchall()
            return list(emloyers_names)
        except Error as e:
            print(f"The error '{e}' occurred")
    
    # Update DB
    def update_cam_state(self, id, state):
        query = f"""
                UPDATE
                    users
                SET
                    isOnCam={state}
                WHERE
                    id={id}
                """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Table updated successfully")
        except Error as e:
            print(f"The error '{e}' occurred")