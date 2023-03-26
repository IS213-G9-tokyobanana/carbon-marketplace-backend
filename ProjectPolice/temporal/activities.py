from temporalio import activity
import pika
import requests

# add the path to the main directory of your project to the system path
from ProjectPolice.police import format_message, format_url, publish_to_notifier
from ProjectPolice.config.config import PAYMENT_MS_URL, RMQHOSTNAME, RMQPORT, RMQUSERNAME, RMQPASSWORD

# Request to Project Microservice to remove reserved offset
@activity.defn
async def remove_reserved_offset(data) -> dict:
    # milestone_id = data["data"]["milestone_id"]
    # project_id = data["data"]["project_id"]
    # payload = format_message(milestone_id, project_id, data["data"])
    # url = format_url(project_id, milestone_id, "offset")

    # # Send request to Project Microservice
    # try:
    #     result = requests.delete(url, json=payload)
    #     result.raise_for_status()
    # except requests.exceptions.HTTPError as err:
    #     result = {
    #         "code": 500,
    #         "message": "invocation of service fails: " + url + ". " + str(err),
    #     }
    # return result
    return {"code": 200, "message": "reserved offset removed"}


# Request to Payment Microservice to retrieve relevant payment intent
@activity.defn
async def get_payment_intent() -> dict:
    # try:
    #     result = requests.get(PAYMENT_MS_URL)
    #     result.raise_for_status()
    # except requests.exceptions.HTTPError as err:
    #     result = {
    #         "code": 500,
    #         "message": "invocation of service fails: "
    #         + PAYMENT_MS_URL
    #         + ". "
    #         + str(err),
    #     }
    # return result
    return {"code": 200, "message": "payment intent retrieved"}


# Request to Messgae Broker to send message to Notifier
@activity.defn
async def send_to_notifier(data) -> dict:
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    result = publish_to_notifier(data, channel)
    return result
