from typing import Text, List, Dict, Any, Union, Optional

from rasa_sdk import Action, Tracker, ActionExecutionRejection

from rasa_sdk.forms import FormAction, REQUESTED_SLOT, Form

from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, AllSlotsReset, FollowupAction

from rasa.core.events import Event

from rasa_sdk.executor import CollectingDispatcher

import re
from datetime import datetime
import sqlite3
import tweepy

from .utils import query_yelp_db,analyze_tweets,query_yelp_db_2

conn = sqlite3.connect('datasets/Yelp.db')

# Authentication
consumerKey = "nFu2HqrelkEiax0L5Lh4Sw"
consumerSecret = "6OUaIfj0ECfeJD24CVlDrcc1qqajnHBgsB7b6RPmvA"
accessToken = "1193875656-G3iatRJ18tCCFTf8x06kV5B6XwdWbja4S4DVXDL"
accessTokenSecret = "IGOxuEQYeTREpGkL4F5LkdYNxUPLFo0zBjX3Yfdg8g"

try:
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    twitter_api = tweepy.API(auth)
    print(twitter_api)
except:
    print("Error: Authentication Failed")

class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:
        dispatcher.utter_message("Hey, How may I help you?")

class ActionGuide(Action):
    def name(self) -> Text:
        return "action_guide"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:

        currLoc = None #Replace with func to get current location
        location = next(tracker.get_latest_entity_values('loc'),currLoc)
        activity = next(tracker.get_latest_entity_values('activity'),None)
        cuisine =  next(tracker.get_latest_entity_values('cuisine'),None)
        ambience =  next(tracker.get_latest_entity_values('ambience'),None)
        outdoor_seating = next(tracker.get_latest_entity_values('outdoor_seating'),None)
        age_allowed = next(tracker.get_latest_entity_values('age_allowed'),None)
        noise_level = next(tracker.get_latest_entity_values('noise_level'),None)
        accept_credit_card = next(tracker.get_latest_entity_values('accept_credit_card'),None)
        price_range = next(tracker.get_latest_entity_values('price_range'),None)
        wifi = next(tracker.get_latest_entity_values('wifi'),None)

        if isinstance(activity,str):
            activity = [activity]
        
        rows = query_yelp_db_2(conn,location,activity=activity,cuisine=cuisine,
        ambience=ambience,outdoor_seating=outdoor_seating,age_allowed=age_allowed,noise_level=noise_level,
        accept_credit_card=accept_credit_card,price_range=price_range,wifi=wifi)

        if isinstance(rows,list):
            new_rows = []
            for i,rowj in enumerate((analyze_tweets([row[2] for row in rows],10,twitter_api))):
                for row in rows:
                    if rowj in row:
                        new_rows.append(str(i+1) + ": " + rowj + '<br>Tip: ' + row[-1])

            dispatcher.utter_message('<br><br>'.join(new_rows))
        else:
            dispatcher.utter_message(rows)
        for row in rows:
            print(row[2],row[9],row[10])

class ActionTravel(Action):
    def name(self) -> Text:
        return 'action_travel'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:

        currLoc = None #Replace with func to get current location
        source = next(tracker.get_latest_entity_values('loc'),currLoc)
        destination = next(tracker.get_latest_entity_values('loc'),None)


class ActionFacts(Action):
    def name(self) -> Text:
        return 'action_facts'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:

        currLoc = None #Replace with func to get current location
        location = next(tracker.get_latest_entity_values('loc'),currLoc)

class ActionSafe(Action):
    def name(self) -> Text:
        return 'action_safe'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:

        currLoc = None #Replace with func to get current location
        location = next(tracker.get_latest_entity_values('loc'),currLoc)

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"
    
    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:
        dispatcher.utter_message("Sorry I did not understand you, please rephrase the sentence or type restart to restart this session")

"""
Unrequired
class ActionStop(Action):
    def name(self) -> Text:
        return "action_stop"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text,Any],
        ) -> List[Dict]:
        current_form = tracker.active_form
        print(current_form)
        if current_form != None and current_form != {}:
            dispatcher.utter_message(template='utter_ask_continue')
        else:
            dispatcher.utter_message("There is nothing to stop!")
"""