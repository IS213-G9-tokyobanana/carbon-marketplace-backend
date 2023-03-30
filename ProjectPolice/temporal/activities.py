from temporalio import activity
import pika
import requests

# add the path to the main directory of your project to the system path
from police import format_message, format_url, publish_to_notifier
from config.config import (
    PROJECT_OFFSET_URL,
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
    PAYMENT_MS_URL,
)

# Request to Project Microservice to remove reserved offset
@activity.defn
async def remove_reserved_offset(data) -> dict:
    # milestone_id = data["data"]["milestone_id"]
    # project_id = data["data"]["project_id"]
    # payload = format_message(milestone_id, "remove_reserved_offset", data["data"])
    # url = format_url(PROJECT_OFFSET_URL, project_id, milestone_id)

    # # Send request to Project Microservice
    # try:
    #     result = requests.delete(url, json=payload)
    #     result.raise_for_status()
    # except requests.exceptions.HTTPError as err:
    #     result = {
    #         "success": False,
    #         "data": {
    #             "message": "invocation of service fails: " + url + ". " + str(err),
    #         },
    #     }
    # return result
    return {
        "success": True,
        "data": {
            "message": "Example test message from remove_reserved_offset",
        },
    }


# Request to Payment Microservice to retrieve relevant payment intent
@activity.defn
async def get_buyer_id(data) -> dict:
    # payment_id = data["data"]["payment_id"]
    # try:
    #     result = requests.get(f"{PAYMENT_MS_URL}/payment/{payment_id}")
    #     result.raise_for_status()
    # except requests.exceptions.HTTPError as err:
    #     result = {
    #         "success": False,
    #         "data": {
    #             "message": f"invocation of service fails: {PAYMENT_MS_URL}. {str(err)}"
    #         },
    #     }
    # return result
    return {
        "success": True,
        "data": {"message": "Example test message from get_buyer_id"},
    }


# Request to Messgae Broker to send message to Notifier
@activity.defn
async def send_to_notifier(data, buyer_id) -> dict:
    # data["data"]["buyer_id"] = buyer_id
    # parameters = pika.ConnectionParameters(
    #     host=RMQHOSTNAME,
    #     port=RMQPORT,
    #     heartbeat=3600,
    #     credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
    #     blocked_connection_timeout=3600,
    # )
    # connection = pika.BlockingConnection(parameters=parameters)
    # channel = connection.channel()
    # result = publish_to_notifier(data, channel)
    return {
        "success": True,
        "data": {"message": "Example test message from send_to_notifier"},
    }
