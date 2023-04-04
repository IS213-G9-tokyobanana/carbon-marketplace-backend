import json
import logging
import requests
from config.config import ( 
    EXCHANGE, USERS_BASE_URL, 
    SENDGRID_API_KEY, SENDGRID_FROM_EMAIL
)
from config.rabbitmq_setup import (
    connection, channel, QUEUES, VERIFIER_MESSAGES, SELLER_MESSAGES, BUYER_MESSAGES
)
from classes.MessageType import MessageType

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

VERIFIERS_URL = f'{USERS_BASE_URL}?role=verifier'

def consume_message(channel, method, properties, body):
    print(f'Received from routing key: {method.routing_key}', end='\n\n')
    # Get subject, get recipients, create message, send email
    try:
        payload = json.loads(body)
        print(f'payload: {payload}', end='\n\n')
        resource_id = payload['resource_id']
        type = payload['type']
        data = payload['data']

        if type == MessageType.PROJECT_CREATE.value: # Sends email to all verifiers
            print(f'Preparing email for {type}...', end='\n\n')
            project = data['project']
            subject = VERIFIER_MESSAGES[MessageType.PROJECT_CREATE.value]['subject']

            response = requests.get(VERIFIERS_URL).json()
            verifiers = response.get('data', [])
            print(f'verifiers: {verifiers}', end='\n\n')

            for verifier in verifiers:
                email = verifier.get('email')
                
                message = VERIFIER_MESSAGES[MessageType.PROJECT_CREATE.value]['message']
                message = message.format(recipient=verifier.get('name'), project_name= project.get('name'), project_id=project.get('id'))
                print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

                send_email(to_emails=email, message=message, subject=subject)
                print(f'Email sent to {email} for type {type}', end='\n\n')

        elif type == MessageType.MILESTONE_ADD.value: # Sends email to all verifiers
            print(f'Preparing email for {type}...', end='\n\n')
            project = data['project']
            milestone = project['milestones'][0]
            subject = VERIFIER_MESSAGES[type]['subject']

            response = requests.get(VERIFIERS_URL).json()
            verifiers = response.get('data', [])
            print(f'verifiers: {verifiers}', end='\n\n')

            for verifier in verifiers:
                email = verifier.get('email')
                
                message = VERIFIER_MESSAGES[type]['message']
                message = message.format(
                    recipient=verifier.get('name'), milestone_id=milestone.get('id'), milestone_name=milestone.get('name'),
                    project_id=project.get('id'), project_name=project.get('name'), due_date=milestone.get('due_date'))

                print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')
                send_email(to_emails=email, message=message, subject=subject)
                print(f'Email sent to {email} for type {type}', end='\n\n')
            

        elif type == MessageType.MILESTONE_UPCOMING.value: # Sends email to all verifiers
            print(f'Preparing email for {type}...', end='\n\n')
            project_id = data['project_id']
            milestone_id = data['milestone_id']
            subject = VERIFIER_MESSAGES[type]['subject']

            response = requests.get(VERIFIERS_URL).json()
            verifiers = response.get('data', [])
            print(f'verifiers: {verifiers}', end='\n\n')

            for verifier in verifiers:
                email = verifier.get('email')
                message = VERIFIER_MESSAGES[type]['message']
                message = message.format(
                    recipient=verifier.get('name'), milestone_id=milestone_id, project_id=project_id)

                print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')
                send_email(to_emails=email, message=message, subject=subject)
                print(f'Email sent to {email} for type {type}', end='\n\n')

        elif type == MessageType.PROJECT_VERIFY.value: # Sends email to seller
            print(f'Preparing email for {type}...', end='\n\n')
            project = data['project']
            subject = SELLER_MESSAGES[type]['subject']
            owner_id = project['owner_id']

            # notify seller
            print(f'Sending URL to users MS: {USERS_BASE_URL}/{owner_id}')
            response = requests.get(f'{USERS_BASE_URL}/{owner_id}').json()
            seller = response.get('data', [])
            print(f'seller: {seller}', end='\n\n')

            email = seller.get('email')
            print(f'seller email: {email}', end='\n\n')
            
            message = SELLER_MESSAGES[type]['message']
            message = message.format(
                recipient=seller.get('name'), project_id=project.get('id'), project_name=project.get('name'))
            print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

            send_email(to_emails=email, message=message, subject=subject)
            print(f'Email sent to {email} for type {type}', end='\n\n')

        elif type == MessageType.MILESTONE_PENALISE.value or type == MessageType.MILESTONE_REWARD.value: # Sends email to seller and all buyers of the milestone
            print(f'Preparing email for {type}...', end='\n\n')
            milestone_id = resource_id
            project = data['project']
            milestones = project['milestones']
            print(f'milestones: {milestones}', end='\n\n')
            milestone_penalised = list(filter(lambda m: m['id'] == milestone_id, milestones))
            if len(milestone_penalised) == 0:
                raise Exception(f'Invalid payload. Milestone penalised of resource_id {resource_id} does not match any milestone_id in project milestones passed in the payload')
            
            milestone_penalised = milestone_penalised[0]
            milestone_name = milestone_penalised.get('name')
            milestone_status = milestone_penalised.get('status')
            project_id = project.get('id')
            project_name = project.get('name')
            project_rating = project.get('rating')
            rating_action = 'penalised' if type == MessageType.MILESTONE_PENALISE.value else 'rewarded'

            subject = SELLER_MESSAGES[type]['subject']
            subject = subject.format(milestone_status=milestone_status)
            owner_id = project['owner_id']

            # notify seller
            print(f'Sending URL to users MS: {USERS_BASE_URL}/{owner_id}')
            response = requests.get(f'{USERS_BASE_URL}/{owner_id}').json()
            print(f'response after GET to {USERS_BASE_URL}/{owner_id}: {response}', end='\n\n')
            seller = response.get('data', [])
            print(f'seller: {seller}', end='\n\n')

            email = seller.get('email')
            print(f'seller email: {email}', end='\n\n')
            
            message = SELLER_MESSAGES[type]['message']
            message = message.format(
                recipient=seller.get('name'), milestone_id=milestone_id, milestone_name=milestone_name, milestone_status=milestone_status, rating_action=rating_action,
                  project_id=project_id, project_name=project_name, rating=project_rating)
            print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

            send_email(to_emails=email, message=message, subject=subject)
            print(f'Email sent to {email} for type {type}', end='\n\n')

            #notify all the buyers of that milestone
            print(f'Getting all buyers by milestone_id to users MS: {USERS_BASE_URL}?milestone_id={milestone_id}')
            response = requests.get(f'{USERS_BASE_URL}?milestone_id={milestone_id}').json()
            print(f'response after GET to {USERS_BASE_URL}?milestone_id={milestone_id}: {response}', end='\n\n')
            buyers = response.get('data', [])
            print(f'buyers: {buyers}', end='\n\n')

            for buyer in buyers:
                email = buyer.get('email')
                print(f'buyer email: {email}', end='\n\n')
                
                message = BUYER_MESSAGES[type]['message']
                message = message.format(
                    recipient=buyer.get('name'), milestone_id=milestone_id, milestone_name=milestone_name, milestone_status=milestone_status, rating_action=rating_action,
                      project_id=project_id, project_name=project_name, rating=project_rating)
                print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

                send_email(to_emails=email, message=message, subject=subject)
                print(f'Email sent to {email} for type {type}', end='\n\n')


        elif type == MessageType.PAYMENT_SUCCESS.value: # Sends email to seller and buyer
            print(f'Preparing email for {type}...', end='\n\n')
            buyer_id = data['buyer_id']
            seller_id = data['seller_id']
            milestone_id = data['milestone_id']
            subject = BUYER_MESSAGES[type]['subject']
            
            # notify buyer
            print(f'Sending URL to users MS: {USERS_BASE_URL}/{buyer_id}')
            response = requests.get(f'{USERS_BASE_URL}/{buyer_id}').json()
            print(f'response after GET to {USERS_BASE_URL}/{buyer_id}: {response}', end='\n\n')
            buyer = response.get('data', [])
            print(f'buyer: {buyer}', end='\n\n')

            email = buyer.get('email')
            
            message = BUYER_MESSAGES[type]['message']
            message = message.format(
                recipient=buyer.get('name'), milestone_id=milestone_id)
            print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

            send_email(to_emails=email, message=message, subject=subject)

            # notify seller
            subject = SELLER_MESSAGES[type]['subject']
            print(f'Sending URL to users MS: {USERS_BASE_URL}/{seller_id}')
            response = requests.get(f'{USERS_BASE_URL}/{seller_id}').json()
            print(f'response after GET to {USERS_BASE_URL}/{seller_id}: {response}', end='\n\n')
            seller = response.get('data', [])
            print(f'seller: {seller}', end='\n\n')

            email = seller.get('email')
            
            message = BUYER_MESSAGES[type]['message']
            message = message.format(
                recipient=seller.get('name'), milestone_id=milestone_id)
            print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

            send_email(to_emails=email, message=message, subject=subject)
            print(f'Email sent to {email} for type {type}', end='\n\n')

        elif type == MessageType.PAYMENT_FAILED.value: # Sends email to buyer
            print(f'Preparing email for {type}...', end='\n\n')
            buyer_id = data['buyer_id']
            milestone_id = data['milestone_id']
            subject = BUYER_MESSAGES[type]['subject']

            # notify buyer
            print(f'Sending URL to users MS: {USERS_BASE_URL}/{buyer_id}')
            response = requests.get(f'{USERS_BASE_URL}/{buyer_id}').json()
            print(f'response after GET to {USERS_BASE_URL}/{buyer_id}: {response}', end='\n\n')
            buyer = response.get('data', [])
            print(f'buyer: {buyer}', end='\n\n')

            email = buyer.get('email')
            
            message = BUYER_MESSAGES[type]['message']
            message = message.format(
                recipient=buyer.get('name'), milestone_id=milestone_id)
            print(f'Sending email TO {email} \t MESSAGE: {message}', end='\n\n')

            send_email(to_emails=email, message=message, subject=subject)
            print(f'Email sent to {email} for type {type}', end='\n\n')

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as err:
        logging.exception("Error processing message: %s", err)
        channel.basic_ack(delivery_tag=method.delivery_tag) # remove the unacknowledged message from the queue

        
def send_email(to_emails, message, subject):
    message = Mail(from_email=SENDGRID_FROM_EMAIL, to_emails=to_emails, subject=subject, plain_text_content=message)
    print(f'trying to send email from {SENDGRID_FROM_EMAIL} to {to_emails}', end='\n\n')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f'response.status_code: {response.status_code}')
        print("Email sent", end='\n\n')

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(
                "Invalid API key. Authentication failed. Please check your credentials"
            )
    except Exception as e:
        logging.exception(f'Uncaught exception {e}')
        

if __name__ == "__main__":
    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        for queue_name, binding_key in QUEUES.items():
            print(f"Monitoring binding queue {queue_name} on exchange {EXCHANGE} with binding key {binding_key}")
            channel.basic_consume(queue=queue_name, on_message_callback=consume_message, auto_ack=False)
        channel.start_consuming()
    except KeyboardInterrupt:
        print(' [*] Exiting...')

    except Exception as e:
        print("Uncaught exception:", e)

    finally:
        channel.stop_consuming()
        connection.close()
