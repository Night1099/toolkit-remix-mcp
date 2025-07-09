#!/usr/bin/env python3
"""
Setup script for RTX Remix Toolkit MCP Server
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README-MCP.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from mcp_server.py or use default
version = "1.0.0"

setup(
    name="rtx-remix-toolkit-mcp",
    version=version,
    description="MCP Server for RTX Remix Toolkit development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RTX Remix Team",
    author_email="rtx-remix@nvidia.com",
    url="https://github.com/NVIDIAGameWorks/toolkit-remix",
    license="Apache-2.0",
    
    # Package structure
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["mcp_server"],
    
    # Dependencies
    install_requires=[
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
        "tomllib; python_version<'3.11'",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "isort",
            "ruff",
        ],
    },
    
    # Entry points for command line tools
    entry_points={
        "console_scripts": [
            "rtx-remix-mcp=mcp_server:main",
            "remix-mcp=mcp_server:main",
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.toml"],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Tools",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Games/Entertainment",
    ],
    
    # Minimum Python version
    python_requires=">=3.8",
    
    # Keywords for PyPI search
    keywords=[
        "rtx",
        "remix", 
        "nvidia",
        "mcp",
        "model-context-protocol",
        "omniverse",
        "usd",
        "3d",
        "graphics",
        "ray-tracing",
        "modding",
        "toolkit",
    ],
    
    # Project URLs
    project_urls={
        "Homepage": "https://github.com/NVIDIAGameWorks/toolkit-remix",
        "Documentation": "https://github.com/NVIDIAGameWorks/toolkit-remix/tree/main/docs",
        "Repository": "https://github.com/NVIDIAGameWorks/toolkit-remix",
        "Bug Tracker": "https://github.com/NVIDIAGameWorks/toolkit-remix/issues",
        "RTX Remix": "https://www.nvidia.com/en-us/geforce/rtx-remix/",
    },
)