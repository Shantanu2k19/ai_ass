import paho.mqtt.client as mqtt

import os 
from dotenv import load_dotenv 
load_dotenv()
from mqtt_topics import MQTT_TOPIC_LIST

# MQTT broker details
broker = os.getenv("MQTT_BROKER")
port = 1883
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")

topics = {}
for x in MQTT_TOPIC_LIST:
    topics[x]="OFF"

# Create client instance
client = mqtt.Client()

# If using authentication
client.username_pw_set(username, password)

# Connect to broker
client.connect(broker, port, keepalive=60)

# Publish a message
for topic, message in topics.items():
    client.publish(topic, message)
    print(f"Published '{message}' to topic '{topic}'")


# Disconnect
client.disconnect()
