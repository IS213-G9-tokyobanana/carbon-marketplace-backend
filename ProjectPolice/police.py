import requests
import pika
import json
from config.config import EXCHANGE_NAME, POLICE_NOTIFY_ROUTING_KEY

# Function to format message before sending to Notifier / Project Microservice
def format_message(resource_id, type, data):
    if data is None:
        new_data = {}
    else:
        keys = ["projectid", "milestoneid"]
        new_data = {x: data[x] for x in keys}
    return json.dumps({"resource_id": resource_id, "type": type, "data": new_data})


# Function to send message to Notifier
def publish_to_notifier(message, channel):
    milestoneid = message["data"]["milestoneid"]
    type = "milestone.upcoming"
    payload = format_message(milestoneid, type, message["data"])
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=POLICE_NOTIFY_ROUTING_KEY,
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2),
    )


# Function to send message to Project Microservice
def send_to_projectms(message):
    milestoneid = message["data"]["milestoneid"]
    projectid = message["data"]["projectid"]
    payload = format_message(milestoneid, projectid, message["data"])
    URL = f"http://localhost:5000/project/{projectid}/milestone/{milestoneid}/penalise"

    # Send request to Project Microservice
    try:
        res = requests.post(URL, json=payload)
    except requests.exceptions.HTTPError as err:
        result = {
            "code": 500,
            "message": "invocation of service fails: " + URL + ". " + str(err),
        }

    # Check if request is successful
    if code not in range(200, 300):
        return result
    if res.status_code != requests.codes.ok:
        code = res.status_code
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
    except Exception as err:
        result = {
            "code": 500,
            "message": "Invalid JSON output from service: " + URL + ". " + str(err),
        }
