import os
import time

import pika

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
# Initialize RabbitMQ connection


def instance():
    for i in range(5):  # Retry up to 5 times
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
            )
            channel = connection.channel()
            channel.queue_declare(queue="video_processing")
            break
        except pika.exceptions.AMQPConnectionError:
            print(
                f"Attempt {i+1}: Unable to connect to RabbitMQ, retrying in 5 seconds..."
            )
            time.sleep(5)
    else:
        raise Exception("Failed to connect to RabbitMQ after several attempts")

    print("Connected to RabbitMQ")

    return channel
