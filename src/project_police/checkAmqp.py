import asyncio
import json
import logging

import pika
import police
from config.config import (
    EXCHANGE_NAME,
    POLICE_SCHEDULER_MANAGER_ROUTING_KEY,
    QUEUE_NAME,
    RMQHOSTNAME,
    RMQPASSWORD,
    RMQPORT,
    RMQUSERNAME,
    TASK_EXECUTE_BINDING_KEY,
)
from temporal.penalise_reward_workflow import PenaliseRewardTemporalWorkflow
from temporal.rollback_workflow import RollbackTemporalWorkflow
from temporal.run_workflow import main

# Global variable
channel = None


def create_connection(type: str):
    # Define connection parameters
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=30,
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
    """
    data = {
        "type": "milestone_penalise",
        "resource_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
        "data": {
            "project_id": "19b65a6f-bbad-4d88-8744-a9cbe7e69a58",
            "milestone_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
            "payment_id": "1234",
            "status": "rejected"
        }
    } 
    """
    
    try:
        if data["type"] == "milestone_upcoming":
            result = police.publish_to_notifier(data, channel)
        elif data["type"] == "milestone_penalise" or data["type"] == "milestone_reward":
            milestone_status = (
                "met" if data["type"] == "milestone_reward" else "rejected"
            )
            print(
                "starting workflow with data: ",
                {**data["data"], "status": milestone_status},
            )
            result = asyncio.run(
                main(
                    PenaliseRewardTemporalWorkflow,
                    {**data["data"], "status": milestone_status},
                    "penalise-reward-task-queue",
                )
            )
        elif data["type"] == "payment_overdue":
            print("starting workflow with data: ", data["data"])
            result = asyncio.run(
                main(
                    RollbackTemporalWorkflow,
                    data["data"],
                    "rollback-task-queue",
                )
            )
        else:
            result = {
                "success": False,
                "data": {
                    "message": "Invalid message type",
                },
            }
        print("Result:", result)
        """ example result
        {
            "success": True,
            "data": {
                "message": "Workflow executed successfully",
                "resource": {
                    "project_id": "19b65a6f-bbad-4d88-8744-a9cbe7e69a58",
                    "milestone_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
                    "payment_id": "1234",
                    "status": "rejected"
                }
            }
        }
        """
        publish_status(result=result, input_data=data)
    except Exception as err:
        logging.exception("Error processing message: %s", err)


def publish_status(result: dict, input_data: dict):
    # Publish result to supoervisor ms
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=POLICE_SCHEDULER_MANAGER_ROUTING_KEY,
        body=json.dumps(dict(result=result, input_data=input_data)),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    """
    {
        "result": {
            "success": True,
            "data": {
                "message": "Workflow executed successfully",
                "resource": {
                    "project_id": "19b65a6f-bbad-4d88-8744-a9cbe7e69a58",
                    "milestone_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
                    "payment_id": "1234",
                    "status": "rejected"
                }
            }
        },
        "input_data": {
            "type": "milestone_penalise",
            "resource_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
            "data": {
                "project_id": "19b65a6f-bbad-4d88-8744-a9cbe7e69a58",
                "milestone_id": "915132d0-3b1d-4ca5-a09a-7b048fcac205",
                "payment_id": "1234",
                "status": "rejected"
            }
        } 
    }
    """


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
