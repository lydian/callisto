import importlib
from functools import lru_cache
from typing import Any
from typing import Dict
from callisto.core.notebook import NotebookContent

from jupyter_server.services.contents.manager import ContentsManager

from callisto.core.config_loader import Config


class Loader:
    contents_manager: ContentsManager

    def __init__(self, config: Config) -> None:
        if isinstance(config.contents_manager_cls, str):
            module_name, cls_name = config.contents_manager_cls.rsplit(".", 1)
            manager_class = getattr(importlib.import_module(module_name), cls_name)
        else:
            manager_class = config.contents_manager_cls

        self.contents_manager = manager_class(
            **(config.contents_manager_kwargs or {})
        )


    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        r = self.contents_manager.get(path, content=True, **kwargs)
        return r

    def info(self, path: str) -> Dict[str, Any]:
        return self.contents_manager.get(path, content=False)

    @lru_cache(10)
    def get_nb(self, path):
        # type: (str) -> callisto.core.notebook.NotebookContent
        return NotebookContent(self, path)
