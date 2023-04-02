#!/bin/bash

RABBITMQ_HOST=${RABBITMQ_HOST:-"rabbitmq3"}

attempts=0
until wget http://${RABBITMQ_HOST}:15672/cli/rabbitmqadmin -O /tmp/rabbitmqadmin || [[ ${attempts} -eq 5 ]]; do
   sleep 10
   attempts=$((attempts + 1))
done

# Create the topic exchange
python3 /tmp/rabbitmqadmin --host ${RABBITMQ_HOST} declare exchange name=topic_exchange type=topic

# Add more exchange here
