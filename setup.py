from setuptools import find_packages, setup
import pathlib

# Package metadata
# ----------------

NAME = "py-messenger"
DESCRIPTION = "A general purpose messaging library that provides a neutral API for the most used communication patterns, like pub-sub, JSON-RPC, etc."

# Get the long description from the README file
HERE = pathlib.Path(__file__).parent.resolve()
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")

URL = "https://github.com/tombenke/py-messenger"
EMAIL = "tamas.benke@lhsystems.com"
AUTHOR = "Tamás Benke"
LICENSE = "MIT"
REQUIRES_PYTHON = ">=3.8"

# What packages are required for this module to be executed?
REQUIRED = [
    "asyncio-nats-client",
    "asyncio-nats-streaming",
    "python-dotenv",
]

TEST_REQUIREMENTS = [
    "coverage",
    "coverage-badge",
    "black",
    "pylint",
    "pdoc",
    "pydeps",
    "loguru",
]

setup(
    name=NAME,
    version="0.1.0",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=REQUIRED,
    extras_require={"dev": TEST_REQUIREMENTS},
    entry_points={
        "console_scripts": [],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
