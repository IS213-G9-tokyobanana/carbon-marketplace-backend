import json
import pika
import logging
import asyncio
from config.config import (
    EXCHANGE_NAME,
    TASK_EXECUTE_BINDING_KEY,
    QUEUE_NAME,
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
)
import police
from temporal.run_workflow import main

# Global variable
channel = None


def create_connection(type: str):
    # Define connection parameters
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    # Connect to RabbitMQ
    if type == "selection":
        connection = pika.SelectConnection(
            parameters=parameters, on_open_callback=on_open
        )
    elif type == "blocking":
        connection = pika.BlockingConnection(parameters=parameters)
    else:
        return "Invalid connection type"
    return connection


# Function is called when connection is open, and channel is open
def on_open(connection: pika.SelectConnection):
    connection.channel(on_open_callback=on_channel_open)


# Function is called when channel is open, and queue is declared
def on_channel_open(new_channel: pika.channel.Channel):
    global channel
    channel = new_channel
    # Create a task_triggered_topic queue
    channel.queue_declare(QUEUE_NAME, durable=True, callback=on_queue_declared)
    # Bind the queue to the exchange
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=TASK_EXECUTE_BINDING_KEY,
    )


# Function is called when queue is declared, and basic_consume is called
def on_queue_declared(frame: pika.frame.Method):
    channel.basic_consume(QUEUE_NAME, callback, auto_ack=False)


# Function is called when message is received
def callback(channel, method, properties, body):
    try:
        print("Received message:", body)
        data = json.loads(body)
        check_message(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as err:
        logging.exception("Error processing message: %s", err)


# Function is called when message is received, and message type is checked
def check_message(data: dict):
    try:
        if data["type"] == "upcoming":
            result = police.publish_to_notifier(data, channel)
        elif data["type"] == "penalise":
            result = police.send_to_projectms(data)
        elif data["type"] == "overdue":
            result = asyncio.run(main(data))
        else:
            result = {
                "success": False,
                "data": {
                    "message": "Invalid message type",
                },
            }
        print("Result:", result)
        publish_status(result)
    except Exception as err:
        logging.exception("Error processing message: %s", err)


def publish_status(result: dict):
    # Publish result to supoervisor ms
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key="events.police.public.task.status",
        body=json.dumps(result),
        properties=pika.BasicProperties(delivery_mode=2),
    )

if __name__ == "__main__":
    print(
        f"monitoring the exchange {EXCHANGE_NAME} on binding key {TASK_EXECUTE_BINDING_KEY} ..."
    )
    connection = create_connection("selection")
    try:
        connection.ioloop.start()
    except KeyboardInterrupt:
        # Gracefully close the connection
        connection.close()
        connection.ioloop.start()
