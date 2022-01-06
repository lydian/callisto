# callisto
[![codecov](https://codecov.io/gh/lydian/callisto/branch/master/graph/badge.svg?token=1YB3XJNKJZ)](https://codecov.io/gh/lydian/callisto)
![build](https://github.com/lydian/callisto/workflows/Build/badge.svg)


![logo](https://user-images.githubusercontent.com/678485/147995610-e9fb67f3-d72e-41ed-82e0-3afb6e89a10d.png?style=centerme)

A jupyter notebook viewer that has the following features:
- Use ContentsManager as content provider. Therefore it is completely work with any of your jupyterhub settings.
- Showing Table of Contents for quickly reference to your notebook
- Directly import the notebook to your jupyterhub server.

# Getting Started

1. Install the package:
```
pip install callisto-nbviewer
```
2. start the server:
```
callisto start --port 5000
```
3. Visit website  `localhost:5000`

![screenshot-list](https://user-images.githubusercontent.com/678485/147997776-ca207748-ff09-4e39-8305-db5e6ea86398.png)
![screenshot-notebook](https://user-images.githubusercontent.com/678485/147997798-161b215c-c7a3-490a-987b-3957bdfb0513.png)


# Configuration

You can use your own config to customize callisto. see example on [tests/fixtures/config.py](https://github.com/lydian/callisto/blob/master/tests/fixtures/config.py)
```python:my_callisto_config.py
ontents_manager_cls = "s3contents.S3ContentsManager"
# `contents_manager_cls` can be string or ContentsManger class
# You can use any existing ContentsManager to load data.
# If the value is not set, the default would be FileContentsManager
# and will serve contents on current working directory


contents_manager_kwargs = {
    "bucket": "test-bucket",
    "access_key_id": "testing",
    "secret_access_key": "testing",
    "endpoint_url": "http://localhost:3000"
}
# [Optional] `contents_manager_kwargs` is a dict of kwargs to configure the required settings
# for whatever ContentsManager you choose.


jupyterhub_base_url = "https://jupyterhub.example.com"
# [Optional] `jupyterhub_base_url` if set, you can import the notebook directly to your jupyterhub server
# This is the base url to your jupyterhub.

import_link_with_hubshare_preview = True
# [Optional] `import_link_with_hubshare_preview`: if you have installed jupyterlab-hubshare plugin,
# You can use this link to show preview on your notebook server


import_link_func = lambda path: "prefix/" + path
# [Optional] `import_link_func` is a function in that takes the current path as an input,
# You can do any magic to update the final path in case the path on the site is different
# from the path on jupyterhub.
```
and then start callisto with
```
callisto --config my_callisto_config.py
```

## Config for different contents manager

### Local File

```python:my_callisto_config.py
contents_manager_cls = "managerjupyter_server.services.contents.filemanager.FileContentsManager"
contents_manager_kwargs = {"root_dir": "/absolute/path/to/your/notebook/folder"}
```

### S3
Note that s3contents seems to be fetching the directory last_modified time, and is very slow.
Therefore I make a work around file in `callisto.contents_managers.s3.SimplifiedS3ContentsManager` class
please take a look on the settings.

```python:my_callisto_config.py
contents_manager_cls = "callisto.contents_managers.s3.SimplifiedS3ContentsManager"
contents_manager_kwargs = {
    "bucket": "my-s3-bucket",
    "prefix": "prefix/to/your/notebook/folder",
    "aws_access_key_id": "my_access_key",
    "aws_secret_access_key": "my_secret_access_key",
}
```

if your file s3 doesn't contains a lot of folders, you can still use s3contents (please ensure you also install `s3contents`)
```python:my_callisto_config.py
contents_manager_cls = "s3contents.S3ContentsManager"
contents_manager_kwargs = {
    "bucket": "my-s3-bucket",
    "prefix": "prefix/to/your/notebook/folder",
}

```
for more settings, please refer to: [s3contents](https://github.com/danielfrg/s3contents)


 # Development
 to start a dev version, download the git repo:
 ```
 git clone https://github.com/lydian/callisto.git
 ```

 and run
 ```
 cd callisto
 make start-dev
 ```

 The dev server will running on http://localhost:5001
