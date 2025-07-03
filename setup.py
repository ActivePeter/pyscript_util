#!/usr/bin/env python3
"""
Setup script for pyscript_util - Python script utilities for maximum compatibility
"""

from setuptools import setup, find_packages
import os


# Read the contents of your README file
def read_file(filename):
    """Read file content."""
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, filename), encoding="utf-8") as f:
        return f.read()


# Try to read README, fallback to basic description if not available
try:
    long_description = read_file("README.md")
except FileNotFoundError:
    long_description = """
    pyscript_util - Python script utilities for maximum compatibility
    
    Provides command execution and directory management functions using os.system
    for scripts that need to work across different Python environments and versions.
    """

setup(
    name="pyscript_util",
    version="0.1.11",
    author="telego-project",
    author_email="",
    description="Python script utilities for maximum compatibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ActivePeter/pyscript_util",
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=["pyscript_util.pyscript_util"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=5.1",  # YAML配置文件支持，兼容Python 3.6+
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyscript-util=pyscript_util.pyscript_util:main",
        ],
    },
    keywords="python script utilities command execution os.system compatibility",
    project_urls={
        "Bug Reports": "https://github.com/ActivePeter/pyscript_util/issues",
        "Source": "https://github.com/ActivePeter/pyscript_util",
    },
)
