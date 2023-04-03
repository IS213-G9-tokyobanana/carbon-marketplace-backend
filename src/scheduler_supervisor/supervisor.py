import json
import logging

from amqp_setup import check_setup, create_connection, publish_message
from config.config import (
    EXCHANGE_NAME,
    QUEUE_NAME,
    SCHEDULER_SUPERVISOR_SCHEDULER_ROUTING_KEY,
    TASK_STATUS_BINDING_KEY,
)


def callback(channel, method, properties, body):
    data = json.loads(body)
    check_status(data)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_message(
    connection,
    channel,
    exchangename,
    queue_name,
    routing_key,
):
    """This function in this module consumes a message (persistent) from the exchange with a routing key."""
    check_setup(connection, channel)
    try:
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=exchangename,
            queue=queue_name,
            routing_key=routing_key,
        )
        channel.basic_consume(queue_name, callback)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
    except Exception as err:
        logging.exception("Error processing message: %s", err)


def check_status(data: dict):
    if data["success"] == True:
        print("Task completed successfully!")
    else:
        payload = data["data"]["resource"]
        payload = json.dumps(payload)
        publish_message(
            connection=connection,
            channel=channel,
            exchangename=EXCHANGE_NAME,
            routing_key=SCHEDULER_SUPERVISOR_SCHEDULER_ROUTING_KEY,
            message=payload,
        )


if __name__ == "__main__":
    print(
        f"monitoring the exchange {EXCHANGE_NAME} on binding key {TASK_STATUS_BINDING_KEY} ..."
    )
    connection = create_connection()
    channel = connection.channel()
    consume_message(
        connection=connection,
        channel=channel,
        exchangename=EXCHANGE_NAME,
        queue_name=QUEUE_NAME,
        routing_key=TASK_STATUS_BINDING_KEY,
    )
