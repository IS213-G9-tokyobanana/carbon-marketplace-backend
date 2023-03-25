# Scheduler

### Description

Scheduler MS that will be responsible for scheduling the tasks to be executed by the workers. Only receives communication through AMQP

### Setting up

Follow these steps to install and set up this flask template.

1. Ensure docker engine is running

2. Spin up the container

```
docker compose up
```

### Testing

1. Check that the Deployed RabbitMQ is up and running
2. For testing of crontab, Please change lines 55, 86, 92 accordingly to test each of the different queues.
    2.1. These test lines are there so that a cronjob that does the same thing will start in 1 minute
3. On rabbitMQ UI got to under topic_exchange and publish a message to the topic exchange to test each of the queues
4. On rabbitMQ UI, go to the queue "task_triggered_topic_queue" to see that there are messages queued once the cronjob runs
