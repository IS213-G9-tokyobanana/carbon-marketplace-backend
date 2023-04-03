import os 
import pika
from os import getenv
from config import RABBITMQ_HOSTNAME, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, EXCHANGE, EXCHANGE_TYPE


QUEUE_PROJECT_CREATE = "notify_project_create"
QUEUE_PROJECT_RATINGS_REWARD = "notify_ratings_reward"
QUEUE_PROJECT_RATINGS_PENALISE = "notify_ratings_penalise"
QUEUE_PROJECT_VERIFY = "notify_project_verify"
QUEUE_PROJECT_MILESTONES_ADD = "notify_milestone_add"
QUEUE_BUYPROJECTS_PAYMENT_SUCCESS = "notify_payment_success"
QUEUE_BUYPROJECTS_PAYMENT_FAILED = "notify_payment_failed"
QUEUE_PROJECTPOLICE_MILESTONE_UPCOMING = "notify_milestone_upcoming"


connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOSTNAME,
            port=RABBITMQ_PORT,
            heartbeat=30,
            credentials= pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD),
            blocked_connection_timeout=3600))

channel = connection.channel()

# channel: BlockingChannel
# method: spec.Basic.Deliver
# properties: spec.BasicProperties

ROUTING_KEY = 'routing_key'
BINDING_KEY = 'binding_key'
SUBJECT = 'subject'
message = 'message'
message_buyer = 'message_buyer'
message_seller = 'message_seller'


QUEUES = {
    QUEUE_PROJECT_CREATE:  
    {   
        BINDING_KEY: "events.projects.*.project.create", 
        SUBJECT: "Project has been created",
        message: "Project with {project_id} has been created"
    },

    QUEUE_PROJECT_VERIFY:  
    {
        BINDING_KEY: "events.projects.*.project.verify" ,
        SUBJECT: "Project has been verified",
        message: "Project {project_id} has been verified"
    }, 

    QUEUE_PROJECT_RATINGS_REWARD: 
     {  
        BINDING_KEY: "events.projects.*.ratings.reward" ,
        SUBJECT: "Project has been rewarded",
        message: "Project {project_id} with milestone {milestone_id} has been rewarded"
     },

    QUEUE_PROJECT_RATINGS_PENALISE: 
    {
        BINDING_KEY: "events.projects.*.ratings.penalise" ,
        SUBJECT: "Project has been penalised", 
        message: "Project {project_id} with milestone {milestone_id} has been penalised"
    },

    QUEUE_PROJECT_MILESTONES_ADD:  
    {
        BINDING_KEY: "events.projects.*.milestone.add" ,
        SUBJECT: "Project Milestone has been added",
        message: "Project {project_id} with milestone {milestone_id} has been added"
    },
    
    QUEUE_PROJECTPOLICE_MILESTONE_UPCOMING: 
    {
        BINDING_KEY: "events.police.notify.milestone.upcoming" ,
        SUBJECT: "Upcoming Milestone",
        message: "Project {project_id} with milestone {milestone_id} is upcoming"
    },

    QUEUE_BUYPROJECTS_PAYMENT_SUCCESS:  
    {
        BINDING_KEY: "events.buyprojects.*.payment.success" ,
        SUBJECT: "Payment has been successful",
        message_buyer: "Hi Buyer {buyer_id} has successfully paid for the project",
        message_seller: "Hi Seller {seller_id} has successfully received payment for the project"
    }, 
    
    QUEUE_BUYPROJECTS_PAYMENT_FAILED: 
    {   
        BINDING_KEY:"events.buyprojects.*.payment.failed" ,
        SUBJECT: "Payment made failed",
        message_buyer: "Hi Buyer {buyer_id} payment has failed for the project"
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
    channel.basic_consume(queue, on_message_callback)
