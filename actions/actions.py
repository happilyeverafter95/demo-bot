import json
from typing import Any, Dict, List, Optional, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction, Restarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher


def select_laptop(price: int, platform: Optional[str], purpose: Optional[str],
                  brand: Optional[List[str]]) -> List[Dict[str, str]]:
    with open('actions/laptops.json') as f:
        laptops = json.load(f)
    laptops = [x for x in laptops if x['price'] <= price]
    if platform and 'no preference' not in platform:
        laptops = [x for x in laptops if x['platform'] == platform]
    if purpose:
        laptops = [x for x in laptops if x['purpose'] == purpose]
    if brand and 'no preference' not in brand:
        laptops = [x for x in laptops if x['brand'] in brand]
    return laptops


class ActionGreet(Action):
    def name(self) -> Text:
        return 'action_greet'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template='utter_greet')
        dispatcher.utter_message(template='utter_price')
        return []


class ActionSelectPrice(Action):
    def name(self) -> Text:
        return 'action_select_upper_price'

    def validate_price(self, message: str) -> bool:
        numerical_values = [int(s) for s in message.split() if s.isdigit()]
        return len(numerical_values) >= 1

    def extract_price(self, message: str) -> int:
        # TODO: dedup methods
        numerical_values = [int(s) for s in message.split() if s.isdigit()]
        if len(numerical_values) >= 1:
            return numerical_values[0]
        else:
            return -1

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        upper_price = tracker.latest_message['text']
        if self.validate_price(upper_price):
            extracted_price = self.extract_price(upper_price)
            dispatcher.utter_message(text=f'I will look for a laptop under ${upper_price}.')
            dispatcher.utter_message(template='utter_purpose')
            return [SlotSet('upper_price', extracted_price)]
        else:
            dispatcher.utter_message(template='utter_default')
            return []


class ActionSelectPlatform(Action):
    def name(self) -> Text:
        return 'action_select_platform'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        platform = tracker.slots['platform']
        dispatcher.utter_message(template='utter_ask_other_requirements')
        return [SlotSet('platform', platform), FollowupAction('action_recommend_laptop')]


class ActionSelectBrand(Action):
    def name(self) -> Text:
        return 'action_select_brand'

    def reformat_brands(self, message: str) -> List[str]:
        return [x.strip() for x in message.split(',')]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        brands = tracker.latest_message['text']
        dispatcher.utter_message(template='utter_platform')
        if brands.lower().strip() != 'no preference':
            return [SlotSet('brand', self.reformat_brands(brands))]
        return [SlotSet('brand', [])]


class ActionSelectPurpose(Action):
    def name(self) -> Text:
        return 'action_select_purpose'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        purpose = tracker.slots['purpose']
        dispatcher.utter_message(template='utter_brand')
        return [SlotSet('purpose', purpose)]


class ActionRecommendLaptop(Action):
    def name(self) -> Text:
        return 'action_recommend_laptop'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        laptops = select_laptop(tracker.slots['upper_price'], tracker.slots['platform'],
                                tracker.slots['purpose'], tracker.slots['brand'])
        if laptops == []:
            dispatcher.utter_message(template='utter_no_recommendations')
        else:
            dispatcher.utter_message(text=f'I have a few recommendations for you.')
            for laptop in laptops[:3]:
                dispatcher.utter_message(
                    text=f'{laptop["name"]} (${laptop["price"]})-- {laptop["description"]}.')
        return []


class ActionGoodbye(Action):
    def name(self) -> Text:
        return 'action_goodbye'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template='utter_goodbye')
        return [Restarted()]
