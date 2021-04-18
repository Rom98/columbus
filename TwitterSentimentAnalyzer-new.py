# Import Libraries
from textblob import TextBlob
import sys
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import pycountry
import re
import string
from PIL import Image
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer

# Authentication
consumerKey = "nFu2HqrelkEiax0L5Lh4Sw"
consumerSecret = "6OUaIfj0ECfeJD24CVlDrcc1qqajnHBgsB7b6RPmvA"
accessToken = "1193875656-G3iatRJ18tCCFTf8x06kV5B6XwdWbja4S4DVXDL"
accessTokenSecret = "IGOxuEQYeTREpGkL4F5LkdYNxUPLFo0zBjX3Yfdg8g"

try:
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)
except:
    print("Error: Authentication Failed")
    
#Sentiment Analysis
def percentage(part,whole):
    return 100 * float(part)/float(whole)

def analyze(keywords,noOfTweet):
    rank = {}
    for keyword in keywords:
        #print("\nCurrent keyword:",keyword)
        tweets = tweepy.Cursor(api.search, q=keyword).items(noOfTweet)
        positive = 0
        negative = 0
        neutral = 0
        polarity = 0
        tweet_list = []
        neutral_list = []
        negative_list = []
        positive_list = []

        for tweet in tweets:
         
            #print(tweet.text)
            tweet_list.append(tweet.text)
            analysis = TextBlob(tweet.text)
            score = SentimentIntensityAnalyzer().polarity_scores(tweet.text)
            neg = score['neg']
            neu = score['neu']
            pos = score['pos']
            comp = score['compound']
            polarity += analysis.sentiment.polarity

            if neg > pos:
                negative_list.append(tweet.text)
                negative += 1
            elif pos > neg:
                positive_list.append(tweet.text)
                positive += 1
            elif pos == neg:
                neutral_list.append(tweet.text)
                neutral += 1

        positive = percentage(positive, noOfTweet)
        negative = percentage(negative, noOfTweet)
        neutral = percentage(neutral, noOfTweet)
        polarity = percentage(polarity, noOfTweet)
        rank[keyword] = positive
        positive = format(positive, '.1f')
        negative = format(negative, '.1f')
        neutral = format(neutral, '.1f')

        #Number of Tweets (Total, Positive, Negative, Neutral)
        tweet_list = pd.DataFrame(tweet_list)
        neutral_list = pd.DataFrame(neutral_list)
        negative_list = pd.DataFrame(negative_list)
        positive_list = pd.DataFrame(positive_list)
        #print("Total number of tweets analyzed: ",len(tweet_list))
        #print("Positive percentage: ",positive,"% and total Positive tweets: ",len(positive_list))
        #print("Negative percentage: ",negative,"% and total Negative tweets: ",len(negative_list))
        #print("Neutral percentage: ",neutral,"% and total Neutral tweets: ",len(neutral_list))
        #print("\n\nSome Positive tweets:")
        #positive_list.set_option('display.width', None)
        #print(positive_list.head())
        #print("\n\nNegative tweets:")
        #print(negative_list.head())
        
    sorted_rank = dict(sorted(rank.items(), key=lambda item: -item[1]))
    return list(sorted_rank.keys())
    
keywords = []
keyword_str = input("Please enter keywords or hashtags to search: ")
noOfTweet = int(input ("Please enter how many tweets to analyze: "))
rank = analyze(keyword_str.split(','),noOfTweet)
#print("\n***************RESULT*********************\n")
print(rank)

#Creating PieCart
#labels = ['Positive ['+str(positive)+'%]' , 'Neutral ['+str(neutral)+'%]','Negative ['+str(negative)+'%]']
#sizes = [positive, neutral, negative]
#colors = ['yellowgreen', 'blue','red']
#patches, texts = plt.pie(sizes,colors=colors, startangle=90)
#plt.style.use('default')
#plt.legend(labels)
#plt.title("Sentiment Analysis Result for keyword= "+keyword+"" )
#plt.axis('equal')
#plt.show()
