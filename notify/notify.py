import json
import logging
import requests
from os import getenv
from dotenv import load_dotenv
from amqp_setup import RABBITMQ_HOSTNAME, RABBITMQ_PORT, \
    connection, channel, \
    RABBITMQ_HOSTNAME, RABBITMQ_PORT, EXCHANGE, EXCHANGE_TYPE, QUEUES, SUBJECT, MS_BASE_URL, channel_consume

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()
def process_message(data, SUBJECT):
    # send message to user (the message is an email)
    #sample message data 
    try: 
        message = data
        subject_retrieved = SUBJECT
        retrieved_user_email = retrieve_users_information()
        send_email_to_user(retrieved_user_email, message, subject_retrieved)
    except KeyError:
        print("The subject does not exist in the dictionary")
        

def retrieve_users_information():
    try:
        response = requests.get(MS_BASE_URL + "/users")
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print("this is the status_code retrieved from HTTP Error:" + status_code)

    data_object = response.json()
    print("this is the data object retrieved", data_object)
    role = data_object.get("data", {}).get("role")
    if role == "buyer":
        user_email_detail = "ownagersg+test@gmail.com"
    if role == "verifier":
        user_email_detail = "ownagersg+test1@gmail.com"
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
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Invalid API key. Authentication failed. Please check your credentials")
        else:
            print("An error occurred:",e)
    else:
        print("Email has been successfully sent")


def on_queue_callback(channel, method, properties, body):
    try:
        data = json.loads(body)
        
        if method.routing_key == "events.projects.public.project.create":
            SUBJECT = "Project has been penalised"
        elif method.routing_key == "events.projects.public.ratings.reward":
            SUBJECT = "Project has been rewarded"
        elif method.routing_key == "events.projects.public.ratings.penalise":
            SUBJECT = "Project has been penalised"
        elif method.routing_key == "events.projects.public.project.verify":
            SUBJECT = "Project has been verified"
        elif method.routing_key == "events.projects.public.milestone.add":
            SUBJECT = "Milestone has been added"
        elif method.routing_key == "events.projects.public.project.create":
            SUBJECT = "Project has been created"
        elif method.routing_key == "events.buyprojects.notify.payment.success":
            SUBJECT = "Payment has been successful"
        elif method.routing_key == "events.buyprojects.public.payment.failed":
            SUBJECT = "Payment made failed"
        elif method.routing_key == "events.buyprojects.notify.payment.failed":
            SUBJECT = "Payment made failed"
        elif method.routing_key == "events.police.notify.milestone.upcoming":
            SUBJECT = "Upcoming Milestone"
        else:
            SUBJECT = "No subject found"

        print("this is data", data.get("status"))
        #process message for input received from temporal service
        process_message(data, SUBJECT)
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

