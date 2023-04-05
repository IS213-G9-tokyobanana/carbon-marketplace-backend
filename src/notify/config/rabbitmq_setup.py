import pika
from classes.MessageType import MessageType
from config.config import (
    EXCHANGE,
    EXCHANGE_TYPE,
    RABBITMQ_HOSTNAME,
    RABBITMQ_PASSWORD,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
)

#<RESOURCE>_<ACTION>_QUEUE = "notify_<RESOURCE>.<ACTION>" # variable = queue_name
PROJECT_CREATE_QUEUE = "notify_project_create"
RATINGS_REWARD_QUEUE = "notify_ratings_reward"
RATINGS_PENALISE_QUEUE = "notify_ratings_penalise"
PROJECT_VERIFY_QUEUE = "notify_project_verify"
MILESTONE_ADD_QUEUE = "notify_milestone_add"
PAYMENT_SUCCESS_QUEUE = "notify_payment_success"
PAYMENT_FAILED_QUEUE = "notify_payment_failed"
MILESTONE_UPCOMING_QUEUE = "notify_milestone_upcoming"

QUEUES = { # { queue_name: binding_key }
    PROJECT_CREATE_QUEUE: "events.projects.*.project.create", 
    RATINGS_REWARD_QUEUE: "events.projects.*.ratings.reward",
    RATINGS_PENALISE_QUEUE: "events.projects.*.ratings.penalise",
    PROJECT_VERIFY_QUEUE: "events.projects.*.project.verify",
    MILESTONE_ADD_QUEUE: "events.projects.*.milestones.add",
    PAYMENT_SUCCESS_QUEUE: "events.buyprojects.*.payment.success",
    PAYMENT_FAILED_QUEUE: "events.*.*.payment.failed",
    MILESTONE_UPCOMING_QUEUE: "events.projectpolice.*.milestone.upcoming",

}


BUYER_MESSAGES = { # { queue_name: message }
    MessageType.PAYMENT_SUCCESS.value: {
        "subject": "Payment success",
        "message": """
        Dear {recipient},
            This is to inform you that the following purchase was successful:
            Milestone ID: {milestone_id}
        """,
    },

    MessageType.PAYMENT_FAILED.value: {
        "subject": "Payment failed",
        "message": """
        Dear {recipient},
            This is to inform you that the following purchase was unsuccessful:
            Milestone ID: {milestone_id}
        """
    },

    MessageType.MILESTONE_PENALISE.value: {
        "subject": "Milestone has been {milestone_status}",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone has been {milestone_status} and project rating {rating_action}.:
            Milestone ID: {milestone_id}
            Milestone Name: {milestone_name}
            Milestone Status: {milestone_status}

            Project ID: {project_id}
            Project Name: {project_name}
            Project Rating: {rating}
        """,
    },

    MessageType.MILESTONE_REWARD.value: {
        "subject": "Milestone has been {milestone_status}",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone has been {milestone_status} and project rating {rating_action}:
            Milestone ID: {milestone_id}
            Milestone Name: {milestone_name}
            Milestone Status: {milestone_status}

            Project ID: {project_id}
            Project Name: {project_name}
            Project Rating: {rating}
        """,
    },
}

SELLER_MESSAGES = {
    MessageType.PROJECT_VERIFY.value: {
        "subject": "Project has been verified",
        "message": """
        Dear {recipient},
            This is to inform you that your project has been verified:
            Project ID: {project_id}
            Project name: {project_name}
        """,
    },

    MessageType.MILESTONE_PENALISE.value: {
        "subject": "Milestone has been {milestone_status}",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone has been {milestone_status} and project rating {rating_action}.:
            Milestone ID: {milestone_id}
            Milestone Name: {milestone_name}
            Milestone Status: {milestone_status}

            Project ID: {project_id}
            Project Name: {project_name}
            Project Rating: {rating}
        """,
    },

    MessageType.MILESTONE_REWARD.value: {
        "subject": "Milestone has been {milestone_status}",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone has been {milestone_status} and project rating {rating_action}.:
            Milestone ID: {milestone_id}
            Milestone Name: {milestone_name}
            Milestone Status: {milestone_status}

            Project ID: {project_id}
            Project Name: {project_name}
            Project Rating: {rating}
        """,
    },

    MessageType.PAYMENT_SUCCESS.value: {
        "subject": "Payment success",
        "message": """
        Dear {recipient},
            This is to inform you that the offsets for the following milestone has been purchased:
            Milestone ID: {milestone_id}
            Milestone Name: {milestone_name}
            Offsets Available: {offsets_available}
            Offsets Total: {offsets_total}
            
        """,
    },

}

VERIFIER_MESSAGES = { # { payload_type: {subject, message} }
    MessageType.PROJECT_CREATE.value: {
        "subject": "Project has been created",
        "message": """
        Dear {recipient},
            A new project {project_name} has been created. Please verify the project.
            Project ID: {project_id}
        """,
    },

    MessageType.MILESTONE_UPCOMING.value: {
        "subject": "Upcoming Milestone for verification",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone is upcoming for verification:
            Milestone id: {milestone_id}
            Project id: {project_id}
        """
    },
    
    MessageType.MILESTONE_ADD.value: {
        "subject": "Milestone Added",
        "message": """
        Dear {recipient},
            This is to inform you that the following milestone has been added for verification:
            Milestone id: {milestone_id}
            Project id: {project_id}
        """
    }
    
}




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


connection, channel = connect_to_broker(RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

setup_exchange(connection, channel, RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, EXCHANGE, EXCHANGE_TYPE)

for queue_name, binding_key in QUEUES.items():
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=binding_key)
