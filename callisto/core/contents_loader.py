import importlib
from functools import lru_cache
from typing import Any
from typing import Dict

from jupyter_server.services.contents.manager import ContentsManager
from tornado.web import HTTPError as TornadoHTTPError
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from callisto.core.callisto_config import CallistoConfig
from callisto.core.notebook_content import NotebookContent


class ContentsLoader:
    contents_manager: ContentsManager

    def __init__(self, config: CallistoConfig) -> None:
        if isinstance(config.contents_manager_cls, str):
            module_name, cls_name = config.contents_manager_cls.rsplit(".", 1)
            manager_class = getattr(importlib.import_module(module_name), cls_name)
        else:
            manager_class = config.contents_manager_cls

        self.contents_manager = manager_class(**(config.contents_manager_kwargs or {}))

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        content = kwargs.pop("content", True)
        try:
            return self.contents_manager.get(path, content=content, **kwargs)
        except TornadoHTTPError as e:
            if e.status_code == 404:
                raise NotFound()
            else:
                raise BadRequest()

    def info(self, path: str) -> Dict[str, Any]:
        return self.get(path, content=False)

    @lru_cache(10)
    def get_nb(self, path):
        return NotebookContent(self, path)
