import checkAmqp
import pika
import json
import requests
from config import EXCHANGE_NAME


def checkType(msg):
    jsonmsg = json.dumps(
        {
            "resource_id": msg["data"]["milestoneid"],
            "type": "milestone.upcoming",
            "data": {
                "project_id": msg["data"]["projectid"],
                "milestone_id": msg["data"]["milestoneid"],
            },
        }
    )
    if msg["type"] == "upcoming":
        publishMsgNotify(jsonmsg)
    elif msg["type"] == "penalise":
        sendRequestProject(jsonmsg)
    elif msg["type"] == "overdue":
        # Trigger Temporal.io workflow
        return


def publishMsgNotify(jsonmsg):
    checkAmqp.channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key="events.police.notify.milestone.upcoming",
        body=jsonmsg,
        properties=pika.BasicProperties(delivery_mode=2),
    )


# Project Microservice URL = http://localhost:5000/api/v1/project
def sendRequestProject(jsonmsg):
    try:
        url = "http://localhost:5000/api/v1/project"
        res = requests.request("POST", url, json=jsonmsg)
    except Exception as e:
        code = 500
        result = {
            "code": code,
            "message": "invocation of service fails: " + url + ". " + str(e),
        }
    if code not in range(200, 300):
        return result
    if res.status_code != requests.codes.ok:
        code = res.status_code
    try:
        result = res.json() if len(res.content) > 0 else ""
    except Exception as e:
        code = 500
        result = {
            "code": code,
            "message": "Invalid JSON output from service: " + url + ". " + str(e),
        }
    return result
