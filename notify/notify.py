import json
import logging
import requests
from os import getenv
from dotenv import load_dotenv
from config import (
    RABBITMQ_HOSTNAME,
    RABBITMQ_PORT,
    EXCHANGE,
    EXCHANGE_TYPE,
    MS_BASE_URL
)
from amqp_setup import (
    connection,
    channel,
    QUEUES,
    message,
    channel_consume,
    message_buyer,
    message_seller
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

def process_message(data, queue_name, SUBJECT):
    retrieved_message = data
    subject_retrieved = SUBJECT
    result_message = format_message(queue_name, retrieved_message)
    retrieved_user_email = retrieve_users_information()
    send_email_to_user(retrieved_user_email, result_message, subject_retrieved)


def format_message(queue_name, retrieved_message):
    format_project_id = retrieved_message.get("data").get("milestones", {}).get("project_id")
    format_milestone_id = retrieved_message.get("data").get("milestones", {}).get("id")
    format_buyer_id = retrieved_message.get("data").get("buyer_id", {})
    format_seller_id = retrieved_message.get("data").get("seller_id",{})
    format_role = retrieved_message.get("data")

    for dict_queue_name, binding_key in QUEUES.items():
        if queue_name == dict_queue_name:
            message_retrieved = QUEUES[queue_name][message]
            new_message_retrieved = message_retrieved.format(project_id=format_project_id, milestone_id=format_milestone_id)
            if new_message_retrieved is None:
                if format_role == 1:
                    message_retrieved = QUEUES[queue_name][message_buyer]
                    new_message_retrieved = message_retrieved.format(buyer_id=format_buyer_id)
                else: 
                    message_retrieved = QUEUES[queue_name][message_seller]
                    new_message_retrieved = message_retrieved.format(seller_id=format_seller_id)
            else:
                return new_message_retrieved
            
            return new_message_retrieved


# communicate with the user microservice to retrieve users information
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
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(
                "Invalid API key. Authentication failed. Please check your credentials"
            )
        else:
            print("An error occurred:", e)
    else:
        print("Email has been successfully sent")


def on_queue_callback(channel, method, properties, body):
    try:
        SUBJECT = "subject"
        data = json.loads(body)
        queue_name = "_".join(method.routing_key.split(".")[-2:])
        subject = QUEUES[queue_name][SUBJECT]
        channel.basic_ack(delivery_tag=method.delivery_tag)
        # this is the data retrieved from the publisher
        process_message(data, queue_name, subject)
    except Exception as err:
        logging.exception("Error processing message: %s", err)


if __name__ == "__main__":
    try:
        for queue_name, binding_key in QUEUES.items():
            channel_consume(
                connection=connection,
                channel=channel,
                host=RABBITMQ_HOSTNAME,
                port=RABBITMQ_PORT,
                exchangename=EXCHANGE,
                exchangetype=EXCHANGE_TYPE,
                queue=queue_name,
                on_message_callback=on_queue_callback,
            )
        channel.start_consuming()
        print("consumed message on all queues")
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
