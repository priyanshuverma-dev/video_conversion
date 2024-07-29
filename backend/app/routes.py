# app/routes.py
import json
import uuid
from flask import Blueprint, request, jsonify
import os
from flask_cors import CORS
from minio import Minio

from . import rabbitmq

bp = Blueprint("routes", __name__)
CORS(app=bp)
# MinIO client
# TODO: change to minio:9000

bucket_name = "videos"

minio_client = Minio(
    os.getenv("MINIO_ROOT_USER", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "adminminio"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "adminminio"),
    secure=False,
)


rabbit_channel = rabbitmq.instance()


@bp.route("/upload", methods=["POST"])
def upload_file():
    email = request.form["email"]
    file = request.files["file"]

    if not file or not email:
        return jsonify({"error": "No file or email provided"}), 400

    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    filePath = os.path.join("app/static/uploads", filename)
    file.save(filePath)

    try:
        # Upload file to MinIO
        minio_client.fput_object("videos", filename, filePath)
        os.remove(filePath)

        # Send message to RabbitMQ
        rabbit_channel.basic_publish(
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
