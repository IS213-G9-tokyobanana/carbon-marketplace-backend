import os 
import pika
from os import getenv

RABBITMQ_HOSTNAME = getenv("RABBITMQ_HOSTNAME") or "13.229.231.31"
RABBITMQ_PORT = getenv("RABBITMQ_PORT") or 5672
RABBITMQ_USERNAME = getenv("RABBITMQ_USERNAME") or "guest"
RABBITMQ_PASSWORD = getenv("RABBITMQ_PASSWORD") or "guest"
EXCHANGE = "topic_exchange"
EXCHANGE_TYPE = "topic"
MS_BASE_URL = "http://localhost:5001"

PROJECT_CREATE_QUEUE = "project_create"
PROJECT_MILESTONES_REWARD_QUEUE = "project_milestones_reward"
PROJECT_MILESTONES_PENALISE_QUEUE = "project_milestones_penalise"
PROJECT_MILESTONES_VERIFY_QUEUE = "project_milestones_verify"
PROJECT_MILESTONES_UPDATE_QUEUE = "project_milestone_update"
BUY_PROJECTS_PAYMENT_SUCCESS_QUEUE = "buy_projects_payment_success"
BUY_PROJECTS_PAYMENT_FAILED_QUEUE = "buy_projects_payment_failed"
BUY_PROJECTS_NOTIFY_PAYMENT_FAILED_QUEUE = "buy_projects_notify_payment_failed"
UPCOMING_MILESTONE_PROJECT_POLICE_QUEUE = "upcoming_milestone_project_police"


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

BINDING_KEY = 'binding_key'
SUBJECT = 'subject'

QUEUES = {
    PROJECT_CREATE_QUEUE:  
    {
        BINDING_KEY: "events.projects.*.project.create", 
        SUBJECT: "Project has been created"
    },

    PROJECT_MILESTONES_REWARD_QUEUE: 
     {
        BINDING_KEY: "events.projects.*.ratings.reward" ,
        SUBJECT: "Project has been rewarded"
     },

    PROJECT_MILESTONES_PENALISE_QUEUE: 
    {
        BINDING_KEY: "events.projects.*.ratings.penalise" ,
        SUBJECT: "Project has been penalised"
    },

    PROJECT_MILESTONES_VERIFY_QUEUE:  
    {
        BINDING_KEY: "events.projects.*.project.verify" ,
        SUBJECT: "Project has been verified"
    }, 
    
    PROJECT_MILESTONES_UPDATE_QUEUE:  
    {
        BINDING_KEY: "events.projects.*.milestone.add" ,
        SUBJECT: "Project Milestone has been added"
    },
    
    BUY_PROJECTS_PAYMENT_SUCCESS_QUEUE:  
    {
        BINDING_KEY: "events.buyprojects.notify.payment.success" ,
        SUBJECT: "Payment has been successful"
    }, 
    
    BUY_PROJECTS_PAYMENT_FAILED_QUEUE: 
    {
        BINDING_KEY:"events.buyprojects.public.payment.failed" ,
        SUBJECT: "Payment made failed"
    },

    BUY_PROJECTS_NOTIFY_PAYMENT_FAILED_QUEUE:  
    {
        BINDING_KEY: "events.buyprojects.notify.payment.failed" ,
        SUBJECT: "Payment made failed"
    },
    UPCOMING_MILESTONE_PROJECT_POLICE_QUEUE: 
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