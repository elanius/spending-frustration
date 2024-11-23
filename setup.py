from setuptools import setup, find_packages

setup(
    name="spending_frustration",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "meilisearch"
    ],
    entry_points={
        "console_scripts": [
            "spending-frustration=spending_frustration.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A package to parse and analyze bank statements.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/spending_frustration",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
