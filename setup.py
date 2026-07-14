"""
WhatsApp Automation Tool - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="whatsapp-automation",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered WhatsApp automation tool with auto-reply, scheduled messages, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/whatsapp-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "ollama>=0.1.0",
        "openai>=1.0.0",
        "anthropic>=0.30.0",
        "google-generativeai>=0.3.0",
        "sqlalchemy>=2.0.0",
        "apscheduler>=3.10.0",
        "loguru>=0.7.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "gradio>=4.0.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "whatsapp-bot=main:main",
        ],
    },
)
