from setuptools import setup, find_packages

setup(
    name="brahim-debugger",
    version="1.0.0",
    author="Elias Oulad Brahim",
    author_email="cloudhabil@gmail.com",
    description="Brahim-Aligned Code Debugger Agent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Cloudhabil/AGI-Server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "brahim-debug=brahim_debugger.agent:main",
        ],
    },
    keywords="debugger, code-analysis, ai-agent, brahim, golden-ratio",
)
