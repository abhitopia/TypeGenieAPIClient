from setuptools import setup, find_packages
from pathlib import Path

with (Path(__file__).parent / "README.md").open("r") as fh:
    long_description = fh.read()

src_dir = str(Path(__file__).parent)

setup(
    name='typegenie',
    version='0.2.0',
    url="https://github.com/abhitopia/TypeGenieApiClient",
    author="abhitopia",
    author_email="hi@typegenie.net",
    description='Client Library for TypeGenie API. Check out https://api.typegenie.net for more info.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages('src', include=['typegenie', 'typegenie.*']),
    # py_modules=[''],
    package_dir={'': 'src'},
    entry_points={'console_scripts': ['typegenie-cli=typegenie.__cli__:main']},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
        "requests>=2.25.1",
        "click>= 8.0.1",
        "python-box>=5.3.0",
        "prompt_toolkit>=3.0.18",
        "colorama>=0.4.4"],
    # These are only required if you want to use the typegenie-cli, i.e. pip install typegenie[with-cli]
    # extras_require={
    #     'with-cli': ["click>= 8.0.1",
    #                  "python-box>=5.3.0",
    #                  "prompt_toolkit>=3.0.18",
    #                  "colorama>=0.4.4"],
    # }
)
