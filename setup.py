#!/usr/bin/env python3
"""
Setup script for Aqwel-Aion v0.2.0
Professional AI Research & Development Library

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
Copyright: 2025 Aqwel AI
License: Apache-2.0
"""

import os
from setuptools import setup, find_packages, Extension
from setuptools.command.develop import develop as _develop_cmd
from setuptools.command.install import install as _install_cmd


def _post_install_splash() -> None:
    try:
        from aion.install_splash import show_install_splash

        show_install_splash(animated=True)
    except Exception:
        pass


class InstallCommand(_install_cmd):
    def run(self) -> None:
        super().run()
        _post_install_splash()


class DevelopCommand(_develop_cmd):
    def run(self) -> None:
        super().run()
        _post_install_splash()


def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip()
            for line in fh
            if line.strip() and not line.startswith("#")
        ]


def _get_extensions():
    """Build C++ extensions if pybind11 and sources are available."""
    try:
        import pybind11
        include = [pybind11.get_include()]
    except ImportError:
        return []
    cxx_args = ["-O3", "-std=c++14"] if os.name != "nt" else ["/O2", "/std:c++14"]
    exts = []
    core_src = "src/aion_core.cpp"
    if os.path.isfile(core_src):
        exts.append(
            Extension(
                "aion._aion_core",
                sources=[core_src],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    universe_src = "src/aion_universe.cpp"
    if os.path.isfile(universe_src):
        exts.append(
            Extension(
                "aion._aion_universe",
                sources=[universe_src],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    return exts


setup(
    name="aqwel-aion",
    version="0.2.0",
    author="Aksel Aghajanyan",
    maintainer="Aqwel AI Team",
    description=(
        "Complete AI Research & Development Library with "
        "Advanced Mathematics, AI, and Visualization Tools"
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://aqwelai.xyz/",
    project_urls={
        "Homepage": "https://aqwelai.xyz",
        "Documentation": "https://aqwelai.xyz/#/docs",
        "PyPI": "https://pypi.org/project/aqwel-aion/",
    },
    packages=find_packages(),
    ext_modules=_get_extensions(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "ai-research",
        "machine-learning",
        "mathematics",
        "statistics",
        "data-science",
        "visualization",
        "scientific-computing",
        "research-tools",
        "aqwel-ai",
    ],
    python_requires=">=3.8",

    # Core dependencies required for all users
    install_requires=[
        "numpy>=1.21.0",
        "watchdog>=2.1.0",
        "gitpython>=3.1.0",
        "certifi>=2023.0.0",
    ],

    # Optional feature dependencies
    extras_require={

        # Visualization support
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],

        # Transformer training (Aion Former: decoder-only, NumPy autograd)
        "former": [
            "matplotlib>=3.5.0",
            "pyyaml>=6.0",
        ],

        # Machine learning and AI stack (keep in sync with pyproject.toml)
        "ai": [
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "openai>=1.0.0",
            "sentence-transformers>=2.2.0",
        ],

        # Documentation and export tools
        "docs": [
            "reportlab>=3.6.0",
            "pillow>=9.0.0",
        ],

        # Development tools
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
        ],

        "tools": [
            "tiktoken>=0.5.0",
        ],
        "rag": [
            "sentence-transformers>=2.2.0",
            "faiss-cpu>=1.7.0",
        ],
        "config": [
            "tomli>=2.0.0; python_version<'3.11'",
            "pyyaml>=6.0",
        ],
        "monitor": [
            "psutil>=5.9.0",
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "nvidia-ml-py>=12.0.0",
        ],

        # Full installation (all features; keep in sync with pyproject.toml)
        "full": [
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "openai>=1.0.0",
            "faiss-cpu>=1.7.0",
            "sentence-transformers>=2.2.0",
            "reportlab>=3.6.0",
            "pillow>=9.0.0",
            "tiktoken>=0.5.0",
            "tomli>=2.0.0; python_version<'3.11'",
            "pyyaml>=6.0",
            "psutil>=5.9.0",
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "nvidia-ml-py>=12.0.0",
        ],
    },
    package_data={
        "aion.monitor": ["static/*.html", "*.md"],
        "aion.monitor.examples": ["*.md"],
    },

    entry_points={
        "console_scripts": [
            "aion=aion.cli:main",
        ],
    },
    cmdclass={
        "install": InstallCommand,
        "develop": DevelopCommand,
    },
    include_package_data=True,
    zip_safe=False,
    license="Apache-2.0",
)
