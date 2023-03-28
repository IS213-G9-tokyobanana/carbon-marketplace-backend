import pika
from config.config import (
    EXCHANGE_NAME,
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
)


def publish_message(
    connection,
    channel,
    exchangename,
    routing_key,
    message,
):
    """This function in this module publishes a message (persistent) to the exchange with a routing key."""
    check_setup(connection, channel)
    channel.basic_publish(
        exchange=exchangename,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )


def create_connection():
    # Define connection parameters
    parameters = pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        blocked_connection_timeout=3600,
    )
    # Create connection
    connection = pika.BlockingConnection(parameters=parameters)
    return connection


def check_setup(connection, channel):
    if not is_connection_open(connection):
        parameters = pika.ConnectionParameters(
            host=RMQHOSTNAME,
            port=RMQPORT,
            heartbeat=3600,
            blocked_connection_timeout=3600,
            credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
        )
        connection = pika.BlockingConnection(parameters=parameters)
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
        )


def is_connection_open(connection: pika.BlockingConnection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
