This MS listens on project.verify, milestone.add, offsets.rollback and offsets.reserve queue. When a message comes in to this queue, the search will be updated accordingly.

## Deployment
Run the following command to deploy the search microservice:
```bash
$ docker-compose up
```

## Testing
I have also included a folder called "rabbitMQ test payload", within it contains the payload to use with RabbitMQ on their respective queues. Everytime you publish to each of the queues, you can go over to the search UI to see the changes.

1. Go to http://localhost:7700 to access the search microservice.
2. Go to the RabbitMQ project_verify queue and send the payload in the file "Project[x].json". This populates the search with 2 new projects.
3. Go to the RabbitMQ milestone_add queue and send the payload in the file "AddMilestone.json". This adds one new milestone to one of the projects
4. Go to the RabbitMQ offsets_reserve queue and send the payload in the file "OffsetReserve.json". This updates the offset available for milestones.
5. Go to the RabbitMQ offsets_rollback queue and send the payload in the file "OffsetRollback.json". This resets the available offset for the milestones.