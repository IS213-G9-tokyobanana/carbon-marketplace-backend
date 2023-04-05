# RabbitMQ

### Description

On docker compose up, a RabbitMQ container with pre-defined exchange will be spun up. This is done through configuring the official RabbitMQ v3 image using rabbitmq.conf file.

https://stackoverflow.com/questions/47153025 add-exchanges-in-rabbitmq-with-dockerfile-or-docker-compose

### Setting up

Follow these steps to install and set up this flask template.

1. Ensure docker engine is running

2. Spin up the container

```
docker compose up
```

### Configuration

To configure which exchange type to use or how many exchanges to start up, edit the rabbitmq_config.sh file after this command.

```
python3 /tmp/rabbitmqadmin --host ${RABBITMQ_HOST} declare exchange name=topic_exchange type=topic
```

If you have previously ran commands to bring up container, you will need to rebuild the container by running

```
docker compose down && docker compose up --build
```

#### Auto creation of exchange on startup

Refer to https://stackoverflow.com/a/71035760/20545838.

Config and definition files are found at {PROJECT_ROOT}/src/rabbitmq.

Example definitions.json:

```json
{
  "queues": [
    {
      "name": "externally_configured_queue",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-queue-type": "classic"
      }
    }
  ],
  "exchanges": [
    {
      "name": "externally_configured_exchange",
      "vhost": "/",
      "type": "direct",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    }
  ],
  "bindings": [
    {
      "source": "externally_configured_exchange",
      "vhost": "/",
      "destination": "externally_configured_queue",
      "destination_type": "queue",
      "routing_key": "externally_configured_queue",
      "arguments": {}
    }
  ]
}
```

Example rabbitmq.conf:

```conf
management.load_definitions = /etc/rabbitmq/definitions.json
```

### Test

To test, go to http://localhost:15672/#/exchanges. You should observe a newly declared exchange called topic_exchange.
