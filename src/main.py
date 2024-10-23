# This is the primary entrypoint/API for this project.
# Must configure both PRAW and Database env vars prior to use (see README for details).


import datetime

from src.extract.extract_subreddit import fetch_subreddit_data_as_json
from src.load.load_to_postgres import open_db_conn, load_to_db, close_db_conn


def extract_load_reddit_data_to_db(
    target_db,
    time_filter,
    subreddits_list_file,
    num_posts,
    max_depth,
    max_top_level_comments,
    max_replies_per_comment
):
    """
    Extracts and loads post data to database for a list of subreddits defined in a .txt file.

    Parameters:
        target_db = Database type (i.e., local or AWS)
        time_filter = Top posts in the past: "day", "week", "month", "year", or "all"
        subreddits_list_file = Path for .txt file listing subreddits for extraction
        num_posts = Max number of posts to extract from each subreddit
        max_depth = Max depth of replies in each post's comment tree
        max_top_level_comments = Max number of top level comments (i.e., affects tree width)
        max_replies_per_comment = Max number of replies (i.e., affects tree width)
    """

    # Get list of subreddits
    with open(subreddits_list_file, 'r') as f:
        subreddits = [line.strip() for line in f]

    # Create connection to 'local' or 'aws' db
    conn = open_db_conn(connection_type=target_db)

    # For each subreddit, get top posts and load to database
    fetch_date = datetime.date.today().isoformat()
    for subreddit in subreddits:
        extracted_data = fetch_subreddit_data_as_json(
            subreddit,
            time_filter=time_filter,
            num_posts=num_posts,
            max_depth=max_depth,
            max_top_level_comments=max_top_level_comments,
            max_replies_per_comment=max_replies_per_comment
        )
        load_to_db(conn, subreddit, fetch_date, extracted_data)

    close_db_conn(conn)


if __name__ == "__main__":
    # Execute primary API for extraction + loading to database
    extract_load_reddit_data_to_db(
        target_db='local',
        time_filter='day',
        subreddits_list_file='src/extract/subreddit_list.txt',
        num_posts=10,
        max_depth=3,
        max_top_level_comments=5,
        max_replies_per_comment=2
)