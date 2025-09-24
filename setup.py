from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in onehash_education/__init__.py
from onehash_education import __version__ as version

setup(
    name="onehash_education",
    version=version,
    description="OneHash Education",
    author="OneHash",
    author_email="engineering@onehash.ai",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
