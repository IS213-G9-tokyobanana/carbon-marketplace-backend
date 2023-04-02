from config.rabbitmq_setup import (
    connection, channel, TOPIC_EXCHANGE_NAME, BINDING_KEYS, 
)
import json
from scheduler import schedule_jobs

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f'received message from method.routing_key: {method.routing_key}')
        schedule_jobs(message)
    except json.decoder.JSONDecodeError as e:
        print("--NOT JSON:", e)
        print("--DATA:", body)
    


if __name__ == '__main__':
    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        for QUEUE_NAME, BINDING_KEY in BINDING_KEYS.items():
            print(f"Monitoring binding queue {QUEUE_NAME} on exchange {TOPIC_EXCHANGE_NAME}")
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except KeyboardInterrupt:
        print(' [*] Exiting...')

    except Exception as e:
        print("Uncaught exception:", e)

    finally:
        channel.stop_consuming()
        connection.close()
        