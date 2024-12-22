# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    # Remove GitHub dark mode images
    DESCRIPTION = "".join([line for line in f if "gh-dark-mode-only" not in line])

setup(
    name="paperetl",
    version="2.3.0",
    author="NeuML",
    description="ETL processes for medical and scientific papers",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/neuml/paperetl",
    project_urls={
        "Documentation": "https://github.com/neuml/paperetl",
        "Issue Tracker": "https://github.com/neuml/paperetl/issues",
        "Source Code": "https://github.com/neuml/paperetl",
    },
    license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    keywords="etl parse covid-19 medical scientific papers",
    python_requires=">=3.9",
    install_requires=[
        "beautifulsoup4>=4.8.1",
        "elasticsearch>=7.8.0",
        "lxml>=4.5.0",
        "nltk>=3.5",
        "pandas>=1.1.0",
        "python-dateutil>=2.8.1",
        "PyYAML>=5.3",
        "requests>=2.22.0",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
)
