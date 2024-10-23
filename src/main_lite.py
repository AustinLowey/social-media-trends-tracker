# This entrypoint/API is simpler than main.py, as it does not interface with any database.
# Must configure PRAW env vars prior to use (see README for details).

# This is the primary entrypoint/API for this project.
# Must configure both PRAW and Database env vars prior to use (see README for details).


import csv
from datetime import datetime

from src.extract.extract_subreddit_lite import fetch_subreddit_data_as_csv


def extract_reddit_data_as_csv(
    time_filter,
    subreddits_list_file,
    num_posts,
    max_depth,
    max_top_level_comments,
    max_replies_per_comment
):
    """
    Extracts post data and saves as a .csv for a list of subreddits defined in a .txt file.

    Parameters:
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

    # Open the CSV file for writing
    now = datetime.now().strftime('%Y%m%d')
    output_csv_fname = f'src/extract/output_samples/subreddits_top_data_{now}.csv'
    with open(output_csv_fname, mode='w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(
            [
                'subreddit',
                'post_id',
                'submission_type',
                'upvote_score',
                'submission_content',
                'author',
                'created_on', # Local time
            ]
        )

        # For each subreddit, get top posts/responses and write to csv
        for subreddit in subreddits:
            fetch_subreddit_data_as_csv(
                csvwriter,
                subreddit,
                time_filter=time_filter,
                num_posts=num_posts,
                max_depth=max_depth,
                max_top_level_comments=max_top_level_comments,
                max_replies_per_comment=max_replies_per_comment
            )


if __name__ == "__main__":
    # Execute primary API for extraction + loading to database
    extract_reddit_data_as_csv(
        time_filter='week',
        subreddits_list_file='src/extract/subreddit_list_lite.txt',
        num_posts=10,
        max_depth=3,
        max_top_level_comments=5,
        max_replies_per_comment=2
)