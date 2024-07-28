import pika
import os

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
    )
    channel = connection.channel()

    # Declare a test queue
    queue_name = "test_queue"
    channel.queue_declare(queue=queue_name)

    # Send a test message
    test_message = "Hello RabbitMQ!"
    channel.basic_publish(exchange="", routing_key=queue_name, body=test_message)
    print(f"Sent '{test_message}' to queue '{queue_name}'")

    # Receive the message
    method_frame, header_frame, body = channel.basic_get(queue=queue_name)
    if method_frame:
        print(f"Received '{body.decode()}' from queue '{queue_name}'")
    else:
        print(f"No message received from queue '{queue_name}'")

    # Close connection
    connection.close()

except pika.exceptions.AMQPConnectionError as e:
    print(f"Error connecting to RabbitMQ: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
