#!/usr/bin/env python
import json
from pathlib import Path

from distutils.core import setup
from setuptools import find_packages


HERE = Path(__file__).parent.resolve()
pkg_json = json.loads((HERE / "front" / "package.json").read_bytes())
long_description = (HERE / "README.md").read_text()


setup(
    name="callisto-nbviewer",
    version=pkg_json["version"],
    description="Jupyter notebook viewer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lydian Lee",
    author_email="lydianly@gmail.com",
    url="https://github.com/lydian/callisto",
    packages=find_packages(),
    py_modules=["cli"],
    include_package_data=True,
    install_requires=[
        "boto3",
        "bs4",
        "click",
        "cryptography",
        "cssutils",
        "flask",
        "gunicorn",
        "jinja2",
        "jupyter-server",
        "more_click",
        "nbconvert",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Framework :: Jupyter",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={"console_scripts": ["callisto = cli:cli"]},
)
