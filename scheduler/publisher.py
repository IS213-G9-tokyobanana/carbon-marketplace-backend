import argparse
import pika
import json
from config.rabbitmq_setup import (
    RMQHOSTNAME, RMQPORT, RMQUSERNAME, RMQPASSWORD, connection, channel, EXCHANGE_TYPE, PUBLISHED_TASK_EXECUTE_ROUTING_KEY, TOPIC_EXCHANGE_NAME, publish_message
)
from classes.enums import TaskType
from classes.Message import Message

def republish_task(message: dict):
    message_serialised = json.dumps(message)
    publish_message(
        connection=connection, channel=channel, hostname=RMQHOSTNAME, port=RMQPORT, username=RMQUSERNAME, password=RMQPASSWORD, exchange_name=TOPIC_EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, 
        routing_key=PUBLISHED_TASK_EXECUTE_ROUTING_KEY, 
        message=message_serialised)

def publish_task(type: str, project_id=None, milestone_id=None, payment_id=None):
    resource_id = milestone_id
    if type == TaskType.PAYMENT_OVERDUE.value:    
        resource_id = payment_id
    
    data = {
        "project_id": project_id,
        "milestone_id": milestone_id,
        "payment_id": payment_id
    }

    message = Message(resource_id=resource_id, type=type, data=data).json()
    message_serialised = json.dumps(message)
    publish_message(
        connection=connection, channel=channel, hostname=RMQHOSTNAME, port=RMQPORT, username=RMQUSERNAME, password=RMQPASSWORD, exchange_name=TOPIC_EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, 
        routing_key=PUBLISHED_TASK_EXECUTE_ROUTING_KEY, 
        message=message_serialised)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='publisher.py', description='Publishes tasks to the exchange')
    parser.add_argument('--type', type=str, help='Type of task to be published')
    parser.add_argument('--project', type=str, help='Project ID of task to be published')
    parser.add_argument('--milestone', type=str, help='Milestone ID of task to be published')
    parser.add_argument('--payment', type=str, help='Payment Intent ID of task to be published', required=False)
    args = parser.parse_args()
    
    type = args.type
    milestone_id = args.milestone
    project_id = args.project
    payment_id = args.payment
    
    publish_task(type=type, project_id=project_id, milestone_id=milestone_id, payment_id=payment_id)