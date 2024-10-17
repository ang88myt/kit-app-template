import random
import json
import time
import requests
from paho.mqtt import client as mqtt_client

# Configuration constants
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'device/dev02'
HTTP_ENDPOINT = 'https://digital-twin.expangea.com/device/'
API_HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Content-Type': 'application/json'
}

# Generate random XYZ position
def generate_random_xyz_position() -> dict:
    return {
        'name': 'dev02',
        'position': {
            'x': random.uniform(-100, 100),
            'y': random.uniform(-100, 100),
            'z': 0
        }
    }

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

# MQTT on_publish callback
def on_publish(client, userdata, mid, properties=None):
    print(f"Message {mid} has been published successfully.")

# Publish position to MQTT
def publish_to_mqtt(client, position: dict):
    result = client.publish(MQTT_TOPIC, json.dumps(position))
    status = result.rc
    if status == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"Sent `{position}` to topic `{MQTT_TOPIC}`")
    else:
        print(f"Failed to send message to topic {MQTT_TOPIC}, return code {status}")

# Update position to HTTP endpoint
def update_to_http_endpoint(position: dict):
    try:
        response = requests.post(HTTP_ENDPOINT, headers=API_HEADERS, json=position)
        response.raise_for_status()
        print(f"Updated position to HTTP endpoint: {position}")
    except requests.RequestException as e:
        print(f"HTTP request error: {e}")

# Connect to MQTT broker
def connect_mqtt() -> mqtt_client.Client:
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,"client_id")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def main():
    client = connect_mqtt()
    client.loop_start()  # Start network loop
    while True:
        position = generate_random_xyz_position()
        publish_to_mqtt(client, position)
        update_to_http_endpoint(position)
        time.sleep(5)  # Adjust interval as needed

if __name__ == "__main__":
    main()