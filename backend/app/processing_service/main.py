# processing_service.py

import json
import os
import smtplib
import logging
import moviepy.editor as mp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from minio import Minio, S3Error

from .. import rabbitmq


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MinIO client
minio_client = Minio(
    os.getenv("MINIO_HOST", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "adminminio"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "adminminio"),
    secure=False,
)


rabbit_channel = rabbitmq.instance()


def process_video(ch, method, properties, body):
    data = json.loads(body)
    filename = data["filename"]
    email = data["email"]

    try:
        # Download video from MinIO
        minio_client.fget_object("videos", filename, f"/tmp/{filename}")
        logger.info(f"Downloaded {filename} from MinIO")

        # Convert video to audio
        video = mp.VideoFileClip(f"/tmp/{filename}")
        audio_filename = f'{filename.rsplit(".", 1)[0]}.mp3'
        video.audio.write_audiofile(f"/tmp/{audio_filename}")
        logger.info(f"Converted {filename} to {audio_filename}")

        # Upload audio to MinIO
        minio_client.fput_object("audios", audio_filename, f"/tmp/{audio_filename}")
        logger.info(f"Uploaded {audio_filename} to MinIO")

        # create a downloadable link
        download_url = minio_client.get_presigned_url(
            "GET",
            bucket_name="audios",
            object_name=audio_filename,
        )
        logger.info(f"Generated download URL: {download_url}")

        # Send email notification
        send_email(email, audio_url=download_url, success=True)
        logger.info(f"Sent success email to {email}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        try:
            minio_client.remove_object("videos", filename)
        except S3Error as remove_err:
            logger.error(f"Failed to remove {filename} from MinIO: {remove_err}")
        send_email(email, audio_url="", success=False)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def send_email(email, audio_url, success):
    msg = MIMEMultipart()
    msg["From"] = "converter@mail.com"
    msg["To"] = email

    if not success:
        msg["Subject"] = "Important: Failed to convert video to audio"
        body = "Please try again to convert your video to audio by uploading again"
    else:
        msg["Subject"] = "Your audio file is ready"
        body = f"You can download your audio file from the following link: {audio_url}"

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(
            os.getenv("EMAIL_HOST", "localhost"), os.getenv("EMAIL_PORT", 1025)
        )
        server.sendmail("converter@mail.com", email, msg.as_string())
        logger.info(f"Sent email to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
    finally:
        server.quit()


rabbit_channel.basic_consume(
    queue="video_processing", on_message_callback=process_video
)

logger.info(" [*] Waiting for messages. To exit press CTRL+C")
try:
    rabbit_channel.start_consuming()
except Exception as e:
    logger.error(f"Error in RabbitMQ consuming: {e}")
finally:
    if not rabbit_channel.is_closed:
        rabbit_channel.close()
