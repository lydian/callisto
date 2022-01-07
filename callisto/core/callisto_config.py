import importlib.util
import importlib.machinery
import os
from typing import Any
from typing import Union
from typing import Type
from typing import Dict
from typing import Callable
from typing import Optional
from dataclasses import dataclass

from jupyter_server.services.contents.manager import ContentsManager


@dataclass
class CallistoConfig:

    contents_manager_cls: Optional[Union[str, Type[ContentsManager]]] = None
    contents_manager_kwargs: Optional[Dict[str, Any]] = None
    jupyterhub_base_url: Optional[str] = None
    import_link_with_hubshare_preview: Optional[bool] = None
    import_link_func: Optional[Callable] = None
    private_contents_manager_cls: Optional[Union[str, Type[ContentsManager]]] = None
    private_contents_manager_kwargs: Optional[Dict[str, Any]] = None
    private_link_encrypt_key: Optional[bytes] = None

    def __post_init__(self):
        if self.contents_manager_cls is None:
            from jupyter_server.services.contents.filemanager import FileContentsManager

            self.contents_manager_cls = FileContentsManager
            self.contents_manager_kwargs = {"root_dir": os.getcwd()}

        self.private_link_encrypt_key = (
            self.private_link_encrypt_key
            or os.getenv("PRIVATE_LINK_ENCRYPT_KEY", "").encode("ascii")
            or None
        )

    @classmethod
    def load_from_config_file(cls, config_path):
        # type: (Optional[str]) -> CallistoConfig
        if config_path is None or not os.path.exists(config_path):
            print(f"Unable to load config from path `{config_path}`")
            return cls()

        print(f"Loading config from path `{config_path}`")
        loader = importlib.machinery.SourceFileLoader("config", config_path)
        spec = importlib.util.spec_from_loader("config", loader)
        config = importlib.util.module_from_spec(spec)  # type: ignore
        loader.exec_module(config)
        kwargs = {
            key: getattr(config, key)
            for key in cls.__dataclass_fields__.keys()
            if hasattr(config, key)
        }
        return cls(**kwargs)
