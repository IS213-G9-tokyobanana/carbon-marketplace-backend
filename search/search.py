import meilisearch
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
        client = meilisearch.Client('http://search:7700')
        data = json.loads(body)
        if data['type'] == 'project.verify' or data['type'] == 'offset.rollback':
            client.index('projects').add_documents([data['data']], primary_key='id')
        elif data['type'] == 'milestone.add':
            # for milestone add
            response = client.index('projects').get_document(document_id = data['data']['project_id'])
            old = response.milestones
            new = data['data']['milestones']
            new.extend(old)
            client.index('projects').update_documents(
                [{
                    "id": data['data']['project_id'],
                    "milestones": new
                }],
                primary_key="id"
            )
        elif data['type'] == 'offset.reserve':
            response = client.index('projects').get_document(document_id = data['resource_id'])
            new = data['data']['milestones']
            client.index('projects').update_documents(
                [{
                    "id": data['resource_id'],
                    "milestones": new
                }],
                primary_key="id"
            )

    except json.decoder.JSONDecodeError as e:
        print("--NOT JSON:", e)
        print("--DATA:", body)

if __name__ == "__main__":
    check_setup()
    receiveMsg()
    
