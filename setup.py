import codecs
import os.path

from setuptools import find_packages, setup

with open("README.md") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


setup(
    name="netbox-acls",
    version="1.1.0",
    # version=get_version("netbox_acls/version.py"),
    description="A NetBox plugin for Access List management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryanmerolle/netbox-acls",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
