#! /usr/bin/env python

from setuptools import find_packages, setup

PACKAGE_NAME = "idr_bench"
VERSIONFILE = "VERSION.txt"
AUTHOR = "IDRIS"
AUTHOR_EMAIL = "assist@idris.fr"
URL = "https://github.com/idriscnrs/idr_bench"

with open(VERSIONFILE, "r") as file:
    VERSION = file.read().strip()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "idr_bench = idr_bench.launcher:run",
            "idr_bench_results = idr_bench.result:gather_results",
        ],
    },
    include_package_data=True,
    license="MIT",
)
