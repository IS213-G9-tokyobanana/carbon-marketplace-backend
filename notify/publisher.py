import pika
import json
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="13.229.231.31", port=5672)
)
channel = connection.channel()

with open('tests/milestone_add.json') as milestone_add:
    milestone_add_data = json.load(milestone_add)

with open('tests/milestone_upcoming.json') as milestone_upcoming:
    milestone_upcoming_data = json.load(milestone_upcoming)

with open('tests/milestone_penalise.json') as milestone_penalise:
    milestone_penalise_data = json.load(milestone_penalise) 

with open('tests/milestone_reward.json') as milestone_reward:
    milestone_reward_data = json.load(milestone_reward)

with open('tests/payment_failed.json') as payment_failed:
    payment_failed_data = json.load(payment_failed)

with open('tests/payment_success.json') as payment_success:
    payment_success_data = json.load(payment_success)

with open('tests/project_create.json') as project_create:
    project_create_data = json.load(project_create)

with open('tests/project_verify.json') as project_verify:
    project_verify_data = json.load(project_verify)

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.ratings.reward",
    # sent user email
    body=json.dumps(milestone_reward_data)
)

print("Sent notify service the message on reward queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.ratings.penalise",
    body=json.dumps(milestone_penalise_data)
)
print(" Sent notify service the message on penalise queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.project.verify",
    body=json.dumps(project_verify_data)
)

print(" Sent notify service the message on project verify queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.milestone.add",
    body=json.dumps(milestone_add_data),
)

print(" Sent notify service the message on milestone add queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.project.create",
    body=json.dumps(project_create_data),
)

print(" Sent notify service the message on project create queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.police.notify.milestone.upcoming",
    body=json.dumps(milestone_upcoming_data),
)

print("Send notify service the message on milestone upcoming queue")


channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.buyprojects.notify.payment.success",
    body=json.dumps(payment_success_data),
)

print("Send notify service the message on success payment buyprojects queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.buyprojects.notify.payment.failed",
    body=json.dumps(payment_failed_data),
)

print("Send notify service the message on failed payment buyprojects queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.buyprojects.public.payment.failed",
    body=json.dumps(payment_failed_data),
)

print("Send notify service the message on failed payment rollback buyprojects queue")


connection.close()
