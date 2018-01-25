#!/usr/bin/env python3
import json
import tweepy
from tweepy.streaming import StreamListener
from textblob import TextBlob
from tweepy import OAuthHandler
from tweepy import Stream

from twitter_keys import *
from main import *


def start_twitter_sentiment(bot):
    # this will take the tweets and run a sentiment analysis
    class StdOutListener(StreamListener):
        def on_data(self, data):
            all_data = json.loads(data)

            tweet = all_data["text"]
            print('\n')
            analysis = TextBlob(tweet)
            print(tweet)
            print('Polarity: ', analysis.sentiment.polarity)
            print('Subjectivity: ', analysis.sentiment.subjectivity)
            if bot:
                bot.signal_sentiment(analysis.sentiment.polarity, analysis.sentiment.subjectivity,
                                     SentimentSources.TWITTER)

        def on_error(self, status):
            print(status)

    # Connection to Twitter API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    # This line filter Twitter Streams to capture data by the keywords: 'bitcoin', 'ethereum', 'litecoin'
    stream.filter(track=['bitcoin', 'ethereum', 'litecoin'])


if __name__ == "__main__":
    start_twitter_sentiment(None)
