from setuptools import find_packages, setup


setup(
    name="config",
    version="0.1.0",
    packages=find_packages(),
    url="https://github.com/clayman74/config",
    licence="MIT",
    author="Kirill Sumorokov",
    author_email="sumorokov.k@gmail.com",
    description="Framework agnostic configuration for apps and microservices",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="config",
    extras_require={
        "develop": [
            "flake8==3.6.0",
            "flake8-bugbear==18.8.0",
            "flake8-builtins-unleashed==1.3.1",
            "flake8-comprehensions==1.4.1",
            "flake8-import-order==0.18",
            "flake8-print==3.1.0",
            "mypy==0.650",
        ],
        "test": ["pytest==4.0.2", "coverage==4.5.2"],
    },
)
