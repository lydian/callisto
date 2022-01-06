import base64
from unittest import mock

import pytest
from tornado.web import HTTPError

from callisto.contents_managers.s3 import SimplifiedS3ContentsManager


class TestSimplifiedS3ContentsManager:
    @pytest.fixture
    def mock_session(self):
        with mock.patch("boto3.session.Session") as m:
            yield m

    def test_client(self, mock_session):
        manager = SimplifiedS3ContentsManager(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            bucket="test-bucket",
            endpoint_url="http://example.com:3000/",
        )
        assert manager.client == mock_session.return_value.client.return_value
        assert manager.bucket == "test-bucket"
        assert manager.prefix == ""

        mock_session.assert_called_once_with(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
        )
        mock_session.return_value.client.assert_called_once_with(
            service_name="s3", endpoint_url="http://example.com:3000/"
        )

    @pytest.fixture
    def manager(self, s3):
        manager = SimplifiedS3ContentsManager(
            bucket="test-bucket",
            prefix="",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        return manager

    @pytest.mark.parametrize(
        "path,is_folder",
        [
            ("nested_folders", True),
            ("test-notebook.ipynb", False),
            ("not-exist", False),
        ],
    )
    def test_is_folder(self, manager, path, is_folder):
        assert manager.is_folder(path) is is_folder

    def test_list_folder(self, manager):
        assert sorted(
            (item["name"], item["path"], item["type"])
            for item in manager.list_folder("")
        ) == sorted(
            [
                ("test-notebook.ipynb", "test-notebook.ipynb", "notebook"),
                ("nested_folders", "nested_folders", "directory"),
            ]
        )

        assert sorted(
            (item["name"], item["path"], item["type"])
            for item in manager.list_folder("nested_folders")
        ) == sorted(
            [
                ("callisto-256.png", "nested_folders/callisto-256.png", "file"),
                ("data.csv", "nested_folders/data.csv", "file"),
            ]
        )

    @pytest.fixture
    def mock_list_folder(self, manager):
        with mock.patch.object(manager, "list_folder") as m:
            yield m

    @pytest.mark.parametrize("has_content", [True, False])
    def test_get_directory(self, manager, has_content, mock_list_folder):
        assert manager.get("nested_folders", content=has_content) == {
            "name": "nested_folders",
            "path": "nested_folders",
            "content": mock_list_folder.return_value if has_content else None,
            "writable": True,
            "type": "directory",
            "created": None,
            "last_modified": None,
            "mimetype": None,
            "format": "json",
        }

    @pytest.mark.parametrize("has_content", [True, False])
    def test_get_text_file(self, manager, has_content):
        with open("tests/fixtures/notebooks/nested_folders/data.csv", "rb") as f:
            expected_content = f.read()

        result = manager.get("nested_folders/data.csv", content=has_content)

        expected_result = {
            "name": "data.csv",
            "path": "nested_folders/data.csv",
            "content": expected_content if has_content else None,
            "mimetype": "text/csv",
            "type": "file",
            "format": "text",
            "writable": True,
        }
        for key, expected_value in expected_result.items():
            assert result[key] == expected_value

    @pytest.mark.parametrize("has_content", [True, False])
    def test_get_non_text_file(self, manager, has_content):
        with open(
            "tests/fixtures/notebooks/nested_folders/callisto-256.png", "rb"
        ) as f:
            expected_content = base64.b64encode(f.read()).decode("ascii")

        result = manager.get("nested_folders/callisto-256.png", content=has_content)

        expected_result = {
            "name": "callisto-256.png",
            "path": "nested_folders/callisto-256.png",
            "content": expected_content if has_content else None,
            "mimetype": "image/png",
            "type": "file",
            "format": "base64",
            "writable": True,
        }
        for key, expected_value in expected_result.items():
            assert result[key] == expected_value

    @pytest.mark.parametrize("has_content", [True, False])
    def test_get_notebook(self, manager, has_content):
        with open("tests/fixtures/notebooks/test-notebook.ipynb", "r") as f:
            expected_content = f.read()

        result = manager.get("test-notebook.ipynb", content=has_content)

        expected_result = {
            "name": "test-notebook.ipynb",
            "path": "test-notebook.ipynb",
            "content": expected_content if has_content else None,
            "mimetype": None,
            "type": "notebook",
            "format": "json",
            "writable": True,
        }
        for key, expected_value in expected_result.items():
            assert result[key] == expected_value

    @pytest.mark.parametrize("has_content", [True, False])
    def test_get_file_not_found(self, manager, has_content):
        with pytest.raises(HTTPError):
            manager.get("test", content=has_content)
