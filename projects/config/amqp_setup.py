import pika

from dotenv import load_dotenv
from os import getenv

load_dotenv()
RABBITMQ_HOSTNAME = getenv('RABBITMQ_HOSTNAME')
RABBITMQ_USERNAME = getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = getenv('RABBITMQ_PASSWORD')
RABBITMQ_PORT = getenv('RABBITMQ_PORT')

ROUTING_KEY = 'routing_key'
BINDING_KEY = 'binding_key'
PROJECTS_CREATED_QUEUE = 'projects_created'
PROJECTS_VERIFIED_QUEUE = 'projects_verified'
PROJECTS_MILESTONES_ADD_QUEUE = 'projects_milestone_added'
PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE = 'projects_milestones_offsets_reserve'
PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE = 'projects_milestones_offsets_commit'
PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE = 'projects_milestones_offsets_rollback'
PROJECTS_MILESTONES_REWARD_QUEUE = 'projects_milestones_reward'
PROJECTS_MILESTONES_PENALISE_QUEUE = 'projects_milestones_penalise'


QUEUES = { # {queue_name: {"binding_key": binding_key, "routing_key": routing_key}, ...}
    PROJECTS_CREATED_QUEUE: {
        ROUTING_KEY: 'events.projects.public.project.create',
        BINDING_KEY: 'events.projects.*.project.create',
    },
    PROJECTS_VERIFIED_QUEUE: {
        ROUTING_KEY: 'events.projects.public.project.verify',
        BINDING_KEY: 'events.projects.*.project.verify',
    },
    PROJECTS_MILESTONES_ADD_QUEUE: {
        ROUTING_KEY: 'events.projects.public.milestone.add',
        BINDING_KEY: 'events.projects.*.milestone.add',
    },
    PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE: {
        ROUTING_KEY: 'events.projects.public.offsets.reserve',
        BINDING_KEY: 'events.projects.*.offsets.reserve',
    },
    PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE: {
        ROUTING_KEY: 'events.projects.public.offsets.commit',
        BINDING_KEY: 'events.projects.*.offsets.commit',
    },
    PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE: {
        ROUTING_KEY: 'events.projects.public.offsets.rollback',
        BINDING_KEY: 'events.projects.*.offsets.rollback',
    },
    PROJECTS_MILESTONES_REWARD_QUEUE: {
        ROUTING_KEY: 'events.projects.public.ratings.reward',
        BINDING_KEY: 'events.projects.*.ratings.reward',
    },
    PROJECTS_MILESTONES_PENALISE_QUEUE: {
        ROUTING_KEY: 'events.projects.public.ratings.penalise',
        BINDING_KEY: 'events.projects.*.ratings.penalise',
    },
}

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOSTNAME, port=RABBITMQ_PORT,
        heartbeat=3600, blocked_connection_timeout=3600,
        credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
))

channel = connection.channel()
exchangename="topic_exchange"
exchangetype="topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


# Bind all queues to the exchange with their respective binding keys
for queue_name, queue_info in QUEUES.items():
    channel.queue_declare(queue=queue_name, durable=True) 
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=queue_info[BINDING_KEY])

def publish_message(connection, channel, hostname, port, exchangename, exchangetype, routing_key, message):
    """This function in this module publishes a message (persistent) to the exchange with a routing key.
    """
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    channel.basic_publish(exchange=exchangename, routing_key=routing_key, body=message, properties=pika.BasicProperties(delivery_mode=2)) # make message persistent

def check_setup(connection, channel, hostname, port, exchangename, exchangetype):
    """This function in this module sets up a connection and a channel to a local AMQP broker,
    and declares a 'topic' exchange to be used by the microservices in the solution.
    """
    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


def is_connection_open(connection: pika.BlockingConnection):
    # For a BlockingConnection in AMQP clients,
    # when an exception happens when an action is performed,
    # it likely indicates a broken connection.
    # So, the code below actively calls a method in the 'connection' to check if an exception happens
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
