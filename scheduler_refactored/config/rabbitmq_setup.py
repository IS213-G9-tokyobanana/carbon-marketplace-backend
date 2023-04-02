import pika
import os
from dotenv import load_dotenv

load_dotenv()
RMQHOSTNAME = os.getenv('rmqhostname')
RMQUSERNAME = os.getenv('rmqusername')
RMQPASSWORD = os.getenv('rmqpassword')
RMQPORT = os.getenv('rmqport')

TOPIC_EXCHANGE_NAME = "topic_exchange"
EXCHANGE_TYPE = "topic"

# Binding Keys that scheduler has to listen to
BINDING_KEYS = {
    "scheduler.milestone.add":"events.projects.*.milestone.add",
    "scheduler.project.verify":"events.projects.*.project.verify",
    "scheduler.task.add":"events.*.scheduler.task.add",
    "scheduler.offsets.reserve":"events.projects.*.offsets.reserve",
    "scheduler.offsets.commit":"events.projects.*.offsets.commit",
    "scheduler.ratings.reward":"events.projects.*.ratings.reward",
    "scheduler.ratings.penalise":"events.projects.*.ratings.penalise",
    "scheduler.payment.fail":"events.buyprojects.*.payment.failed",
}

# Routing Keys that scheduler has to publish to
PUBLISHED_TASK_EXECUTE_ROUTING_KEY = "events.scheduler.public.task.execute"

def connect_to_broker(hostname, port, username, password):
    """Connects to an AMQP broker and returns a connection and a channel.
    """
    print(f'connecting to broker with hostname: {hostname} port:{port} username: {username} password: {password})')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname, port=port,
            heartbeat=30, blocked_connection_timeout=3600,
            credentials=pika.PlainCredentials(username, password)
    ))
    channel = connection.channel()
    return connection, channel


def is_connection_open(connection: pika.BlockingConnection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False


def setup_exchange(connection, channel, hostname, port, username, password, exchange_name, exchange_type):
    """Declares an exchange if channel is closed
    """
    if not is_connection_open(connection):
        connection, channel = connect_to_broker(hostname, port, username, password)
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)


def publish_message(connection, channel, hostname, port, username, password, exchange_name, exchange_type, routing_key, message):
    """Publishes a message (persistent) to the exchange with a routing key.
    """
    setup_exchange(
        connection=connection, channel=channel, hostname=hostname, port=port, username=username, password=password, 
        exchange_name=exchange_name, exchange_type=exchange_type)
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message, properties=pika.BasicProperties(delivery_mode=2)) # make message persistent


connection, channel = connect_to_broker(RMQHOSTNAME, RMQPORT, RMQUSERNAME, RMQPASSWORD)

setup_exchange(connection, channel, RMQHOSTNAME, RMQPORT, RMQUSERNAME, RMQPASSWORD, TOPIC_EXCHANGE_NAME, EXCHANGE_TYPE)

# Bind all queues to the exchange with their respective binding keys (done by consumer microservices)
for QUEUE_NAME, BINDING_KEY in BINDING_KEYS.items():
    channel.queue_declare(queue=QUEUE_NAME, durable=True) 
    channel.queue_bind(exchange=TOPIC_EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=BINDING_KEY)
