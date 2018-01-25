
# coding: utf-8

# In[13]:
import praw
import datetime
from textblob import TextBlob
from redditkeys import *
from main import *

relevant_subs = ('btc+ethereum+bitcoin+litecoin')

reddit = praw.Reddit(username = reddit_username, user_agent = user_agent_info,
                     client_id = reddit_api_id, client_secret = reddit_api_secret)


# Time format: (year, month, day, hour, minute, second, microsecond, and tzinfo)
# tzinfo: - accounts for timezone differences


def start_reddit_sentiment(bot):
    # Collects posts from selected subreddits' 'new' pages and runs a sentiment analysis.
    def new_submits(list_of_subs):
        subs_instance = reddit.subreddit(list_of_subs)
        def get_date(submission):
            time = submission.created
            return datetime.datetime.fromtimestamp(time)
        for submission in subs_instance.stream.submissions():
            reddit_data = TextBlob(submission.title + submission.selftext.replace('\n',' '))
            submit = submission.title + submission.selftext.replace('\n',' ')
            time = get_date(submission)

            print(submit + '\n')
            print('Polarity: ', reddit_data.sentiment.polarity)
            print('Subjectivity: ', reddit_data.sentiment.subjectivity)
            print('Time: ', str(time) + '\n')
        if bot:
                bot.signal_sentiment(reddit_data.polarity, reddit_data.subjectivity,
                                 SentimentSources.REDDIT)

    new_submits(relevant_subs)
    #  Returns the following:
    # "Post name" + "Post-text (if any)"
    # Polarity score (textblob) 
    # Subjectivity score (textblob) 
    # Date-time

if __name__ == '__main__': 
    start_reddit_sentiment(None)
