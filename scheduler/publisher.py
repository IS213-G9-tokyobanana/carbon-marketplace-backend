import argparse
import pika
import json
from config import (
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
    TOPIC_EXCHANGE_NAME,
    PUBLISHED_TASK_EXECUTE_ROUTING_KEY
)

def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False

def check_setup(connection, channel, RMQHOSTNAME, RMQPORT):
    if not is_connection_open(connection):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RMQHOSTNAME,
                port=RMQPORT,
                heartbeat=3600,
                blocked_connection_timeout=3600,
            )
        )
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=TOPIC_EXCHANGE_NAME, exchange_type="topic", durable=True
        )

# Function to format message before sending to Notifier / Project Microservice
def format_message(resource_id, type, milestone_id, payment_id):

    new_data = {
        "project_id": resource_id,
        "milestone_id": milestone_id,
        "payment_id": payment_id
    }
    return json.dumps({"resource_id": resource_id, "type": type, "data": new_data})

# Function that republishes tasks that failed
def publishTask(event, project_id, milestone_id, payment_intent_id=None):
    type = ""
    if event == "upcoming":
        type = "upcoming"
    elif event == "overdue":
        type = "penalise"
    else:
        type = "rollback"
    
    payload = format_message(project_id, type, milestone_id, payment_intent_id)
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RMQHOSTNAME, port=RMQPORT,
        heartbeat=3600, blocked_connection_timeout=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD)
    ))
    channel = connection.channel()
    check_setup(connection, channel, RMQHOSTNAME, RMQPORT)
    channel.basic_publish(exchange=TOPIC_EXCHANGE_NAME, routing_key=PUBLISHED_TASK_EXECUTE_ROUTING_KEY, body=payload, properties=pika.BasicProperties(delivery_mode=2))

if __name__ == "__main__":
    # Need to have 3 options that can be passed in
    # 1. Upcoming Milestone
    # 2. Overdue Milestone
    # 3. Reserve Offset
    parser = argparse.ArgumentParser(prog='publisher.py', description='Publishes tasks to the exchange')
    parser.add_argument('--type', type=str, help='Type of task to be published')
    parser.add_argument('--proj', type=str, help='Project ID of task to be published')
    parser.add_argument('--mile', type=str, help='Milestone ID of task to be published')
    parser.add_argument('--payment', type=str, help='Payment Intent ID of task to be published', required=False)
    args = parser.parse_args()
    event = ""
    if args.type == 'upcoming':
        event = "upcoming"
    elif args.type == 'overdue':
        event = "overdue"
    else:
        event = "offset"
    publishTask(event, args.proj, args.mile, args.payment)