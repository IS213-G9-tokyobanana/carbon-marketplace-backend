from os import getenv

import pika

RABBITMQ_HOSTNAME = getenv("RABBITMQ_HOSTNAME")
RABBITMQ_USERNAME = getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = getenv("RABBITMQ_PASSWORD")
RABBITMQ_PORT = getenv("RABBITMQ_PORT")

ROUTING_KEY = "routing_key"
BINDING_KEY = "binding_key"
PROJECTS_CREATED_QUEUE = "project_create"
PROJECTS_VERIFIED_QUEUE = "project_verify"
PROJECTS_MILESTONES_ADD_QUEUE = "milestone_add"
PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE = "offsets_reserve"
PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE = "offsets_commit"
PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE = "offsets_rollback"
PROJECTS_MILESTONES_REWARD_QUEUE = "ratings_reward"
PROJECTS_MILESTONES_PENALISE_QUEUE = "ratings_penalise"


QUEUES = (
    {  # {queue_name: {"binding_key": binding_key, "routing_key": routing_key}, ...}
        PROJECTS_CREATED_QUEUE: {
            ROUTING_KEY: "events.projects.public.project.create",
            BINDING_KEY: "events.projects.*.project.create",
        },
        PROJECTS_VERIFIED_QUEUE: {
            ROUTING_KEY: "events.projects.public.project.verify",
            BINDING_KEY: "events.projects.*.project.verify",
        },
        PROJECTS_MILESTONES_ADD_QUEUE: {
            ROUTING_KEY: "events.projects.public.milestone.add",
            BINDING_KEY: "events.projects.*.milestone.add",
        },
        PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE: {
            ROUTING_KEY: "events.projects.public.offsets.reserve",
            BINDING_KEY: "events.projects.*.offsets.reserve",
        },
        PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE: {
            ROUTING_KEY: "events.projects.public.offsets.commit",
            BINDING_KEY: "events.projects.*.offsets.commit",
        },
        PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE: {
            ROUTING_KEY: "events.projects.public.offsets.rollback",
            BINDING_KEY: "events.projects.*.offsets.rollback",
        },
        PROJECTS_MILESTONES_REWARD_QUEUE: {
            ROUTING_KEY: "events.projects.public.ratings.reward",
            BINDING_KEY: "events.projects.*.ratings.reward",
        },
        PROJECTS_MILESTONES_PENALISE_QUEUE: {
            ROUTING_KEY: "events.projects.public.ratings.penalise",
            BINDING_KEY: "events.projects.*.ratings.penalise",
        },
    }
)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOSTNAME,
        port=RABBITMQ_PORT,
        heartbeat=30,
        blocked_connection_timeout=3600,
        credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
    )
)

channel = connection.channel()
exchangename = "topic_exchange"
exchangetype = "topic"
channel.exchange_declare(
    exchange=exchangename, exchange_type=exchangetype, durable=True
)


# Bind all queues to the exchange with their respective binding keys (done by consumer microservices)
# for queue_name, queue_info in QUEUES.items():
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=queue_info[BINDING_KEY])


def publish_message(
    exchangename,
    routing_key,
    message,
):
    """This function in this module publishes a message (persistent) to the exchange with a routing key."""
    global connection, channel
    connection, channel = check_setup(connection, channel)
    channel.basic_publish(
        exchange=exchangename,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )


def create_connection():
    # Define connection parameters
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOSTNAME,
        port=RABBITMQ_PORT,
        heartbeat=30,
        credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
        blocked_connection_timeout=3600,
    )
    # Create connection
    connection = pika.BlockingConnection(parameters=parameters)
    print("Connection created", connection)
    return connection


def check_setup(connection, channel):
    if not is_connection_open(connection) or channel.is_closed:
        connection = create_connection()
        channel = connection.channel()
    return connection, channel


def is_connection_open(connection: pika.BlockingConnection):
    try:
        connection.process_data_events()
        return connection.is_closed
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
