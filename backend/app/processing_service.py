# processing_service.py

import json
import os
import smtplib
import time
import moviepy.editor as mp
import pika
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from minio import Minio

# Initialize MinIO client
minio_client = Minio(
    os.getenv("MINIO_HOST", "localhost:9000"),
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


def process_video(ch, method, properties, body):
    data = json.loads(body)
    filename = data["filename"]
    email = data["email"]

    try:
        # Download video from MinIO
        minio_client.fget_object("videos", filename, f"/tmp/{filename}")

        # Convert video to audio
        video = mp.VideoFileClip(f"/tmp/{filename}")
        audio_filename = f'{filename.rsplit(".", 1)[0]}.mp3'
        video.audio.write_audiofile(f"/tmp/{audio_filename}")

        # Upload audio to MinIO
        minio_client.fput_object("audios", audio_filename, f"/tmp/{audio_filename}")

        # create a downloadable link
        download_url = minio_client.get_presigned_url(
            "GET",
            bucket_name="audios",
            object_name=audio_filename,
        )

        # Send email notification
        send_email(email, audio_url=download_url, success=True)

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        minio_client.delete_object_tags("videos", filename)
        print(f"Failed to convert video try again. ERROR:{e}")
        send_email(email, "", success=False)


def send_email(email, audio_url, success):
    msg = MIMEMultipart()
    msg["From"] = "converter@mail.com"
    msg["To"] = email

    if success is not True:
        msg["Subject"] = "Important: Failed to convert video to audio"
        body = "Please try again to convert your video to audio by uploading again"
    else:
        msg["Subject"] = "Your audio file is ready"
        body = f"You can download your audio file from the following link: {audio_url}"

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(
        os.getenv("EMAIL_HOST", "localhost"), os.getenv("EMAIL_PORT", 1025)
    )
    server.sendmail("converter@mail.com", email, msg.as_string())
    server.quit()


channel.basic_consume(queue="video_processing", on_message_callback=process_video)

print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
