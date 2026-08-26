#!/usr/bin/env python3
"""
Setup script for PyTekt v0.1.0
High-performance data engineering and processing engine built for Python with a C++ core.

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
        from pytekt.install_splash import maybe_show_install_splash

        maybe_show_install_splash()
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
        import pybind11  # pyright: ignore[reportMissingImports]
        include = [pybind11.get_include()]
    except ImportError:
        return []
    root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root, "src")
    include = include + [src_dir]
    cxx_args = ["-O3", "-std=c++14"] if os.name != "nt" else ["/O2", "/std:c++14"]
    exts = []
    if os.path.isfile(os.path.join(src_dir, "pytekt_core.cpp")):
        exts.append(
            Extension(
                "pytekt._pytekt_core",
                sources=["src/pytekt_core.cpp"],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    if os.path.isfile(os.path.join(src_dir, "pytekt_bigdata.cpp")):
        exts.append(
            Extension(
                "pytekt._pytekt_bigdata",
                sources=["src/pytekt_bigdata.cpp"],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    if os.path.isfile(os.path.join(src_dir, "pytekt_universe.cpp")):
        exts.append(
            Extension(
                "pytekt._pytekt_universe",
                sources=["src/pytekt_universe.cpp"],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    if os.path.isfile(os.path.join(src_dir, "pytekt_physics.cpp")):
        exts.append(
            Extension(
                "pytekt._pytekt_physics",
                sources=["src/pytekt_physics.cpp"],
                include_dirs=include,
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    bots_dir = os.path.join(root, "pytekt", "bots", "_core")
    bots_sources = [
        os.path.join("pytekt", "bots", "_core", "bindings.cpp"),
        os.path.join("pytekt", "bots", "_core", "dispatcher.cpp"),
        os.path.join("pytekt", "bots", "_core", "ratelimiter.cpp"),
        os.path.join("pytekt", "bots", "_core", "fsm.cpp"),
        os.path.join("pytekt", "bots", "_core", "cache.cpp"),
        os.path.join("pytekt", "bots", "_core", "webhook_server.cpp"),
        os.path.join("pytekt", "bots", "_core", "antispam.cpp"),
        os.path.join("pytekt", "bots", "_core", "metrics.cpp"),
    ]
    if all(os.path.isfile(os.path.join(root, s)) for s in bots_sources):
        exts.append(
            Extension(
                "pytekt.bots._native_core",
                sources=bots_sources,
                include_dirs=include + [bots_dir],
                extra_compile_args=cxx_args,
                language="c++",
            )
        )
    return exts


setup(
    name="pytekt",
    version="0.2.1",
    author="Aksel Aghajanyan",
    maintainer="Aqwel AI Team",
    description=(
        "Open-source AI library for researchers and data scientists "
        "(physics, universe, ML, RAG, vision)"
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://aqwelai.xyz/",
    project_urls={
        "Homepage": "https://github.com/Aqwel-AI/pytekt",
        "Documentation": "https://github.com/Aqwel-AI/pytekt#readme",
        "Repository": "https://github.com/Aqwel-AI/pytekt",
        "Changelog": "https://github.com/Aqwel-AI/pytekt/blob/main/CHANGELOG.md",
        "Issues": "https://github.com/Aqwel-AI/pytekt/issues",
        "PyPI": "https://pypi.org/project/pytekt/",
    },
    packages=find_packages(),
    ext_modules=_get_extensions(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Image Processing",
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
        "Programming Language :: Python :: 3.13",
    ],
    keywords=[
        "pytekt",
        "ai-research",
        "machine-learning",
        "data-science",
        "llm",
        "physics",
        "astronomy",
        "computer-vision",
        "scientific-computing",
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
            "numpy>=1.20.0",
        ],
        "viz3d": [
            "plotly>=5.18.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "numpy>=1.20.0",
        ],

        # Transformer training (PyTekt Former: decoder-only, NumPy autograd)
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

        # Computer vision (image I/O, transforms, OpenCV helpers)
        "vision": [
            "pillow>=9.0.0",
            "opencv-python-headless>=4.5.0",
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
        "db": [
            "pymysql>=1.1.0",
            "psycopg[binary]>=3.1.0",
            "pymongo>=4.6.0",
            "redis>=5.0.0",
        ],
        "universe": [
            "matplotlib>=3.5.0",
        ],
        "cosmos": [
            "matplotlib>=3.5.0",
        ],
        "physics": [
            "matplotlib>=3.5.0",
        ],
        "serve": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
        ],
        "ui": [
            "gradio>=4.0.0",
            "streamlit>=1.28.0",
        ],
        "monitor": [
            "psutil>=5.9.0",
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "nvidia-ml-py>=12.0.0",
        ],

        # Full installation (all features; keep in sync with pyproject.toml)
        "full": [
            "pymysql>=1.1.0",
            "psycopg[binary]>=3.1.0",
            "pymongo>=4.6.0",
            "redis>=5.0.0",
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
            "opencv-python-headless>=4.5.0",
            "tiktoken>=0.5.0",
            "tomli>=2.0.0; python_version<'3.11'",
            "pyyaml>=6.0",
            "psutil>=5.9.0",
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "nvidia-ml-py>=12.0.0",
            "gradio>=4.0.0",
            "streamlit>=1.28.0",
        ],
    },
    package_data={
        "pytekt.monitor": ["static/*.html", "*.md"],
        "pytekt.monitor.examples": ["*.md"],
    },

    entry_points={
        "console_scripts": [
            "pytekt=pytekt.cli:main",
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
