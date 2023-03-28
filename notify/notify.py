import json
import logging
import requests
from os import getenv
from dotenv import load_dotenv
from amqp_setup import RABBITMQ_HOSTNAME, RABBITMQ_PORT, \
    connection, channel, \
    RABBITMQ_HOSTNAME, RABBITMQ_PORT, EXCHANGE, EXCHANGE_TYPE, QUEUES, BINDING_KEY, ROUTING_KEY, SUBJECT, MS_BASE_URL, channel_consume

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()
def process_message(data, SUBJECT):
    # send message to user (the message is an email)
    #sample message data 
    try: 
        retrieved_message = data
        print("this is data", retrieved_message)
        subject_retrieved = SUBJECT
        retrieved_user_email = retrieve_users_information()
        result_message = ""

        if retrieved_message["type"] == "project.create":
            result_message = project_created_details(retrieved_message)
        elif retrieved_message["type"] == "milestone.reward":
            result_message = project_milestone_rewarded_details(retrieved_message)
        elif retrieved_message["type"] == "milestone.penalise":
            result_message = project_milestone_penalised_details(retrieved_message)
        elif retrieved_message["type"] == "milestone.verify":
            result_message = project_milestone_verify_details(retrieved_message)
        elif retrieved_message["type"] == "milestone.add":
            result_message = project_milestone_add(retrieved_message)
        elif retrieved_message["type"] == "buyprojects.payment.success":
            result_message = buyproject_payment_success(retrieved_message)
        elif retrieved_message["type"] == "buyprojects.public.payment.fail":
            result_message = buyproject_payment_failure(retrieved_message)
        elif retrieved_message["type"] == "buyprojects.notify.payment.fail":
            result_message = buyproject_payment_failure(retrieved_message)
        elif retrieved_message["type"] == "milestone.upcoming":
            result_message = police_notify_upcoming_milestone(retrieved_message)
        
        send_email_to_user(retrieved_user_email, result_message, subject_retrieved)

    except KeyError:
        print("The subject does not exist in the dictionary")

def project_created_details(retrieved_message):
    project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    message = (f"Project with {project_id} has been created")
    return message

def project_milestone_rewarded_details(retrieved_message):
    project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    milestone_id = retrieved_message.get("data").get("milestones", {}).get("id")
    message = (f"Project {project_id} with milestone {milestone_id} has been rewarded")
    return message

def project_milestone_penalised_details(retrieved_message):
    project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    milestone_id = retrieved_message.get("data").get("milestones", {}).get("id")
    message = (f"Project {project_id} with milestone {milestone_id} has been penalised")
    return message

def project_milestone_verify_details(retrieved_message):
    project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    milestone_id = retrieved_message.get("data").get("milestones", {}).get("id")
    message = (f"Project {project_id} with milestone {milestone_id} has been verified")
    return message 

def project_milestone_add(retrieved_message):
    project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    milestone_id = retrieved_message.get("data").get("milestones", {}).get("id")
    message = (f"Project {project_id} with milestone {milestone_id} has been added")
    return message

def buyproject_payment_success(retrieved_message):
    buyer_id = retrieved_message.get("buyer_id", {})
    seller_id = retrieved_message.get("seller_id",{})
    role = retrieved_message.get("role",{})
    if role == 1:
        message = (f"Buyer {buyer_id} has successfully paid for the project")
    else:
        message = (f"Seller {seller_id} has successfully received payment for the project")
    return message

def buyproject_payment_failure(retrieved_message):
        buyer_id = retrieved_message.get("buyer_id", {})
        #assuming that role 1 is buyer and 2 is seller 
        role = retrieved_message.get("role",{})

        if role == 1 and (retrieved_message["type"] == "buyprojects.public.payment.fail"):
            message = (f"Buyer {buyer_id} payment has failed for the project")
        if role == 1 and (retrieved_message["type"] == "buyprojects.notify.payment.fail"):
            message = (f"Buyer {buyer_id} payment has failed for the project")
        return message

def police_notify_upcoming_milestone(retrieved_message):
    project_id = retrieved_message.get("project_id")
    task_id = retrieved_message.get("task_id")
    milestone_id = retrieved_message.get("milestone_id")
    message = ("f Project {project_id} for task {task_id} with milestone {milestone_id} is upcoming")

#communicate with the user microservice to retrieve users information
def retrieve_users_information():
    try:
        response = requests.get(MS_BASE_URL + "/users")
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print("this is the status_code retrieved from HTTP Error:" + status_code)

    data_object = response.json()
    role = data_object.get("data", {}).get("role")
    if role == "buyer":
        user_email_detail = "ownagersg+test@gmail.com"
    elif role == "verifier":
        user_email_detail = "ownagersg+test1@gmail.com"
    else:
        user_email_detail = "ownagersg+test2@gmail.com"
    return user_email_detail

def send_email_to_user(user_email, message, subject_retrieved):
    from_email = "zactao.work@gmail.com"
    to_emails = user_email
    subject = subject_retrieved
    plain_text_content = str(message)
    message = Mail(from_email, to_emails, subject, plain_text_content)
    try:
        sg = SendGridAPIClient(getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        # response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Invalid API key. Authentication failed. Please check your credentials")
        else:
            print("An error occurred:",e)
    else:
        print("Email has been successfully sent")


def on_queue_callback(channel, method, properties, body):
    try:
        SUBJECT = 'subject'
        data = json.loads(body)
        print("this is the method retrieved", method)
        pub_queue_routing_key = ".".join(method.routing_key.split(".")[-5:])
        for queue_name, binding_key in QUEUES.items():
            if pub_queue_routing_key == binding_key[ROUTING_KEY]:

                    subject = QUEUES[queue_name][SUBJECT]
                    print("this is the subject retrieved", subject)
                    print("this is the data printed", data)
                    # this is the data retrieved from the publisher
                    process_message(data, subject)      
        
    except Exception as err:
        logging.exception("Error processing message: %s", err)

if __name__ == "__main__":
    try:
        for queue_name, binding_key in QUEUES.items():
            channel_consume(connection=connection, channel=channel, host=RABBITMQ_HOSTNAME, port=RABBITMQ_PORT, exchangename=EXCHANGE, exchangetype=EXCHANGE_TYPE, 
                    queue=queue_name, on_message_callback=on_queue_callback)
        channel.start_consuming()
        print("consumed message on all queues")
    except KeyboardInterrupt:
        connection.close()

