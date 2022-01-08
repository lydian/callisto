#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


setup(
    name="callisto-nbviewer",
    version="1.0.0",
    description="Jupyter notebook viewer",
    author="Lydian Lee",
    author_email="lydianly@gmail.com",
    url="https://github.com/lydian/callisto",
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
        "gunicorn",
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
