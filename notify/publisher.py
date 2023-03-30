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
    body=json.dumps(
        {
            "resource_id": "58a460e1-4276-4e25-8c42-520efaca56af",
            "type": "milestone.penalise",
            "data": {
                "id": "a3cc8e03-07e4-4211-a029-431beed4ef87",
                "name": "100.5MW Wind Power Project in Madhya Pradesh, India",
                "owner_id": "3b08a327-42b2-4694-bbeb-f61ad526ec47",
                "description": "desc3",
                "types": ["carbon capture", "local green initiative (small project)"],
                "status": "verified",
                "created_at": "2023-03-28T09:09:35Z",
                "updated_at": "2023-03-28T09:10:57Z",
                "rating": 90.0,
                "milestones": {
                    "id": "58a460e1-4276-4e25-8c42-520efaca56af",
                    "name": "Generation of 180 GWh of clean electricity annually",
                    "description": "Generation of 180 GWh of clean electricity annually after the project has been implemented.",
                    "type": "Temporal",
                    "offsets_available": 50.0,
                    "offsets_total": 50.0,
                    "status": "rejected",
                    "created_at": "2023-03-28T09:09:35Z",
                    "updated_at": "2023-03-28T09:23:23Z",
                    "due_date": "2024-03-21T19:30:22Z",
                    "project_id": "a3cc8e03-07e4-4211-a029-431beed4ef87",
                },
            },
        }
    ),
)
print(" Sent notify service the message on penalise queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.project.verify",
    body=json.dumps(
        {
            "resource_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
            "type": "project.verify",
            "data": {
                "id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                "name": "100.5MW Wind Power Project in Madhya Pradesh, India",
                "owner_id": "3b08a327-42b2-4694-bbeb-f61ad526ec47",
                "description": "desc3",
                "types": ["carbon capture", "local green initiative (small project)"],
                "status": "Pending",
                "created_at": "2023-03-26T19:10:30Z",
                "updated_at": "2023-03-26T19:10:30Z",
                "rating": 100.0,
                "milestones": [
                    {
                        "id": "60af22a8-e44f-4300-95db-b776ae703848",
                        "name": "0.5 million tCO2e saved by year 3",
                        "description": "0.5 million tCO2e saved in 3 years after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2026-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "4f5c1fe9-8187-4115-9e1e-c698751b998e",
                        "name": "1 million tCO2e saved by year 6",
                        "description": "1 million tCO2e saved by year 6 after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2029-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "4119b4c1-b392-4e92-8e7a-801ebfdcebd3",
                        "name": "Generation of 180 GWh of clean electricity annually",
                        "description": "Generation of 180 GWh of clean electricity annually after the project has been implemented.",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2024-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "18d09220-bfed-4b98-874d-551eaa0af7f9",
                        "name": "1.23 million tCO2e saved by year 7",
                        "description": "1.23 million tCO2e saved by year 7 after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2030-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                ],
            },
        }
    ),
)

print(" Sent notify service the message on verify queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.milestone.add",
    body=json.dumps(
        {
            "resource_id": "48d727ec-4d74-466c-bc3a-f0e566792250",
            "type": "milestone.add",
            "data": {
                "id": "dd95aa97-f0b4-44c2-b069-22c3a4975f52",
                "name": "100.5MW Wind Power Project in Madhya Pradesh, India",
                "owner_id": "3b08a327-42b2-4694-bbeb-f61ad526ec47",
                "description": "desc3",
                "types": ["carbon capture", "local green initiative (small project)"],
                "status": "pending",
                "created_at": "2023-03-28T07:51:54Z",
                "updated_at": "2023-03-28T07:51:54Z",
                "rating": 100.0,
                "milestones": [
                    {
                        "id": "48d727ec-4d74-466c-bc3a-f0e566792250",
                        "name": "0.2 million tCO2e saved by year 2",
                        "description": "0.2 million tCO2e saved by year 2 after project launch",
                        "type": "Temporal",
                        "offsets_available": 20.0,
                        "offsets_total": 20.0,
                        "status": "pending",
                        "created_at": "2023-03-28T08:25:12Z",
                        "updated_at": "2023-03-28T08:25:12Z",
                        "due_date": "2025-03-21T09:31:23Z",
                        "project_id": "dd95aa97-f0b4-44c2-b069-22c3a4975f52",
                    }
                ],
            },
        }
    ),
)

# print(" Sent notify service the message on milestone add queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.project.create",
    body=json.dumps(
        {
            "resource_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
            "type": "project.create",
            "data": {
                "id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                "name": "100.5MW Wind Power Project in Madhya Pradesh, India",
                "owner_id": "3b08a327-42b2-4694-bbeb-f61ad526ec47",
                "description": "desc3",
                "types": ["carbon capture", "local green initiative (small project)"],
                "status": "Pending",
                "created_at": "2023-03-26T19:10:30Z",
                "updated_at": "2023-03-26T19:10:30Z",
                "rating": 100.0,
                "milestones": [
                    {
                        "id": "60af22a8-e44f-4300-95db-b776ae703848",
                        "name": "0.5 million tCO2e saved by year 3",
                        "description": "0.5 million tCO2e saved in 3 years after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2026-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "4f5c1fe9-8187-4115-9e1e-c698751b998e",
                        "name": "1 million tCO2e saved by year 6",
                        "description": "1 million tCO2e saved by year 6 after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2029-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "4119b4c1-b392-4e92-8e7a-801ebfdcebd3",
                        "name": "Generation of 180 GWh of clean electricity annually",
                        "description": "Generation of 180 GWh of clean electricity annually after the project has been implemented.",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2024-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                    {
                        "id": "18d09220-bfed-4b98-874d-551eaa0af7f9",
                        "name": "1.23 million tCO2e saved by year 7",
                        "description": "1.23 million tCO2e saved by year 7 after the launch of the windmill",
                        "type": "Temporal",
                        "offsets_available": 50.0,
                        "offsets_total": 50.0,
                        "status": "Pending",
                        "created_at": "2023-03-26T19:10:30Z",
                        "updated_at": "2023-03-26T19:10:30Z",
                        "due_date": "2030-03-21T09:30:00Z",
                        "project_id": "3a99ba93-6494-44fc-a3de-19bc5b9fbf6e",
                    },
                ],
            },
        }
    ),
)

print(" Sent notify service the message on project create queue")

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.police.notify.milestone.upcoming",
    body=json.dumps(
        {
            "resource_id": "274487fhsdbchb-23ecsdv",
            "type": "upcoming",
            "data": {"project_id": "1", "milestone_id": "2"},
        }
    ),
)

print("Send message on milestone upcoming queue")


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
