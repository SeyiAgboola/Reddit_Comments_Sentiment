# Extract Reddit Comments and Perform Sentimental Analysis

This repo allows you to collect reddit comments and perform sentimental analysis on them.

There's 3 stages to this document:
* extract_submissions_via_search.py - Search within specific subreddit for keyword(s) and save metadata to file
* extract_submission_comments.py - Extract reddit comments for IDs provided via file
* sentiment_build_allcomms.py - Calculate Sentiment Scores on every comment and save to file

You will need PRAW API key to access Reddit's metadata with this code.

If you wish for full details of how the code works, see my blog below:

* [Basics of Data Extraction of Reddit Threads using Python](https://rareloot.medium.com/basics-of-data-extraction-of-reddit-threads-using-python-c96854c41344)


