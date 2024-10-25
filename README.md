# Data Science - Social Media Trends Tracker

## Project Overview

Complete end-to-end, full-stack data application. Scrapes social media posts daily using PRAW (Python Reddit API Wrapper), stores the data in PostgreSQL as JSONB, processes and analyzes the data using a combination of Python (NLP/ML) and dbt, and finally visualizes the trends and insights through a dashboard. This system helps in understanding time series social media trends regarding general sentiment, mental health, extremism, and hate speech.

A second API was also created to extract reddit data as a csv file for easy conjunction with current LLM capabilities.

### [ERD and Date Pipeline Overview (click for fully-detailed pdf):](./assets/ERD-Data-Pipeline-and-Transformations.pdf)

<a href="./assets/ERD-Data-Pipeline-and-Transformations.pdf">
    <img src="/assets/ERD-Data-Pipeline-and-Transformations-slide1.png" alt="Presentation Thumbnail" width="900">
</a>

## Key Features

- **Data Extraction**: Utilizes Python/PRAW to fetch posts from specified subreddits.
- **Data Storage**: Stores the raw and transformed data in PostgreSQL.
- **Data Processing**: Processes and transforms the data using Python and dbt.
- **Data Analysis**: Performs text analysis on the posts using NLP and ML techniques to extract meaningful insights.
- **Visualization**: Provides a dashboard to visualize the trends and data points, making the insights accessible to users.

## Key Tools/Technologies Used

- **PRAW**: For extracting data from Reddit.
- **PostgreSQL**: For storing processed, time series results data.
- **Python 3.12**: Primary programming language for scripting and analysis. See requirements.txt for all package/library versions.
- **Dagster**: For orchestrating the data pipeline.
- **dbt**: For transforming data stored in PostgreSQL.
- **Docker**: For containerization of the application.

## Setup
1) Git clone the project repo
2) Open cmd terminal, navigate to project folder, (optionally set up a virtual environment with python -m venv .venv), and run pip install -r requirements.txt.
3) Configure environment variables:
  a) PRAW (for extracting reddit data): PRAW_CLIENT_ID, PRAW_CLIENT_SECRET, and PRAW_USER_AGENT
  b) (Optional) Database: If using any of the database APIs, configure either local db variables (LOCAL_DB_NAME, LOCAL_DB_USER, and LOCAL_DB_PASSWORD) or cloud/AWS db variables (currently these are AWS_DB_ENDPOINT, AWS_DB_NAME, AWS_DB_USER, and AWS_DB_PASSWORD). If only using an API that does not interface with a database, this setup step is not needed.
4) (Optional) Fill out the file src/extract/subreddit_list.txt with the list of subreddits to extract data from.
5) Run main.py (extract data to database) or main_lite.py (extract data to .csv) to execute with default extraction parameters. If desired, extraction parameters (num_posts, max_depth, etc.) can be updated to modify how much data is extracted from each subreddit.

## Development

### Project Folder Structure
- **/assets**: Documentation files.
- **/dagster**
  - **/jobs**: Contains Dagster jobs for data pipelines.
  - **/solids**: Individual solids for building Dagster pipelines (ex: one handling data, one handling transformation, etc.).
  - **/resources**: Configurations and utilities (db connections).
  - **/schedules**: Pipeline scheduling.
- **/sandbox**: Jupyter Notebooks for data exploration and early scripting.
- **/src**
  - **/content_analysis**: NLP and machine learning scripts. Will likely have subfolders to manage different text analysis methods, including folder structure for developing and implementing ML models. One such text analysis method is an ML model using this mental health dataset: https://www.kaggle.com/code/swathiunnikrishnan/mental-health-analysis-using-nlp
  - **/extract**: PRAW data extraction.
  - **/load**: Loading to database(s).
  - **/reports_and_viz**: Dashboard, reports, and visualization scripts.
  - **/transform**
    - **/dbt**: Transformations using dbt.
  - **main.py**: Primary entrypoint/API for this project.
  - **main_lite.py**: Second entrypoint/API for this project. Extracts data as a .csv file. No database interfacing.
- **/tests**


### Recursive Weight-Decay Algorithm to Aggregate Subreddit Sentiment

The data pipeline extracts the top posts for selected, tracked subreddits daily. Each post can be thought of as a tree, where there is a root node (post title + text), which branches to the 2nd-layer of nodes (comments), each branching to a 3rd-layer (top-level replies to each comment), and so on. Text-analysis can be performed on each submission (the term "submission" encompassing any user content, including posts, comments, and replies), however the deeper the tree is traversed, each submission is considered less and less significant, and therefore less representative of the entire subreddit on that day. Therefore, a node-weighting approach is used in order to aggregate all of the submissions' text-analysis scores into a single comprehensive score representing that entire subreddit on that specific day. The current model includes a recursive, tree-traversal algorithm that has a decay in node weight with each branch traversal.

Furthermore, submissions have upvotes and downvotes representing user engagement, which can also be incorporated into the model. The decay in node weight is therefore dynamically calculated based on the difference in |node1 upvotes| and |node2 upvotes|, with a logarithmic dampening function likely being utilized to calculate the exact decay.

decay rate = log(|node1_upvotes|) / log(node2_upvotes|), with a minimum decay rate of perhaps 5-10% also likely to utilized

Ex: If a post has 7,000 upvotes, and one of its comments has 700 upvotes, then the decay rate would be calculated as log(7,000)/log(700) = 1.35, so the weighting of the comment's text-analysis score would be 74% (1/1.35) of the post's text-analysis score.

The original design intent was to implement this decay during extraction so that when the rate lowered beneath a certain threshold, the recursion would end for that branch of the tree. All trees would be explored using this approach, with each tree also being weighted in relation to the |upvotes| of the top tree's root node. All scores would then be aggregated during this approach, then finally a score given to the whole forest, representing a subreddit's score for that day in that text-analysis area. **However, this approach was modified so that the data would first be extracted and loaded to the database, then later in the pipeline the decay weighting algorithm be applied. This ELT (vs ETL) approach was chosen in order to retain the raw data in case analysis methods changed later in development.**

### Extraction using PRAW

PRAW is used to extract the top 10 (within past 24 hours) posts from 25 different subreddits every day (orchestrated using Dagster). The posts are recursively parsed, then saved/loaded as JSONB in PostgreSQL. Heavily trafficked posts, such as those in extremely popular subreddits, are also capped in tree height and width to manage file size. Parameters were implemented in the recursive extraction algorithm to impose the below limits.

Default extraction parameters:
  - time_filter='day',
  - num_posts=10,
  - max_depth=3,
  - max_top_level_comments=5,
  - max_replies_per_comment=2

This still allowed for analysis of the top (up to) 9,000 submissions each day across the chosen subreddits (25 subreddits * 10 posts * (1 post + 5 comments + 10 replies + 20 replies) = **9,000 submissions extracted daily**), which was considered adequate to maintain sentiment capture in each post and subreddit, while lowering file sizes from 100-400kb to 5-15kb, enabling a more scalable long-term storage solution.
