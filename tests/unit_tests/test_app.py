import base64
import random
import json
from unittest import mock

import pytest
from werkzeug.exceptions import NotFound

from callisto.app import app
from callisto.app import configure_app


@pytest.fixture
def mock_loader():
    with mock.patch("callisto.app.ContentsLoader") as m:
        yield m.return_value


@pytest.fixture
def mock_config():
    with mock.patch("callisto.app.CallistoConfig") as m:
        yield m.load_from_config_file.return_value


def test_configure_app(mock_config, mock_loader):
    configure_app(app)
    assert app.callisto_config == mock_config
    assert app.contents_loader == mock_loader


@pytest.fixture
def client(mock_loader, mock_config):
    configure_app(app)
    with app.test_client() as c:
        yield c


@pytest.mark.parametrize("path", ["/", "/some/path", "/private/path"])
def test_index_success(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize(
    "path,expected_search_path",
    [("/api/info/<root>", ""), ("/api/info/some/path", "some/path")],
)
def test_info(client, mock_loader, path, expected_search_path):
    mock_loader.info.return_value = {"some": "value"}
    r = client.get(path)
    assert r.status_code == 200
    assert json.loads(r.data) == {"some": "value"}
    mock_loader.info.assert_called_once_with(expected_search_path)


@pytest.mark.parametrize(
    "path,expected_search_path",
    [("/api/get/<root>", ""), ("/api/get/some/path", "some/path")],
)
def test_list(client, mock_loader, path, expected_search_path):
    def make_item(type_, name):
        return {"type": type_, "name": name}

    folders = [make_item("directory", f"d_{i}") for i in range(5)]
    files = [make_item("file", f"f_{i}") for i in range(3)]
    items = folders + files
    random.shuffle(items)
    mock_loader.get.return_value = {"type": "directory", "content": items}
    r = client.get(path)
    assert r.status_code == 200
    contents = json.loads(r.data)
    assert contents["content"] == folders + files
    mock_loader.get.assert_called_once_with(expected_search_path)


@pytest.mark.parametrize("is_download", [True, False])
@pytest.mark.parametrize("is_base64", [True, False])
def test_raw_base64(client, mock_loader, is_download, is_base64):
    content = (
        base64.encodebytes(b"some-value").decode("ascii") if is_base64 else "some-value"
    )
    mock_loader.get.return_value = {
        "format": "base64" if is_base64 else "text",
        "content": content,
        "mimetype": "text/txt",
        "name": "file.txt",
    }
    path = "/api/raw/some/file.txt" + ("?download=1" if is_download else "")
    r = client.get(path)

    mock_loader.get.assert_called_once_with("some/file.txt", type="file")
    assert r.status_code == 200 if is_download else 308
    if not is_download:
        r.data == content


@pytest.mark.parametrize("has_mimetype", [True, False])
def test_raw_notebook(client, mock_loader, has_mimetype):
    mock_notebook = {"format": "json", "content": "content", "name": "notebook.ipynb"}
    if has_mimetype:
        mock_notebook["mimetype"] = None
    mock_loader.get.return_value = mock_notebook
    r = client.get("/api/raw/path/notebook.ipynb")
    assert r.data == b"content"


def test_toc(client, mock_loader):
    mock_loader.get_nb.return_value.toc.return_value = "toc"
    r = client.get("/api/notebook/toc/some/notebook.ipynb")
    assert r.status_code == 200
    assert json.loads(r.data) == "toc"
    mock_loader.get_nb.assert_called_once_with("some/notebook.ipynb")


def test_render_nb(client, mock_loader):
    mock_loader.get_nb.return_value.html_content = "html"
    r = client.get("/api/notebook/render/some/notebook.ipynb")
    assert r.status_code == 200
    assert r.data == b"html"
    mock_loader.get_nb.assert_called_once_with("some/notebook.ipynb")


@pytest.mark.parametrize("use_link_func", [True, False])
@pytest.mark.parametrize("with_hub_share", [True, False])
def test_import_nb(client, mock_config, use_link_func, with_hub_share):
    mock_config.jupyterhub_base_url = "https://example.com/"
    if use_link_func:
        mock_config.import_link_func = lambda x, _: "prefix/" + x
        expected_path = "prefix/some/notebook.ipynb"
    else:
        mock_config.import_link_func = None
        expected_path = "some/notebook.ipynb"

    if with_hub_share:
        mock_config.import_link_with_hubshare_preview = True
        expected_url = b"/user-redirect/?hubshare-preview=" + base64.b64encode(
            expected_path.encode("utf-8")
        )
    else:
        mock_config.import_link_with_hubshare_preview = None
        expected_url = f"/user-redirect/lab/tree/{expected_path}".encode("utf-8")

    r = client.get("/api/notebook/import/some/notebook.ipynb")
    assert r.status_code == 200
    assert r.data == b"https://example.com" + expected_url


def test_import_nb_without_base_url(client, mock_config):
    mock_config.jupyterhub_base_url = ""
    r = client.get("/api/notebook/import/some/notebook.ipynb")
    assert r.status_code == 200
    assert r.data == b""


def test_handle_exception(client, mock_loader):
    mock_loader.get.side_effect = NotFound()
    r = client.get("/api/raw/path/not-found")
    assert r.status_code == 404
    assert json.loads(r.data)["code"] == 404
