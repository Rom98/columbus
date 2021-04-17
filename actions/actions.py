from typing import Text, List, Dict, Any, Union, Optional

from rasa_sdk import Action, Tracker, ActionExecutionRejection

from rasa_sdk.forms import FormAction, REQUESTED_SLOT, Form

from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, AllSlotsReset, FollowupAction

from rasa.core.events import Event

from rasa_sdk.executor import CollectingDispatcher

import re
from datetime import datetime

from .utils import dummy

form_intents_actions = {'dth_Recharge':'dth_form',}

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
        outdoor_seating = next(tracker.get_latest_entity_values('outdoor_seating'),None)

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