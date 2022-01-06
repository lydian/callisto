import os

import boto3
import pytest
from moto import mock_s3

from tests.utils.create_s3 import upload_fixture_to_s3
from tests.utils.create_s3 import set_env


@pytest.fixture(scope="session")
def bucket():
    return "test-bucket"


@pytest.fixture(scope="session")
def env():
    new_env, old_env = set_env()
    yield
    os.environ.update(old_env)
    for key in set(new_env.keys()) - set(old_env.keys()):
        del os.environ[key]


@pytest.fixture(scope="session")
def set_s3(env, bucket):
    with mock_s3():
        client = boto3.client("s3", region_name="us-east-1")
        upload_fixture_to_s3(client)
        yield


@pytest.fixture
def s3(set_s3):
    client = boto3.client("s3", region_name="us-east-1")
    yield client
