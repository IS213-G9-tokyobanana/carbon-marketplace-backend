# Scheduler

### Description

Scheduler MS that will be responsible for scheduling the tasks to be executed by the workers. Only receives communication through AMQP

### Setting up

Follow these steps to install and set up this flask template.

1. Ensure docker engine is running

2. Docker compose up

```
docker compose up
```

### Testing
For windows users, change the `CRLF` to `LF` in the `start.sh` file
1. Check that the Deployed RabbitMQ is up and running
2. For testing of crontab, uncomment the comments with "Uncomment below for testing" in the `scheduler.py` file 
    2.1. These test lines are there so that a cronjob that does the same thing will start in 1 minute
3. Refer to Projects MS notion page below for the payload to consume from each queue and the expected result e.g. whether to publish to another queue or delete cron job