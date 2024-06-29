import praw

from transform.process_praw_trees.praw_tree import process_praw_tree


def process_praw_forest(posts):

    posts = [] # Import all posts from MongoDB for a specific subreddit and specific day
    tree_sentiment_scores, tree_engagement_scores = [], []
    total_forest_sentiment_score = 0
    # total_forest_mental_health_score = 0 # Planned as later feature

    for post in posts:
        tree_engagement_score, tree_sentiment_score,  = process_praw_tree(post)
        tree_sentiment_scores.append(tree_sentiment_score)
        tree_engagement_scores.append(tree_engagement_score)
        total_forest_sentiment_score += tree_sentiment_score * tree_engagement_score

    forest_engagement_score = sum(tree_engagement_scores)
    forest_sentiment_score = total_forest_sentiment_score / forest_engagement_score
    # forest_mental_health_score = total_forest_mental_health_score / forest_engagement_score # Planned feature

    return forest_engagement_score, forest_sentiment_score # forest_mental_health_score