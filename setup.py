#!/usr/bin/env python3
"""
Setup script for Land Area Automation System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'LAND_AREA_AUTOMATION_README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Land Area Automation AI System for Real Estate Analysis"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="land-area-automation",
    version="2.0.0",
    author="Land Area Automation Team",
    author_email="team@landareaautomation.com",
    description="AI-powered comprehensive real estate analysis and investment intelligence system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/land-area-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.8",
            "mkdocstrings>=0.24.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "nginx>=1.25.0",
            "supervisor>=4.2.5",
        ]
    },
    entry_points={
        "console_scripts": [
            "land-area-automation=main:main",
            "land-automation-demo=run_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.py"],
        "models": ["*.pkl"],
        "docs": ["*.md"],
        "examples": ["*.py"],
        "tests": ["*.py"],
    },
    zip_safe=False,
    keywords=[
        "real estate",
        "property valuation",
        "machine learning",
        "AI",
        "investment analysis",
        "land suitability",
        "automated valuation model",
        "SHAP",
        "explainable AI",
        "recommendation system"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/land-area-automation/issues",
        "Source": "https://github.com/your-org/land-area-automation",
        "Documentation": "https://land-area-automation.readthedocs.io/",
    },
)
