import json

import pika
import requests
from config.config import (
    EXCHANGE_NAME,
    PAYMENT_MS_URL,
    PAYMENT_STATUS_ROUTING_KEY,
    PROJECT_MS_URL,
    RMQHOSTNAME,
    RMQPASSWORD,
    RMQPORT,
    RMQUSERNAME,
    USER_MS_URL,
)
from temporalio import activity


# Request to Payment MS to create a new payment intent
@activity.defn
async def create_payment(data) -> dict:
    r = requests.post(f"{PAYMENT_MS_URL}/payments", json=data)
    r.raise_for_status()
    return r.json()


# Post to Project MS to reserve offset
@activity.defn
async def reserve_offset(payment_object) -> dict:
    project_id = payment_object["project_id"]
    milestone_id = payment_object["milestone_id"]
    buyer_id = payment_object["buyer_id"]
    payment_id = payment_object["payment_id"]
    quantity_tco2e = payment_object["quantity_tco2e"]
    url = f"{PROJECT_MS_URL}/projects/{project_id}/milestones/{milestone_id}/offset"
    r = requests.post(
        url,
        json=dict(
            payment_id=payment_id,
            buyer_id=buyer_id,
            amount=quantity_tco2e,
        ),
    )
    r.raise_for_status()
    return r.json()


# Get payment intent from Payment MS
@activity.defn
async def get_payment_object(payment_id) -> dict:
    """Get payment object to get project, milestone, seller & buyer id"""
    url = f"{PAYMENT_MS_URL}/payments?payment_id={payment_id}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


# Patch request to Project MS to commit offset
@activity.defn
async def commit_offset(payment_object) -> dict:
    payment_id = payment_object["payment_id"]
    url = f"{PROJECT_MS_URL}/projects/milestones/offset"
    r = requests.patch(url, json={"payment_id": payment_id})
    r.raise_for_status()
    return r.json()


# Post request to User MS to add pending offset
@activity.defn
async def add_pending_offset(payment_object) -> dict:
    milestone_id = payment_object["milestone_id"]
    buyer_id = payment_object["buyer_id"]
    payment_id = payment_object["payment_id"]
    quantity_tco2e = payment_object["quantity_tco2e"]
    url = f"{USER_MS_URL}/users/{buyer_id}/offset"
    payload = {
        "payment_id": payment_id,
        "milestone_id": milestone_id,
        "amount": quantity_tco2e,
        "status": "pending",
        "buyer_id": buyer_id,
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()


# Delete request to Projects MS to remove offset
@activity.defn
async def remove_offset(payment_object) -> dict:
    payment_id = payment_object["payment_id"]
    url = f"{PROJECT_MS_URL}/projects/milestones/offset"
    r = requests.delete(url, json={"payment_id": payment_id})
    r.raise_for_status()
    return r.json()


# Publish message to Notify MS through AMQP to indicate payment success or failure
@activity.defn
async def publish_message(data) -> dict:
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=30,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    payment_status = "success" if data["payment_succeeded"] else "failed"
    key = PAYMENT_STATUS_ROUTING_KEY.format(payment_status=payment_status)
    data["type"] = f"payment.{payment_status}"
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=key,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    return {
        "success": True,
        "data": {"message": "message sent to Notifier"},
    }
