# Scheduler

### Description

Scheduler MS that will be responsible for scheduling the tasks to be executed by the workers. Only receives communication through AMQP



### Pre-requisites

To be able to run/test this MS, the rabbitMQ container must be running.
Ensure that the rabbitMQ container is running before testing scheduler.


### Setting up

Follow these steps to install and set up this flask template.

1. Ensure docker engine is running

2. Spin up the container

```
docker compose up
```

### Testing

1. Check that  the rabbitMQ Queues and Exchanges have bee created
2. On rabbitMQ UI got to under topic_exchange and publish a message to the topic exchange to test each of the queues
