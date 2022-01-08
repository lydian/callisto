import base64
from typing import Any
from typing import Dict
from typing import Optional

from cryptography.fernet import Fernet

from callisto.core.contents_loader import ContentsLoader
from callisto.core.callisto_config import CallistoConfig


class PrivateLoader(ContentsLoader):

    encrypt_key: Optional[bytes]

    def __init__(self, config: CallistoConfig) -> None:
        private_config = CallistoConfig(
            contents_manager_cls=config.private_contents_manager_cls,
            contents_manager_kwargs=getattr(
                config, "private_contents_manager_kwargs", {}
            ),
        )
        super().__init__(private_config)
        if (
            config.private_contents_manager_cls is not None
            and config.private_link_encrypt_key is None
        ):
            raise ValueError(
                "Missing either `private_link_encrypt_key` in config or "
                "`PRIVATE_LINK_ENCRYPT_KEY` in environment variable"
            )
        self.encrypt_key = getattr(config, "private_link_encrypt_key", None)

    def resolve_path(self, encrypted_path: str):
        f = Fernet(self.encrypt_key)
        print("ENCRYPTED", encrypted_path)
        return f.decrypt(base64.b64decode(encrypted_path.encode("ascii"))).decode(
            "utf-8"
        )

    def encrypt_path(self, path: str):
        f = Fernet(self.encrypt_key)
        return base64.b64encode(f.encrypt(path.encode("utf-8"))).decode("ascii")

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        decrypted_path = self.resolve_path(path)
        return super().get(decrypted_path, **kwargs)
