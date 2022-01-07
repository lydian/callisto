from typing import Callable


contents_manager_cls = "callisto.contents_managers.s3.SimplifiedS3ContentsManager"
# `contents_manager_cls` can be string or ContentsManger class
# You can use any existing ContentsManager to load data.
# If the value is not set, the default would be FileContentsManager
# and will serve contents on current working directory


contents_manager_kwargs = {
    "bucket": "test-bucket",
    "access_key_id": "testing",
    "secret_access_key": "testing",
    "endpoint_url": "http://localhost:3000",
}
# [Optional] `contents_manager_kwargs` is a dict of kwargs to configure the required
# settings for whatever ContentsManager you choose.


jupyterhub_base_url = "https://jupyterhub.example.com"
# [Optional] `jupyterhub_base_url` if set, you can import the notebook directly to your
# jupyterhub server. This is the base url to your jupyterhub.

import_link_with_hubshare_preview = True
# [Optional] `import_link_with_hubshare_preview`: if you have installed
# jupyterlab-hubshare plugin. You can use this link to show preview on your
# notebook server


import_link_func: Callable[[str, bool], str] = (
    lambda path, private: "prefix/" + path if not private else "private/prefix/" + path
)
# [Optional] `import_link_func` is a function in that takes the current path as an
# input. You can do any magic to update the final path in case the path on the site
# is different from the path on jupyterhub.


private_contents_manager_cls = (
    "callisto.contents_managers.s3.SimplifiedS3ContentsManager"
)
# [Optional] `private_contents_manager_cls` Add this option if you have notebook that
# should not be disscoverable but still want to allow people with link to view it.

private_contents_manager_kwargs = {
    "bucket": "test-bucket",
    "access_key_id": "testing",
    "secret_access_key": "testing",
    "endpoint_url": "http://localhost:3000",
}
# [Optional] the kwargs for private contents manager

private_link_encrypt_key = b"MPQkJL_w4wKx1HJQRdII6pBRQOTPiuzcAPfACjZORNI="
# [Optional] `private_link_encrypt_key` use this link to encrypt path, so that
# it is not discoverable
# The key is generated via
# `from cryptography.fernet import Fernet; Fernet.generate_key()`
