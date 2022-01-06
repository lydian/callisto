import os
import pathlib

import boto3


BUCKET = "test-bucket"


def set_env():
    preset_env = {
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    old_env = {key: os.environ[key] for key in preset_env if key in os.environ}
    os.environ.update(preset_env)
    return preset_env, old_env


def upload_fixture_to_s3(client):
    client.create_bucket(Bucket=BUCKET)
    for root, _, files in os.walk("tests/fixtures/notebooks"):
        for name in files:
            path = pathlib.Path(root) / name
            key = path.relative_to("tests/fixtures/notebooks")
            print(path, "->", key)
            client.upload_file(str(path), BUCKET, str(key))


def create_files():
    set_env()
    client = boto3.client(
        "s3", region_name="us-east-1", endpoint_url="http://localhost:3000"
    )
    upload_fixture_to_s3(client)
