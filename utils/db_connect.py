import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        # Initialize the connection as None
        self.connection = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        if self.connection is None:
            try:
                self.connection = mysql.connector.connect(
                    host='127.0.0.1', 
                    user='user',  
                    password='',  
                    database='test'  
                )

                if self.connection.is_connected():
                    print("Successfully connected to the database")
                return self.connection

            except Error as e:
                print(f"Error: {e}")
                self.connection = None
                return None

    def get_cursor(self):
        """Returns a cursor from the current connection with error handling."""
        try:
            if self.connection and self.connection.is_connected():
                return self.connection.cursor(dictionary=True)
            else:
                raise Exception("No active database connection.")
        except Exception as e:
            print(f"Error getting cursor: {e}")
            return None

    def close(self):
        """Safely close the database connection with error handling."""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("Database connection closed.")
            else:
                print("No connection to close.")
        except Exception as e:
            print(f"Error closing connection: {e}")

# Singleton instance of Database for reuse
database = Database()