import base64
import os
import pathlib
import mimetypes
from typing import Any
from typing import Dict
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from tornado.web import HTTPError as TornadoHTTPError


class SimplifiedS3ContentsManager:

    """The current s3contents seems to be slow when there are multiple direcotries.
    This class is a simplified version which only implements the `get` function
    of the regular ContentsManager. This should be good enough to serve our needs.

    Based on my tests, this simplifiedS3ContentsManager is 6 times faster than
    s3contents.
    """

    avaiable_boto3_session_arg_names = [
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_session_token",
        "region_name",
        "endpoint_url",
        "profile_name",
    ]

    available_s3_arg_names = ["bucket", "prefix"]

    def __init__(
        self, bucket: str, prefix: Optional[str] = None, **kwargs: Dict[str, Any]
    ) -> None:
        self.session_kwargs = {
            key: kwargs[key]
            for key in self.avaiable_boto3_session_arg_names
            if key in kwargs
        }

        self.bucket = bucket
        self.prefix = prefix or ""

    @property
    def client(self):
        session_kwargs = self.session_kwargs.copy()
        endpoint_url = session_kwargs.pop("endpoint_url", None)
        session = boto3.session.Session(**session_kwargs)
        client = session.client(
            service_name="s3",
            endpoint_url=endpoint_url,
        )
        return client

    def is_folder(self, path):
        path = os.path.join(self.prefix, path)
        path = path.rstrip("/") + "/"
        if path == "/":
            path = ""

        r = self.client.list_objects(
            Bucket=self.bucket, Prefix=path, Delimiter="/", MaxKeys=1
        )
        return "Contents" in r or "CommonPrefixes" in r

    def list_folder(self, path):
        prefix = os.path.join(self.prefix, path).rstrip("/") + "/"
        if prefix == "/":
            prefix = ""
        result = []
        paginator = self.client.get_paginator("list_objects")
        page_iterator = paginator.paginate(
            Bucket=self.bucket,
            Delimiter="/",
            Prefix=prefix,
            PaginationConfig={"PageSize": 1000},
        )
        for data in page_iterator:
            contents = data.get("Contents")
            if contents:
                for content in contents:
                    if content["Key"] == prefix:
                        continue
                    name = pathlib.Path(content["Key"]).name
                    if not name.startswith("."):
                        result.append(
                            {
                                "name": name,
                                "path": str(
                                    pathlib.Path(content["Key"]).relative_to(
                                        self.prefix
                                    )
                                ),
                                "writable": True,
                                "last_modified": content["LastModified"],
                                "created": content["LastModified"],
                                "content": None,
                                "format": None,
                                "mimetype": None,
                                "type": "notebook"
                                if name.endswith(".ipynb")
                                else "file",
                            }
                        )
            common_prefixes = data.get("CommonPrefixes")
            if common_prefixes:
                for common_prefix in common_prefixes:
                    name = pathlib.Path(common_prefix["Prefix"]).name
                    result.append(
                        {
                            "name": name,
                            "path": str(
                                pathlib.Path(common_prefix["Prefix"]).relative_to(
                                    self.prefix
                                )
                            ),
                            "writable": True,
                            "last_modified": None,
                            "created": None,
                            "content": None,
                            "format": None,
                            "mimetype": None,
                            "type": "directory",
                        }
                    )
        return result

    def get(self, path, content, type=None, **kwargs):
        try:
            name = pathlib.Path(path).name
            if self.is_folder(path):
                return {
                    "name": name,
                    "path": path,
                    "writable": True,
                    "last_modified": None,
                    "created": None,
                    "content": self.list_folder(path) if content else None,
                    "format": "json",
                    "mimetype": None,
                    "type": "directory",
                }

            key = str(pathlib.Path(self.prefix) / path)
            obj = self.client.get_object(Bucket=self.bucket, Key=key)

            if path.endswith(".ipynb"):
                c = obj["Body"].read().decode("utf-8")
                return {
                    "name": name,
                    "path": path,
                    "writable": True,
                    "last_modified": obj["LastModified"],
                    "created": obj["LastModified"],
                    "content": None if not content else c,
                    "format": "json",
                    "mimetype": None,
                    "type": "notebook",
                }

            mimetype, _ = mimetypes.guess_type(name)
            content_s = None if not content else obj["Body"].read()

            if mimetype.startswith("text/"):
                format_ = "text"
            else:
                format_ = "base64"
                content_s = (
                    base64.b64encode(content_s).decode("ascii") if content else None
                )

            return {
                "name": name,
                "path": path,
                "writable": True,
                "last_modified": obj["LastModified"],
                "created": obj["LastModified"],
                "content": content_s,
                "format": format_,
                "mimetype": mimetype,
                "type": "file",
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise TornadoHTTPError(404, e.response["Error"]["Message"])
            else:
                raise TornadoHTTPError(500, e.response["Error"]["Message"])
