from setuptools import setup, find_packages
from pathlib import Path

# Read the README if it exists
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="librarian-agent",
    version="0.1.0",
    description="Multi-Agent Software Construction Swarm with JosieDesk orchestration and Kirktower control tower",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JosieHQ",
    author_email="dev@josiehq.com",
    url="https://github.com/josiehq/librarian-agent",
    license="MIT",
    py_modules=[
        "josiedesk_core",
        "josiedesk_hybrid",
        "josiedesk_memory",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "httpx>=0.24.0",
        "flask>=2.3.0",
        
        # LLM and knowledge base
        "llama-index>=0.9.0",
        "llama-index-core>=0.1.0",
        
        # Multi-agent orchestration
        "pyautogen>=0.2.0",
        
        # Async and utilities
        "asyncio-contextmanager>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "go": [
            # For Kirktower and Tower CLI components
            # Requires Go 1.20+
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "multi-agent",
        "orchestration",
        "swarm",
        "ai",
        "construction",
        "llm",
        "metagpt",
    ],
    project_urls={
        "Bug Reports": "https://github.com/josiehq/librarian-agent/issues",
        "Source": "https://github.com/josiehq/librarian-agent",
    },
)
