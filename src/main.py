from src.extract.extract_subreddit import fetch_subreddit_data
from src.load.load_to_postgres import open_db_conn, load_to_db, close_db_conn


# Get list of subreddits
with open('src/extract/subreddit_list.txt', 'r') as f:
    subreddits = [line.strip() for line in f]

conn = open_db_conn()

# For each subreddit, get top posts and load to database
for subreddit in subreddits:
    extracted_data = fetch_subreddit_data(subreddit, num_posts=10)
    load_to_db(conn, extracted_data)

close_db_conn(conn)