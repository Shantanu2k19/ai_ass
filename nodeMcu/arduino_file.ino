#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "192.168.1.10"; # rpi ip

WiFiClient espClient;
PubSubClient client(espClient);
const int relayPin = D1;

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) message += (char)payload[i];

  if (message == "ON")  digitalWrite(relayPin, LOW);
  if (message == "OFF") digitalWrite(relayPin, HIGH);
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("NodeMCU1")) client.subscribe("home/livingroom/light");
    else delay(5000);
  }
}

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}
