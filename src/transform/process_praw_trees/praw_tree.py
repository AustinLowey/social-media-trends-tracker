import praw

from content_analysis.mental_health_analysis import analyze_mental_health
from content_analysis.sentiment_analysis import analyze_sentiment

def process_praw_tree(post, decay_sensitivity):
    
    # Initialize variables to track totals across 
    total_tree_submission_weight = 0
    total_tree_sentiment_score = 0
    # total_tree_mental_health_score = 0 # Planned as later feature
    tree_engagement_score = 0


    # Recurse through tree
    # Calculate decay based on upvotes/downvotes of the 2 nodes
    # Call a selected (or multiple) text-analysis function(s) (sentiment, mental health, etc) and return a score(s)
    # Increment the total_tree_* variables

    tree_sentiment_score = total_tree_sentiment_score / total_tree_submission_weight
    # tree_mental_health_score = total_tree_mental_health_score / total_tree_submission_weight # Planned feature

    return tree_engagement_score, tree_sentiment_score # tree_mental_health_score