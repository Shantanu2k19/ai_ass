from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = "localhost"  # Replace with broker IP when ready
MQTT_PORT = 1883

class ActionTurnOnLights(Action):
    def name(self) -> str:
        return "action_turn_on_lights"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        dispatcher.utter_message(text="Lights turned on (simulation).")

        # try:
        #     client = mqtt.Client()
        #     client.connect(MQTT_BROKER, MQTT_PORT, 60)
        #     client.publish("home/lights", "ON")
        #     client.disconnect()
        #     dispatcher.utter_message(text="Lights turned on (simulation).")
        # except Exception as e:
        #     dispatcher.utter_message(text=f"Error turning on lights: {str(e)}")

        return []


class ActionFetchWeather(Action):
    def name(self) -> str:
        return "action_fetch_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        dispatcher.utter_message(text="weater triggered lol")

        # try:
        #     url = "http://api.weatherapi.com/v1/current.json"
        #     params = {
        #         "key": "YOUR_KEY",  # Replace with your API key
        #         "q": "YOUR_LOCATION"
        #     }
        #     response = requests.get(url, params=params)
        #     response.raise_for_status()
        #     weather = response.json()
        #     dispatcher.utter_message(text=f"The weather is {weather['current']['condition']['text']}")
        # except Exception as e:
        #     dispatcher.utter_message(text=f"Error fetching weather: {str(e)}")

        return []




class ActionDefault(Action):
    def name(self) -> str:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        dispatcher.utter_message(text="Default")
        return []