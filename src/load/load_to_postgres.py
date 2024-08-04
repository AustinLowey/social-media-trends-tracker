import os
import psycopg2
import psycopg2.extras


def open_db_conn(connection_type="local"):
    conn_params = {
        "database": os.getenv(f"{connection_type.upper()}_DB_NAME"),
        "user": os.getenv(f"{connection_type.upper()}_DB_USER"),
        "password": os.getenv(f"{connection_type.upper()}_DB_PASSWORD")
    }
    if connection_type.upper() == "AWS":
        conn_params["host"] = os.getenv("AWS_DB_ENDPOINT")
        conn_params["port"] = 5432
    conn = psycopg2.connect(**conn_params)
    return conn

def load_to_db(conn, subreddit, fetch_date, data):
    cursor = conn.cursor()
    for item in data:
        cursor.execute(
            "INSERT INTO raw_data (post_id, subreddit, date, praw_tree) VALUES (%s, %s, %s, %s)",
            (item['post_id'], subreddit, fetch_date, psycopg2.extras.Json(item))
        )
    conn.commit()

def close_db_conn(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')