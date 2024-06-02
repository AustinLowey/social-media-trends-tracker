# Social Media Trends Tracker

## Project Overview

This project scrapes social media posts daily using PRAW (Python Reddit API Wrapper), stores the raw data in MongoDB, processes and analyzes the data using a combination of Python and dbt, stores the processed data in PostgreSQL, and finally visualizes the trends and insights through a dashboard. This system helps in understanding time series social media trends regarding general sentiment, mental health, extremism, and hate speech.

## Key Features

- **Data Extraction**: Utilizes PRAW to fetch posts from specified subreddits.
- **Data Storage**: Stores the raw data in MongoDB, a NoSQL database, and processed data in PostgreSQL.
- **Data Processing**: Processes and transforms the data using Python and dbt.
- **Data Analysis**: Performs text analysis on the posts using NLP and ML techniques to extract meaningful insights.
- **Visualization**: Provides a dashboard to visualize the trends and data points, making the insights accessible to users.

## Technologies Used

- **PRAW**: For extracting data from Reddit.
- **MongoDB**: For storing BSON PRAW data.
- **PostgreSQL**: For storing processed, time series results data.
- **Python 3.12**: Primary programming language for scripting and analysis.
- **Dagster**: For orchestrating the data pipeline.
- **dbt**: For transforming data stored in PostgreSQL.
- **Docker**: For containerization of the application.

## Development

### Project Folder Structure
- **/src**
  - **/extract**: Contains scripts for PRAW data extraction (may include additional sources over time).
  - **/load**
    - **/mongodb**: Loads data extracted using /extract modules into MongoDB.
    - **/postgres** Loads data processed using /transform modules into PostgreSQL.
  - **/transform**
    - **/dbt**: transformations with dbt
    - **/process_praw_trees**: Takes PRAW data from MongoDB, runs a decaying-weight, recursive tree algorithm while executing text models from /content_analysis.
  - **/content_analysis**: NLP and machine learning scripts. Will likely have subfolders to manage different text analysis methods, including folder structure for developing and implementing ML models. One such text analysis method is an ML model using this mental health dataset: https://www.kaggle.com/code/swathiunnikrishnan/mental-health-analysis-using-nlp
  - **/reports_and_viz**: Dashboard, reports, and visualization scripts.
- **/dagster**
  - **/jobs**: Contains Dagster jobs for data pipelines.
  - **/solids**: Individual solids for building Dagster pipelines (ex: one handling data, one handling transformation, etc.)
  - **/resources**: Configurations and utilities (db connections).
  - **/schedules**: Pipeline scheduling.
- **/sandbox**: Jupyter Notebooks for data exploration and early scripting.
- **/tests**
- **/assets**

### Recursive Weight-Decay Algorithm to Aggregate Subreddit Sentiment

The currently-planned approach for analyzing and aggregating subreddit sentiment is outlined below.

The data pipeline will extract the top x number of posts for selected, tracked subreddits daily. Each post can be thought of as a tree, where there is a root node (post title and text), which branches to the 2nd-layer of nodes (comments), which each branch to a 3rd-layer (top-level replies to comments), and so on. Text-analysis can be performed on each submission (the term "submission" encompassing any user content, including posts, comments, and replies), however the deeper the tree is traversed, each submission is considered less and less significant, and therefore less representative of the entire subreddit on that day. Therefore, a node-weighting approach is needed in order to aggregate all of these submissions' text-analysis scores into a comprehensive score representing that entire subreddit on that specific day. The current model includes a recursive, tree-traversal algorithm that has a decay in node weight with each branch traversal.

Furthermore, submissions have upvotes and downvotes representing user engagement, which can also be incorporated into the model. The decay in node weight is therefore dynamically calculated based on the difference in |node1 upvotes| and |node2 upvotes|, with a logarithmic dampening function likely being utilized to calculate the exact decay.

decay rate = log(|node1_upvotes|) / log(node2_upvotes|), with a minimum decay rate of perhaps 5-10% also likely to utilized

Ex: If a post has 7,000 upvotes, and one of its comments has 700 upvotes, then the decay rate would be calculated as log(7,000)/log(700) = 1.35, so the weighting of the comment's text-analysis score would be 74% (1/1.35) of the post's text-analysis score.

Once the decay rate lowers beneath a certain threshold, the recursion ends for that branch of the tree. All trees are explored using this approach, with each tree also being weighted in relation to the |upvotes| of the top tree's root node. All scores are aggregated during this approach, then finally a score is given to the whole forest, which is that subreddit's score for that day in that text-analysis area.

Prior to starting the forest exploration, 3 pointers are initialized:
1) submission_weight (based on decay rate and the previous node's submission_weight)
2) sentiment_score (this variable dependent on what type of text-analysis is being performed, as there are likely to be multiple that are explored for this project - i.e., sentiment score, mental health score, extremism score, etc.)
3) engagement_score (absolute value of upvotes)

With each node explored, the 3 pointers are updated:
submission_weight += node_submission_weight
sentiment_score += node_sentiment_score
engagement_score += |node_upvotes|

After the forest exploration is finished, the results are calculated.
subreddit_date_score = sum(submission_weight * sentiment_score) / sum(submission_weight)

The results, subreddit_date_score and engagement_score, are then stored in PostgreSQL.
