import json

import pika
from config.config import EXCHANGE_NAME, RMQHOSTNAME, RMQPASSWORD, RMQPORT, RMQUSERNAME


# Function to format message before sending to Notifier / Project Microservice
def format_message(resource_id, type, data):
    new_data = {k: v for k, v in data.items() if k != "task_id"}
    return json.dumps({"resource_id": resource_id, "type": type, "data": new_data})


def get_connection():
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    return pika.BlockingConnection(parameters=parameters)


# Function to send message to Notifier
def publish_to_notifier(channel, message, routing_key):
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    return {
        "success": True,
        "data": {
            "message": "message sent to Notifier",
            "resource": message,
        },
    }
