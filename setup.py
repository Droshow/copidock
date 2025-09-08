from setuptools import setup, find_packages

setup(
    name="copidock",
    version="0.2.0",
    # packages=find_packages(include=["cli", "cli.*"]),
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "copidock=copidock.cli.main:app",  # <- points to app in cli/main.py
        ],
    },
    python_requires=">=3.8",
    author="Copidock Team",
    description="CLI for Copidock serverless note management",
)
