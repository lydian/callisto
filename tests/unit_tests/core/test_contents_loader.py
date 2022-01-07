from unittest import mock

import pytest
from jupyter_server.services.contents.manager import ContentsManager
from tornado.web import HTTPError as TornadoHTTPError
from werkzeug import exceptions as FlaskHTTPExceptions

from callisto.core.contents_loader import ContentsLoader
from callisto.core.callisto_config import CallistoConfig
from callisto.core.notebook_content import NotebookContent


class TestLoader:
    @pytest.fixture
    def mock_import_module(self):
        with mock.patch("importlib.import_module") as m:
            yield m

    def test_init_str_class(self, mock_import_module):
        config = mock.MagicMock(spec=CallistoConfig)
        config.contents_manager_cls = "fake.module.FakeContentsManager"
        loader = ContentsLoader(config)
        assert (
            loader.contents_manager
            is mock_import_module.return_value.FakeContentsManager.return_value
        )
        mock_import_module.return_value.FakeContentsManager.assert_called_once_with()

    def test_init_actual_class(self):
        class Dummy(ContentsManager):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        config = mock.MagicMock(spec=CallistoConfig)
        config.contents_manager_cls = Dummy
        config.contents_manager_kwargs = {"foo": "bar"}

        loader = ContentsLoader(config)
        assert isinstance(loader.contents_manager, Dummy)
        assert loader.contents_manager.kwargs == {"foo": "bar"}

    @pytest.fixture
    def contents_manager(self):
        return mock.MagicMock(spec=ContentsManager)

    @pytest.fixture
    def loader(self, mock_import_module, contents_manager):
        loader = ContentsLoader(mock.MagicMock(spec=CallistoConfig))
        loader.contents_manager = contents_manager
        return loader

    def test_get_success(self, loader, contents_manager):
        contents_manager.get.return_value = {"content": "some-content"}
        assert loader.get("/path/to/file", type="file") == {"content": "some-content"}
        contents_manager.get.assert_called_once_with(
            "/path/to/file", content=True, type="file"
        )

    def test_get_fail_404(self, loader, contents_manager):
        contents_manager.get.side_effect = TornadoHTTPError(404, "file not found")
        with pytest.raises(FlaskHTTPExceptions.NotFound):
            loader.get("/path/not-exist")

    def test_get_other(self, loader, contents_manager):
        contents_manager.get.side_effect = TornadoHTTPError(400, "Bad Request")
        with pytest.raises(FlaskHTTPExceptions.BadRequest):
            loader.get("/bad-request")

    def test_info(self, loader, contents_manager):
        contents_manager.get.return_value = {"name": "filename"}
        assert loader.info("/path/filename") == {"name": "filename"}
        contents_manager.get.assert_called_once_with("/path/filename", content=False)

    def test_get_nb_cached(self, loader):
        f1 = loader.get_nb("/file_1")
        f2 = loader.get_nb("/file_2")
        f3 = loader.get_nb("/file_1")
        assert f1 is f3
        assert f1 is not f2
        assert all(isinstance(f, NotebookContent) for f in [f1, f2, f3])
