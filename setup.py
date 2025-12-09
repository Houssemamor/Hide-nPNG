"""
Setup configuration for Hide'nPNG steganography tool.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hide-npng",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Hide secret documents in PNG/BMP images using LSB steganography",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Houssemamor/Hide-nPNG",
    project_urls={
        "Bug Tracker": "https://github.com/Houssemamor/Hide-nPNG/issues",
        "Documentation": "https://github.com/Houssemamor/Hide-nPNG#readme",
        "Source Code": "https://github.com/Houssemamor/Hide-nPNG",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hide-npng=main:main",
        ],
    },
    include_package_data=True,
)
