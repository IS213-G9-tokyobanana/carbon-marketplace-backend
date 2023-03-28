import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="13.229.231.31", port=5672)
)
channel = connection.channel()

channel.basic_publish(
    exchange="topic_exchange",
    routing_key="events.projects.public.ratings.reward",
    # sent user email
    body=json.dumps(
        {
            "resource_id": "ec2b5bc8-19d6-4a4f-a5e5-7b42b7d4851e",
            "type": "milestone.reward",
            "data": {
                "id": "a3cc8e03-07e4-4211-a029-431beed4ef87",
                "name": "100.5MW Wind Power Project in Madhya Pradesh, India",
                "owner_id": "3b08a327-42b2-4694-bbeb-f61ad526ec47",
                "description": "desc3",
                "types": ["carbon capture", "local green initiative (small project)"],
                "status": "verified",
                "created_at": "2023-03-28T09:09:35Z",
                "updated_at": "2023-03-28T09:10:57Z",
                "rating": 110.0,
                "milestones": {
                    "id": "ec2b5bc8-19d6-4a4f-a5e5-7b42b7d4851e",
                    "name": "0.5 million tCO2e saved by year 3",
                    "description": "0.5 million tCO2e saved in 3 years after the launch of the windmill",
                    "type": "Temporal",
                    "offsets_available": 29.400000000000002,
                    "offsets_total": 50.0,
                    "status": "met",
                    "created_at": "2023-03-28T09:09:35Z",
                    "updated_at": "2023-03-28T09:18:58Z",
                    "due_date": "2026-03-21T09:30:00Z",
                    "project_id": "a3cc8e03-07e4-4211-a029-431beed4ef87",
                },
            },
        }
    ),
)

print(" Sent notify service the message on reward queue")

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

connection.close()
