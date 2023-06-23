"""
Configuration for setuptools.
"""
import codecs
import os.path

from setuptools import find_packages, setup

script_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(script_dir, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read().replace("(docs/img/", "(https://raw.githubusercontent.com/ryanmerolle/netbox-acls/release/docs/img/")


def read(relative_path):
    """
    Read a file and return its contents.
    """
    with codecs.open(os.path.join(script_dir, relative_path), "r") as fp:
        return fp.read()


def get_version(relative_path):
    """
    Extract the version number from a file without importing it.
    """
    for line in read(relative_path).splitlines():
        if not line.startswith("__version__"):
            raise RuntimeError("Unable to find version string.")
        delim = '"' if '"' in line else "'"
        return line.split(delim)[1]


setup(
    name="netbox-acls",
    version=get_version("netbox_acls/version.py"),
    description="A NetBox plugin for Access List management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryanmerolle/netbox-acls",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Framework :: Django",
        "Topic :: System :: Networking",
        "Topic :: Internet",
    ],
)
