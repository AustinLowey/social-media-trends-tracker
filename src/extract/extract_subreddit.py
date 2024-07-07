import datetime
import os
import praw


# PRAW Configuration
reddit = praw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_CLIENT_SECRET"),
    user_agent=os.getenv("PRAW_USER_AGENT"),
)

def fetch_subreddit_data(
    subreddit_name,
    num_posts=10,
    max_depth=3,
    max_top_level_comments=10,
    max_replies_per_comment=5
):
    """Extracts top posts for a given subreddit from past 24 hours."""
    subreddit = reddit.subreddit(subreddit_name)
    submissions = subreddit.top('day', limit=num_posts)

    today = datetime.date.today().isoformat()
    extracted_data = []

    for submission in submissions:
        comments_data = fetch_comments(
            submission.comments,
            max_depth,
            max_top_level_comments,
            max_replies_per_comment
        )

        post_data = {
            'post_id': submission.id,
            'title': submission.title if submission.title else None,
            'selftext': submission.selftext if submission.selftext else None,
            'author': str(submission.author) if submission.author else None,
            'upvote_score': submission.score,
            'created_utc': submission.created_utc,
            'num_comments': submission.num_comments,
            'comments': comments_data,
            'subreddit': subreddit_name,
            'fetch_date': today
        }
        extracted_data.append(post_data)

    return extracted_data


def fetch_comments(
    comment_forest,
    max_depth,
    max_top_level_comments,
    max_replies_per_comment,
    current_depth=1
):
    """Fetches comments recursively, handling both top-level and nested comments."""
    comment_forest.replace_more(limit=0)
    comments_data = []

    for comment in comment_forest[:max_top_level_comments]:
        if isinstance(comment, praw.models.MoreComments):
            continue

        comment_data = {
            'response_id': comment.id,
            'author': str(comment.author) if comment.author else None,
            'body': comment.body if comment.body else None,
            'upvote_score': comment.score,
            'created_utc': comment.created_utc,
            'replies': []
        }

        if current_depth < max_depth:
            comment_data['replies'] = fetch_comments(
                comment.replies,  # Recurse for nested replies
                max_depth,
                max_replies_per_comment,
                max_replies_per_comment,
                current_depth + 1
            )

        comments_data.append(comment_data)

    return comments_data