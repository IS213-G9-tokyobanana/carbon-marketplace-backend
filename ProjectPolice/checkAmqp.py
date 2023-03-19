import json
import pika
from config import RMQHOSTNAME, RMQPORT, RMQUSERNAME, RMQPASSWORD, EXCHANGE_NAME, TASK_EXECUTE_ROUTING_KEY
import police

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RMQHOSTNAME, port=RMQPORT, heartbeat=3600, blocked_connection_timeout=3600, credentials=pika.PlainCredentials(RMQUSERNAME, RMQPASSWORD)
    )
)

# Create a connection channel
channel = connection.channel()

# Create a task_triggered_topic queue
channel.queue_declare("task_triggered_topic", durable=True)
channel.queue_bind(
    exchange= EXCHANGE_NAME,
    queue="task_triggered_topic",
    routing_key=TASK_EXECUTE_ROUTING_KEY,
)

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
            exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
        )

def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False

def receiveError():
    check_setup()
    channel.basic_consume(
        queue="task_triggered_topic",
        on_message_callback=callback,
        auto_ack=True,
    )
    channel.start_consuming()

def callback(channel, method, properties, body):
    processTrigger(body)

def processTrigger(message):
    try:
        data = json.loads(message)
        police.checkType(data)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", data)

if __name__ == "__main__": 
    print(": monitoring routing key '{}' in exchange '{}' ...".format("events.*.*.task.execute", EXCHANGE_NAME))
    receiveError()


