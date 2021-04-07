from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='typegenie',
    version='0.0.7',
    url="https://github.com/abhitopia/TypeGenieApiClient",
    author="abhitopia",
    author_email="hi@typegenie.net",
    description='Client Library for TypeGenie API. Check out http://api.typegenie.net for more info.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages('src', include=['typegenie', 'typegenie.*']),
    # py_modules=[''],
    package_dir={'': 'src'},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        "pandas",
        "requests"
    ]
)
