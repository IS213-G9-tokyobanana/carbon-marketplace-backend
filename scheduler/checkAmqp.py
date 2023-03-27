import json
import pika
from config import (
    RMQHOSTNAME,
    RMQPORT,
    RMQUSERNAME,
    RMQPASSWORD,
    TOPIC_EXCHANGE_NAME,
    BINDING_KEYS,
)
import scheduler

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RMQHOSTNAME,
        port=RMQPORT,
        heartbeat=3600,
        blocked_connection_timeout=3600,
        credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD),
    )
)

# Create a connection channel
channel = connection.channel()

# Loops through all the binding keys and creates a queue for each
for queue_name, binding_key in BINDING_KEYS.items():
    channel.queue_declare(queue_name, durable=True)
    channel.queue_bind(exchange=TOPIC_EXCHANGE_NAME, queue=queue_name, routing_key=binding_key)

def check_setup():
    global connection, channel, RMQHOSTNAME, RMQPORT
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


def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False

# For each queue, begin to consume messages
def receiveMsg():

    for key, value in BINDING_KEYS.items():
        print(
            ": monitoring key '{}' on exchange '{}' ...".format(
                value, TOPIC_EXCHANGE_NAME
            )
        )
        channel.basic_consume(
            queue=key,
            on_message_callback=callback,
            auto_ack=True,
        )
    channel.start_consuming()


def callback(channel, method, properties, body):
    # print(" [x] Received %r" % body)
    # after receiving a message, call the scheduler
    try:
        data = json.loads(body)
        scheduler.checkType(data)
    except json.decoder.JSONDecodeError as e:
        print("--NOT JSON:", e)
        print("--DATA:", body)

def test():
    print('testing cron')
    scheduler.test_cron()
    print('after test cron')


if __name__ == "__main__":
    check_setup()
    receiveMsg()
