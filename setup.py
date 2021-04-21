#!/bin/env python
import os

from setuptools import find_packages, setup


def find_xdg_data_files(from_dir, to_dir, package_name, data_files):
    for (root, _, files) in os.walk(from_dir):
        if files:
            to_dir = to_dir.format(pkgname=package_name)

            sub_path = root.split(from_dir)[1]
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]

            files = [os.path.join(root, file) for file in files]
            data_files.append((os.path.join(to_dir, sub_path), files))


def find_data_files(data_map, package_name):
    data_files = []

    for (from_dir, to_dir) in data_map:
        find_xdg_data_files(from_dir, to_dir, package_name, data_files)

    return data_files


DATA_FILES = [
    ("data/icons", "share/icons"),
    ("data/applications", "share/applications"),
]

setup(
    author="Juan Manuel Schillaci",
    author_email="jmschillaci@gmail.com",
    description="A pomodoro timer and time tracker",
    include_package_data=True,
    keywords="pomodoro,focusyn",
    license="GPL-3",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    name="focusyn-gtk",
    packages=find_packages(exclude=["tests"]),
    data_files=find_data_files(DATA_FILES, "focusyn"),
    url="https://github.com/skalanux/focusyn",
    version="0.1.0",
    zip_safe=False,
    entry_points={"console_scripts": ["focusyn=focusyn.__main__:main"]},
)
