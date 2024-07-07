import os
import psycopg2
import psycopg2.extras


def open_db_conn():
    conn = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_ENDPOINT"),
        port=5432
    )
    return conn

def load_to_db(conn, data):
    cursor = conn.cursor()
    for item in data:
        cursor.execute(
            "INSERT INTO raw_data (post_id, praw_tree) VALUES (%s, %s)",
            (item['post_id'], psycopg2.extras.Json(item))
        )
    conn.commit()

def close_db_conn(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')