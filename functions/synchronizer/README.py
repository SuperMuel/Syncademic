from setuptools import setup, find_packages

setup(
    name="synchronizer",
    version="0.1.0",
    description="Package for synchronizing events between ics files and Google Calendars",
    author="SuperMuel",
    author_email="supermuel@supermuel.fr",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "validators",
    ],
)
