from setuptools import find_packages, setup
import pathlib
import os

# Package metadata
# ----------------

NAME = "py-msgp"
DESCRIPTION = "A general purpose messaging library that provides a neutral API for the most used communication patterns, like pub-sub, request-response, etc."

# Get the long description from the README file
HERE = pathlib.Path(__file__).parent.resolve()
# LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")
LONG_DESCRIPTION = """
A general purpose messaging library that provides a neutral API for the most used communication patterns, like pub-sub, request-response, etc.

For further information, please visit the [project's homepage](https://github.com/tombenke/py-msgp).
"""

URL = "https://github.com/tombenke/py-msgp"
EMAIL = "tamas.benke@lhsystems.com"
AUTHOR = "Tamás Benke"
LICENSE = "MIT"
REQUIRES_PYTHON = ">=3.8"

# What packages are required for this module to be executed?
REQUIRED = [
    "nats-py",
    "python-dotenv",
    "loguru",
    "typing",
]

DEV_REQUIREMENTS = [
    "build",
    "coverage",
    "coverage-badge",
    "black",
    "otel-inst-py >= 2.0.0",
    "pylint",
    "pdoc",
    "pydeps",
]

setup(
    name=NAME,
    version=os.getenv("VERSION", "1.0.0"),
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
    extras_require={"dev": DEV_REQUIREMENTS},
    entry_points={
        "console_scripts": [],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
