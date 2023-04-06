import pika
import requests
from config.config import (
    PAYMENT_MS_URL,
    POLICE_NOTIFY_ROLLBACK_ROUTING_KEY,
    PROJECT_MS_URL,
    USER_MS_URL,
)

# add the path to the main directory of your project to the system path
from police import format_message, get_connection, publish_to_notifier
from temporalio import activity


# Request to Payment Microservice to retrieve relevant payment intent
@activity.defn
async def get_payment_object_by_milestone_id(milestone_id) -> dict:
    r = requests.get(f"{PAYMENT_MS_URL}/payments?milestone_id={milestone_id}")
    if r.status_code == 404:
        return
    r.raise_for_status()
    return r.json()


@activity.defn
async def update_user_offset(data) -> dict:
    if not data.get("buyer_id"):
        return {"success": True, "data": {"message": "No buyer_id found in data"}}

    user_id = data["buyer_id"]
    payment_id = data["payment_id"]
    milestone_status = data["status"]
    url = f"{USER_MS_URL}/users/{user_id}/offset/{payment_id}"
    r = requests.patch(url, json=dict(status=milestone_status))
    r.raise_for_status()
    return r.json()


@activity.defn
async def update_project_milestone_status(data) -> dict:
    # reward or penalise project
    project_id = data["project_id"]
    milestone_id = data["milestone_id"]
    milestone_status = data["status"]
    url = f"{PROJECT_MS_URL}/projects/{project_id}/milestones/{milestone_id}/status"
    r = requests.patch(url, json=dict(status=milestone_status))
    r.raise_for_status()
    return r.json()


@activity.defn
async def notify_buyer_payment_failed(data) -> dict:
    message = format_message(
        resource_id=data["payment_id"], type="payment.failed", data=data
    )
    channel = get_connection().channel()
    result = publish_to_notifier(
        channel=channel,
        message=message,
        routing_key=POLICE_NOTIFY_ROLLBACK_ROUTING_KEY,
    )
    return result


# Request to Project Microservice to remove reserved offset
@activity.defn
async def remove_reserved_offset_by_payment_id(payment_id) -> dict:
    url = f"{PROJECT_MS_URL}/projects/milestones/offset"
    r = requests.delete(url, json=dict(payment_id=payment_id))
    r.raise_for_status()
    return r.json()
