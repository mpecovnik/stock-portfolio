import os
import re

from setuptools import find_packages, setup


def parse_requirements(file):
    with open(os.path.join(os.path.dirname(__file__), file), mode="r", encoding="ascii") as req_file:
        return [line.strip() for line in req_file if "/" not in line]


def get_version():
    with open(
        os.path.join(os.path.dirname(__file__), "sp", "__init__.py"),
        mode="r",
        encoding="ascii",
    ) as file:
        return re.findall('__version__ = "(.*)"', file.read())[0]


setup(
    name="sp",
    python_requires=">=3.8",
    version=get_version(),
    description="Stock Portfolio tracker and analyzer",
    url="https://github.com/mpecovnik/stock-portfolio",
    author="Matic Pečovnik",
    author_email="matic.pecovnik@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt"),
    zip_safe=False,
    entry_points={"console_scripts": ["sp=sp.cli:cli"]},
)
