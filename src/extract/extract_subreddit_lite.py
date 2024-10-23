from datetime import datetime
import os
import praw


# PRAW Configuration
reddit = praw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_CLIENT_SECRET"),
    user_agent=os.getenv("PRAW_USER_AGENT"),
)


def fetch_subreddit_data_as_csv(
    csvwriter,
    subreddit_name,
    time_filter,
    num_posts=10,
    max_depth=3,
    max_top_level_comments=5,
    max_replies_per_comment=2
):
    """Extracts top posts for a given subreddit and time window while controlling the number of responses."""

    subreddit = reddit.subreddit(subreddit_name)
    submissions = subreddit.top(time_filter=time_filter, limit=num_posts)

    for submission in submissions:
        # Combine title and selftext for submission_content
        submission_content = (
            f'{submission.title}: {submission.selftext}'
        ).strip()
        
        # Write post data
        csvwriter.writerow([
            submission.subreddit.display_name,
            submission.id,
            'post',
            submission.score,
            submission_content,
            str(submission.author) if submission.author else None,
            datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d, %H:%M, %A'),
        ])

        # Recursively fetch and write comments and replies
        fetch_comments(
            csvwriter,
            submission.id,
            submission.subreddit.display_name,
            submission.comments,
            max_depth,
            max_top_level_comments,
            max_replies_per_comment
        )


def fetch_comments(
    csvwriter,
    post_id,
    subreddit_name,
    comment_forest,
    max_depth,
    max_top_level_comments,
    max_replies_per_comment,
    current_depth=1
):
    """Fetches comments recursively, handling both top-level and nested comments."""

    comment_forest.replace_more(limit=0)

    for comment in comment_forest[:max_top_level_comments]:
        if isinstance(comment, praw.models.MoreComments):
            continue

        # Write each comment as a new row in the CSV
        csvwriter.writerow([
            subreddit_name,
            post_id,
            'response',
            comment.score,
            comment.body,
            str(comment.author) if comment.author else None,
            datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d, %H:%M, %A'),
        ])

        # Recurse until tree limits are hit
        if current_depth < max_depth:
            fetch_comments(
                csvwriter,
                post_id,
                subreddit_name,
                comment.replies,
                max_depth,
                max_replies_per_comment,
                max_replies_per_comment,
                current_depth + 1
            )