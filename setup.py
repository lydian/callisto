#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


setup(
    name="callisto-nbviewer",
    version="1.0.0",
    description="Viewer for notebooks",
    author="Lydian Lee",
    author_email="lydianly@gmail.com",
    url="",
    packages=find_packages(),
    py_modules=["cli"],
    include_package_data=True,
    install_requires=[
        "boto3",
        "bs4",
        "flask",
        "jinja2",
        "nbconvert",
        "pycrypto",
        "click",
        "more_click",
        "jupyter-server",
    ],
    entry_points={"console_scripts": ["callisto = cli:cli"]},
)
