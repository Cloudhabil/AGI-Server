from setuptools import setup, find_packages

setup(
    name="brahim-iias",
    version="1.0.0",
    author="Elias Oulad Brahim",
    author_email="obe@cloudhabil.com",
    description="Intelligent Infrastructure as a Service - Deterministic AI resource allocation",
    long_description=open("../../publications/README_IIAS.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/asios/iias-framework",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai infrastructure golden-ratio npu gpu optimization",
)
