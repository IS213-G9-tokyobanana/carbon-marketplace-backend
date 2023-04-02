import json
import logging
import requests
from config import (
    RABBITMQ_HOSTNAME,
    RABBITMQ_PORT,
    EXCHANGE,
    EXCHANGE_TYPE,
    MS_BASE_URL,
    SENDGRID_API_KEY,
    SENDGRID_FROM_EMAIL,
    VERIFIERS_EMAILS
)
from amqp_setup import (
    connection,
    channel,
    QUEUES,
    message,
    channel_consume,
    message_buyer,
    message_seller, SUBJECT
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def callback(channel, method, properties, body):
    try:
        data = json.loads(body)
        queue_name = "_".join(method.routing_key.split(".")[-2:])
        queue_name = "notify_" + queue_name

        email_subject = QUEUES[queue_name][SUBJECT]
        # this is the data retrieved from the publisher
        process_message(data, queue_name, email_subject)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as err:
        logging.exception("Error processing message: %s", err)

def process_message(data, queue_name, SUBJECT):
    if queue_name == "notify_payment_success":
        buyer_id = data.get("data").get("buyer_id", {})
        seller_id = data.get("data").get("seller_id", {})

        retrieved_email_buyer, retrieved_role_buyer = retrieve_user_email(buyer_id)
        result_message = format_message(data, queue_name, retrieved_role_buyer)
        send_email_to_user(retrieved_email_buyer, result_message, SUBJECT)

        retrieved_email_seller, retrieved_role_seller = retrieve_user_email(seller_id)
        result_message = format_message(data, queue_name, retrieved_role_seller)
        send_email_to_user(retrieved_email_seller, result_message, SUBJECT)

    elif queue_name == "notify_payment_failed":
        buyer_id = data.get("data").get("buyer_id", {})
        retrieved_email_buyer, retrieved_role_buyer = retrieve_user_email(buyer_id)
        result_message = format_message(data, queue_name, retrieved_role_buyer)
        send_email_to_user(retrieved_email_buyer, result_message, SUBJECT)

    elif queue_name == "notify_milestone_add" or queue_name == "notify_project_create" or queue_name == "notify_milestone_upcoming":
        verifiers_emails = get_all_verifiers()
        for email in verifiers_emails:
            result_message = format_message(data, queue_name, retrieved_role="verifier")
            send_email_to_user(email, result_message, SUBJECT)
            
    elif queue_name == "notify_project_verify":
        owner_id = data.get("data").get("owner_id", {})
        retrieved_email, retrieved_role = retrieve_user_email(owner_id)
        result_message = format_message(data, queue_name, retrieved_role)
        send_email_to_user(retrieved_email, result_message, SUBJECT)
 
def get_all_verifiers():
    response = requests.get(VERIFIERS_EMAILS)
    data_object = response.json()
    verifiers_emails = []
    payload = data_object.get("data", {})
    for item in payload:
        verifiers_emails.append(item["email"])
    return verifiers_emails

# communicate with the user microservice to retrieve users information
def retrieve_user_email(id):
    try:
        get_user_url = "".join([MS_BASE_URL, id])
        print(get_user_url)
        response = requests.get(get_user_url)
        response.raise_for_status()
        #handles 404,403 and 500 error
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print("this is the status_code retrieved from HTTP Error:", status_code)
        if status_code == 404:
            print("User not found")
    data_object = response.json()
    user_email = data_object.get("data", {}).get("email")
    retrieved_role = data_object.get("data").get("type", {})
    return (user_email, retrieved_role)

def format_message(data, queue_name, retrieved_role):
    if queue_name == "notify_ratings_reward" or queue_name == "notify_ratings_penalise":
        format_resource_id = data.get("project",{}).get("id", {})
        format_milestone_id = data.get("data").get("resource_id", {})
    elif queue_name == "notify_milestone_upcoming":
        format_resource_id = data.get("data").get("project_id", {})
        format_milestone_id = data.get("data").get("milestone_id", {})
    elif queue_name == "notify_payment_success":
        format_buyer_id = data.get("data").get("buyer_id", {})
        format_seller_id = data.get("data").get("seller_id",{})
    elif queue_name == "notify_payment_failed":
        format_buyer_id = data.get("data").get("buyer_id", {})
    elif queue_name == "notify_milestone_add" or queue_name == "notify_project_create" or queue_name == "notify_project_verify":
        format_resource_id = data.get("project",{}).get("id", {})


    if queue_name in QUEUES:
        queue_data = QUEUES[queue_name]
    message_retrieved = queue_data.get(message)

    if message_retrieved is not None:
        new_message_retrieved = message_retrieved.format(
            project_id=format_resource_id,
            milestone_id=format_milestone_id
        )
        if new_message_retrieved is not None:
            return new_message_retrieved
    elif retrieved_role == "buyer":
        message_retrieved = queue_data.get(message_buyer)
        if message_retrieved is not None:
            return message_retrieved.format(buyer_id=format_buyer_id)
    elif retrieved_role == "seller":
        message_retrieved = queue_data.get(message_seller)
        if message_retrieved is not None:
            return message_retrieved.format(seller_id=format_seller_id)
        
def send_email_to_user(user_email, message, subject_retrieved):
    from_email = SENDGRID_FROM_EMAIL
    to_emails = user_email
    subject = subject_retrieved
    plain_text_content = str(message)
    message = Mail(from_email, to_emails, subject, plain_text_content)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print("Email has been successfully sent")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(
                "Invalid API key. Authentication failed. Please check your credentials"
            )
        else:
            print("An error occurred:", e)
        

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
                on_message_callback=callback,
            )
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
