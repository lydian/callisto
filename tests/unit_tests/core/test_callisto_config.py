import os

from callisto.core.callisto_config import CallistoConfig
from jupyter_server.services.contents.filemanager import FileContentsManager


def test_load_from_config_file():
    config = CallistoConfig.load_from_config_file("tests/fixtures/config.py")
    assert (
        config.contents_manager_cls
        == "callisto.contents_managers.s3.SimplifiedS3ContentsManager"
    )
    assert config.contents_manager_kwargs == {
        "bucket": "test-bucket",
        "access_key_id": "testing",
        "secret_access_key": "testing",
        "endpoint_url": "http://localhost:3000",
    }
    assert config.jupyterhub_base_url == "https://jupyterhub.example.com"
    assert config.import_link_with_hubshare_preview is True
    assert config.import_link_func("some/path", False) == "prefix/some/path"


def test_load_from_config_file_missing_manager_cls(tmpdir):
    config_file = tmpdir.join("test-config.py")
    config_file.write("jupyterhub_base_url = 'https://jupyterhub.example.com'")

    config = CallistoConfig.load_from_config_file(str(config_file))
    assert config.contents_manager_cls == FileContentsManager
    assert config.contents_manager_kwargs == {"root_dir": os.getcwd()}
    assert config.jupyterhub_base_url == "https://jupyterhub.example.com"
    assert config.import_link_func is None
    assert config.import_link_with_hubshare_preview is None


def test_load_from_config_file_not_exist(capsys):
    config = CallistoConfig.load_from_config_file("file-not-exist.py")
    assert config.contents_manager_cls == FileContentsManager
    assert config.contents_manager_kwargs == {"root_dir": os.getcwd()}
    assert config.jupyterhub_base_url is None
    assert config.import_link_func is None
    assert config.import_link_with_hubshare_preview is None
    assert (
        "Unable to load config from path `file-not-exist.py`" in capsys.readouterr().out
    )
