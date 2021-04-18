import sqlite3

# Import Libraries - Twitter
from textblob import TextBlob
import sys
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import pycountry
import random
import re
import string
from PIL import Image
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer

def query_yelp_db(db,location,**kwargs):
    query = "SELECT * from business WHERE city='" +location+"'"
    activity_synonyms = {'tours':['Beer Tours','Architectural Tours', 'ATV Tours', 'Food Tours','Wine Tours', 'Art Tours'],
                         'drink':['Bistros', 'Beer Bar', 'Brewpubs', 'Bartenders', 'Bars', 
                         'Whiskey Bars','Wine Tasting Room', 'Wine Tours', 'Wineries'],
                         'relax':['Massage', 'Ski Resorts', 'Hot Springs', 'Scuba Diving', 'Boating', 'Kayaking/Rafting', 'Meditation Centers'],
                         'exploring':['Bike Rentals', 'Local Flavor', 'Souvenir Shops', 'Kayaking', 'Traditional Clothing', 'Nightlife'],
                         'adventurous':['Skydiving','Kickboxing', 'Rafting', 'Horseback Riding', 'Skiing', 'Mountain Biking',
                         'Racing Experience', 'Paragliding', 'Surfing', 'Rock Climbing',
                         'Snorkeling', 'Hydro-jetting', 'Free Diving']
                         }
    cuisine = kwargs.get('cuisine')
    activities = kwargs.get('activity') #ANDing these
    ambience = kwargs.get('ambience') #NOT A COLUMN
    outdoor_seating = kwargs.get('outdoor_seating')

    if activities:
        if 'Restaurants' not in activities:
            cuisine = None
            ambience = None
            outdoor_seating = None

        for i in range(len(activities)):
            if activities[i] in activity_synonyms:
                activities[i] = activity_synonyms[activities[i]] #ORing activities
    
    age_allowed = kwargs.get('age_allowed')
    noise_level = kwargs.get('noise_level')
    accept_credit_card = kwargs.get('accept_credit_card')
    price_range = kwargs.get('price_range')
    wifi = kwargs.get('wifi')

    if outdoor_seating:
        query += " AND OutdoorSeating = 'True'"
    if age_allowed == 'adult':
        query += " AND (AgesAllowed = 'u'18plus'' OR AgesAllowed = 'u'19plus'' OR AgesAllowed = 'u'21plus'')"
    if noise_level=='quiet':
        query += " AND (NoiseLevel = 'u'quiet'' OR NoiseLevel = 'quiet')"
    if noise_level=='loud':
        query += " AND (NoiseLevel = 'u'loud'' OR NoiseLevel = ''loud'' OR NoiseLevel = 'u'very_loud'' OR NoiseLevel = ''very_loud'')"
    if accept_credit_card:
        query += " AND BusinessAcceptsCreditCards = 'True'"
    if price_range == 'low price':
        query += " AND RestaurantsPriceRange2 = '1'"
    if price_range == 'medium price':
        query += " AND RestaurantsPriceRange2 = '2'"
    if price_range == 'high price':
        query += " AND RestaurantsPriceRange2 = '3'"
    if price_range == 'very high price':
        query += " AND RestaurantsPriceRange2 = '4'"
    if wifi ==  'free wifi':
        query += " AND (WiFi = 'u'free'' OR WiFi =  ''free'')"
    if wifi ==  'no wifi':
        query += " AND (WiFi = 'u'no'' OR WiFi =  ''no'')"

    query += ' ORDER BY stars DESC, review_count DESC'

    print(query,activities,cuisine)
    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()

    if rows == []:
        return "No businesses match the search"
    
    new_rows = []
    for row in rows:
        #cat: 12, Amb: 24
        if activities:
            for activity in activities:
                if isinstance(activity,str) and activity in row[12]:
                    if cuisine: 
                        if cuisine in row[12]:    
                            if ambience:
                                ambs = row[24]
                                if ambs[0] == '{':
                                    ambs = eval(ambs)
                                else:
                                    ambs = None
                                if ambs:
                                    if ambs[ambience]:
                                        new_rows.append(row)
                                        break
                            else:
                                new_rows.append(row)
                    else:
                        new_rows.append(row)
                        break
                elif isinstance(activity,list):
                    for a in activity:
                        if a in row[12]:
                            new_rows.append(row)
                            break
        else:
            return rows[:5]
    return list(new_rows)[:5]

#Sentiment Analysis
def _percentage(part,whole):
    return 100 * float(part)/float(whole)

def analyze_tweets(keywords,noOfTweet,api):
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

        positive = _percentage(positive, noOfTweet)
        negative = _percentage(negative, noOfTweet)
        neutral = _percentage(neutral, noOfTweet)
        polarity = _percentage(polarity, noOfTweet)
        rank[keyword] = positive
        positive = format(positive, '.1f')
        negative = format(negative, '.1f')
        neutral = format(neutral, '.1f')

        #Number of Tweets (Total, Positive, Negative, Neutral)
        tweet_list = pd.DataFrame(tweet_list)
        neutral_list = pd.DataFrame(neutral_list)
        negative_list = pd.DataFrame(negative_list)
        positive_list = pd.DataFrame(positive_list)
        """print("Total number of tweets analyzed: ",len(tweet_list))
        print("Positive percentage: ",positive,"% and total Positive tweets: ",len(positive_list))
        print("Negative percentage: ",negative,"% and total Negative tweets: ",len(negative_list))
        print("Neutral percentage: ",neutral,"% and total Neutral tweets: ",len(neutral_list))
        print("\n\nSome Positive tweets:")
        #positive_list.set_option('display.width', None)
        print(positive_list.head())
        print("\n\nNegative tweets:")
        print(negative_list.head())"""
        
    sorted_rank = dict(sorted(rank.items(), key=lambda item: -item[1]))
    return list(sorted_rank.keys())


if __name__ == '__main__':
    conn = sqlite3.connect('datasets/Yelp.db')

    for row in query_yelp_db(conn,'Boulder',activity=['Restaurants'],cuisine='Mexican',outdoor_seating=True):
        print(row)
        break
            

