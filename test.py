from minio import Minio
import pika
import os


def test_rabbitmq_connection():
    minio_client = Minio(
        "localhost:9000",
        access_key=os.getenv("MINIO_ROOT_USER", "adminminio"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "adminminio"),
        secure=False,
    )

    l = minio_client.list_buckets()
    print(l)


if __name__ == "__main__":
    test_rabbitmq_connection()
