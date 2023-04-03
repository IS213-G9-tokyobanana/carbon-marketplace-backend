from temporalio import activity
import pika
import requests

from config.config import (
    PAYMENT_MS_URL,
    PROJECT_OFFSET_URL,
    USER_MS_URL,
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
    EXCHANGE_NAME,
    PAYMENT_STATUS_ROUTING_KEY,
)


def format_url(url, pid, mid):
    return url.format(project_id=pid, milestone_id=mid)


# Request to Payment MS to create a new payment intent
@activity.defn
async def create_payment_intent(data) -> dict:
    data["amount"] = data["amount_of_money"]
    try:
        result = requests.post(f"{PAYMENT_MS_URL}/payments", data=data)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {PAYMENT_MS_URL}. {str(err)}"
            },
        }
    return result


# Post to Project MS to reserve offset
@activity.defn
async def reserve_offset(data) -> dict:
    url = format_url(
        PROJECT_OFFSET_URL,
        data["project_id"],
        data["milestone_id"],
    )
    payload = {
        "payment_id": data["payment_id"],
        "amount": data["quantity_tco2e"],
        "buyer_id": data["buyer_id"],
    }
    try:
        result = requests.post(url, data=payload)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {PROJECT_OFFSET_URL}. {str(err)}"
            },
        }
    return result


# Get payment intent from Payment MS
@activity.defn
async def get_payment_intent(data) -> dict:
    payment_id = data
    url = f"{PAYMENT_MS_URL}/payments/{payment_id}"
    try:
        result = requests.get(url)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {PAYMENT_MS_URL}. {str(err)}"
            },
        }
    return result


# Patch request to Project MS to commit offset
@activity.defn
async def commit_offset(data) -> dict:
    url = format_url(
        PROJECT_OFFSET_URL,
        data["project_id"],
        data["milestone_id"],
    )
    try:
        result = requests.post(url, data={"payment_id": data["payment_id"]})
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {PROJECT_OFFSET_URL}. {str(err)}"
            },
        }
    return result


# Post request to User MS to add pending offset
@activity.defn
async def add_pending_offset(data) -> dict:
    url = f"{USER_MS_URL}/users/{data['buyer_id']}/offset"
    payload = {
        "success": True,
        "data": {
            "amount": data["amount"],
            "buyer_id": data["project_id"],
            "created_at": data["created_at"],
            "milestone_id": data["milestone_id"],
            "payment_id": data["payment_id"],
            "status": "pending",
            "updated_at": data["updated_at"],
        },
    }
    try:
        result = requests.post(url, data=payload)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {USER_MS_URL}. {str(err)}"
            },
        }
    return result


# Delete request to Projects MS to remove offset
@activity.defn
async def remove_offset(data) -> dict:
    url = format_url(PROJECT_OFFSET_URL, data["project_id"], data["milestone_id"])
    try:
        result = requests.delete(url, data={"payment_id": data["payment_id"]})
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        result = {
            "success": False,
            "data": {
                "message": f"invocation of service fails: {PROJECT_OFFSET_URL}. {str(err)}"
            },
        }
    return result


# Publish message to Notify MS through AMQP to indicate payment success or failure
@activity.defn
async def publish_message(data) -> dict:
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    if data["payment_status"] == "failed":
        payload = {
            "payment_status": data["payment_status"],
            "buyer_id": data["buyer_id"],
            "seller_id": data["seller_id"],
        }
    else:
        payload = {
            "payment_status": data["payment_status"],
            "buyer_id": data["buyer_id"],
        }
    key = PAYMENT_STATUS_ROUTING_KEY.format(payment_status=data["payment_status"])
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=key,
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    return {
        "success": True,
        "data": {
            "message": "message sent to Notifier",
            "resource": "",
        },
    }
