import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def create_connection():
    """ or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def setup_database():
    sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files (
                                        id integer PRIMARY KEY,
                                        path text NOT NULL,
                                        artist text,
                                        album text,
                                        title text,
                                        track integer,
                                        year integer,
                                        genre text
                                    ); """

    sql_create_config_table = """CREATE TABLE IF NOT EXISTS config (
                                    key TEXT PRIMARY KEY,
                                    value TEXT
                                );"""
    
    sql_create_users_table = """CREATE TABLE IF NOT EXISTS users (
                                    username TEXT PRIMARY KEY,
                                    hashed_password TEXT NOT NULL
                                );"""

    # create a database connection
    conn = create_connection()

    # create tables
    if conn is not None:
        create_table(conn, sql_create_files_table)
        create_table(conn, sql_create_config_table)
        create_table(conn, sql_create_users_table)
        
        # Migrate data from JSON files
        migrate_data(conn)
        
        conn.close()
    else:
        print("Error! cannot create the database connection.")

def migrate_data(conn):
    cursor = conn.cursor()
    
    # Migrate config.json
    config_path = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            
            # Migrate users
            if "users" in config:
                for username, hashed_password in config["users"].items():
                    cursor.execute("INSERT OR IGNORE INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed_password))
            
            # Migrate other config values
            for key, value in config.items():
                if key != "users":
                    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        conn.commit()

    # Migrate files.json
    files_path = os.path.join(BASE_DIR, "files.json")
    if os.path.exists(files_path):
        with open(files_path, "r") as f:
            files = json.load(f)
            for file_info in files:
                cursor.execute("""
                    INSERT OR IGNORE INTO files (id, path, artist, album, title, track, year, genre)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_info.get("id"),
                    file_info.get("path"),
                    file_info.get("artist"),
                    file_info.get("album"),
                    file_info.get("title"),
                    file_info.get("track"),
                    file_info.get("year"),
                    file_info.get("genre"),
                ))
        conn.commit()

if __name__ == '__main__':
    setup_database()
