# app/routes.py
import json
import uuid
import time
from flask import Blueprint, request, jsonify
import os
from minio import Minio
import pika

bp = Blueprint("routes", __name__)

# MinIO client
# TODO: change to minio:9000
minio_client = Minio(
    os.getenv("MINIO_ROOT_USER", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "adminminio"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "adminminio"),
    secure=False,
)


# Initialize RabbitMQ connection
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))

for i in range(5):  # Retry up to 5 times
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
        )
        channel = connection.channel()
        channel.queue_declare(queue="video_processing")
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"Attempt {i+1}: Unable to connect to RabbitMQ, retrying in 5 seconds...")
        time.sleep(5)
else:
    raise Exception("Failed to connect to RabbitMQ after several attempts")

print("Connected to RabbitMQ")


@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files or "email" not in request.form:
        return jsonify({"error": "No file or email provided"}), 400

    file = request.files["file"]
    filename = f"{uuid.uuid4()}_{file.filename}"
    email = request.form["email"]
    filePath = os.path.join("app/static/uploads", filename)
    file.save(filePath)
    try:
        # Upload file to MinIO
        minio_client.fput_object("videos", filename, filePath)

        # Send message to RabbitMQ
        channel.basic_publish(
            exchange="",
            routing_key="video_processing",
            body=json.dumps({"filename": filename, "email": email}),
        )
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        print(e)
        if os.path.exists(filePath):
            os.remove(filePath)
        return jsonify({"message": "Failed to add in queue."}), 500
