import requests
import pika
import json
from ProjectPolice.config.config import (
    EXCHANGE_NAME,
    POLICE_NOTIFY_ROUTING_KEY,
    PROJECT_STATUS_URL,
)


def format_url(pid, mid, task):
    return PROJECT_STATUS_URL.format(project_id=pid, milestone_id=mid, task=task)


# Function to format message before sending to Notifier / Project Microservice
def format_message(resource_id, type, data):
    new_data = {k: v for k, v in data.items() if k != "task_id"}
    return json.dumps({"resource_id": resource_id, "type": type, "data": new_data})


# Function to send message to Notifier
def publish_to_notifier(message, channel):
    milestoneid = message["data"]["milestone_id"]
    type = "milestone.upcoming"
    payload = format_message(milestoneid, type, message["data"])
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=POLICE_NOTIFY_ROUTING_KEY,
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    return {"code": 200, "message": "message sent to Notifier"}


# Function to send message to Project Microservice
def send_to_projectms(message):
    milestone_id = message["data"]["milestone_id"]
    project_id = message["data"]["project_id"]
    payload = format_message(milestone_id, project_id, message["data"])
    url = format_url(project_id, milestone_id, "penalise")

    # Send request to Project Microservice
    try:
        result = requests.patch(url, json=payload)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "code": 500,
            "message": "invocation of service fails: " + url + ". " + str(err),
        }
    return result
