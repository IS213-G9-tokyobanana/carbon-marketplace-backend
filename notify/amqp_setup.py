import os 
import pika
from os import getenv
from dotenv import load_dotenv

load_dotenv()
RABBITMQ_HOSTNAME = getenv("RABBITMQ_HOSTNAME") or "13.229.231.31"
RABBITMQ_PORT = getenv("RABBITMQ_PORT") or 5672
RABBITMQ_USERNAME = getenv("RABBITMQ_USERNAME") or "guest"
RABBITMQ_PASSWORD = getenv("RABBITMQ_PASSWORD") or "guest"
EXCHANGE = getenv("EXCHANGE")
EXCHANGE_TYPE = getenv("EXCHANGE_TYPE")
MS_BASE_URL = getenv("MS_BASE_URL")


QUEUE_PROJECT_CREATE = "project_create"
QUEUE_PROJECT_MILESTONES_REWARD = "ratings_reward"
QUEUE_PROJECT_MILESTONES_PENALISE = "ratings_penalise"
QUEUE_PROJECT_MILESTONES_VERIFY = "project_verify"
QUEUE_PROJECT_MILESTONES_UPDATE = "milestone_add"
QUEUE_BUY_PROJECTS_PAYMENT_SUCCESS = "payment_success"
QUEUE_BUY_PROJECTS_PAYMENT_FAILED = "payment_failed"
QUEUE_BUY_PROJECTS_NOTIFY_PAYMENT_FAILED = "payment_failed"
QUEUE_UPCOMING_MILESTONE_PROJECT_POLICE = "milestone_upcoming"


connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOSTNAME,
            port=RABBITMQ_PORT,
            heartbeat=3600,
            credentials= pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
            blocked_connection_timeout=3600))

channel = connection.channel()

# channel: BlockingChannel
# method: spec.Basic.Deliver
# properties: spec.BasicProperties

ROUTING_KEY = 'routing_key'
BINDING_KEY = 'binding_key'
SUBJECT = 'subject'

QUEUES = {
    QUEUE_PROJECT_CREATE:  
    {   
        BINDING_KEY: "events.projects.*.project.create", 
        SUBJECT: "Project has been created"
    },

    QUEUE_PROJECT_MILESTONES_REWARD: 
     {  
        BINDING_KEY: "events.projects.*.ratings.reward" ,
        SUBJECT: "Project has been rewarded"
     },

    QUEUE_PROJECT_MILESTONES_PENALISE: 
    {
        BINDING_KEY: "events.projects.*.ratings.penalise" ,
        SUBJECT: "Project has been penalised"
    },

    QUEUE_PROJECT_MILESTONES_VERIFY:  
    {
        BINDING_KEY: "events.projects.*.project.verify" ,
        SUBJECT: "Project has been verified"
    }, 
    
    QUEUE_PROJECT_MILESTONES_UPDATE:  
    {
        BINDING_KEY: "events.projects.*.milestone.add" ,
        SUBJECT: "Project Milestone has been added"
    },
    
    QUEUE_BUY_PROJECTS_PAYMENT_SUCCESS:  
    {
        BINDING_KEY: "events.buyprojects.notify.payment.success" ,
        SUBJECT: "Payment has been successful"
    }, 
    
    QUEUE_BUY_PROJECTS_PAYMENT_FAILED: 
    {   
        BINDING_KEY:"events.buyprojects.public.payment.failed" ,
        SUBJECT: "Payment made failed"
    },

    QUEUE_BUY_PROJECTS_NOTIFY_PAYMENT_FAILED:  
    {   
        BINDING_KEY: "events.buyprojects.notify.payment.failed" ,
        SUBJECT: "Payment made failed"
    },
    QUEUE_UPCOMING_MILESTONE_PROJECT_POLICE: 
    {
        BINDING_KEY: "events.police.notify.milestone.upcoming" ,
        SUBJECT: "Upcoming Milestone"
    }
}

for queue_name, binding_key in QUEUES.items():
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=binding_key[BINDING_KEY])

def is_connection_open(connection:pika.BlockingConnection):
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
    
def check_setup(connection, channel, host, port, exchangename, exchangetype):
    #This function in this module sets up a connection and a channel to a local AMQP broker,
    #and declares a 'topic' exchange to be used by the microservices in the solution.
    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOSTNAME, port=RABBITMQ_PORT, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type=EXCHANGE_TYPE, durable=True) ###

def channel_consume(connection, channel, host, port, exchangename, exchangetype, queue, on_message_callback):
    check_setup(connection, channel, host, port, exchangename, exchangetype)
    channel.basic_consume(queue, on_message_callback, auto_ack=True)