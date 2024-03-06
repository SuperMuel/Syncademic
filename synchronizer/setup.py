from setuptools import setup, find_packages

setup(
    name="synchronizer",
    version="0.1.0",
    packages=find_packages(),
    description="Package that synchronizes events between ics sources and google calendar",
    author="supermuel",
    author_email="supermuel@supermuel.fr",
    install_requires=["validators", "ics", "arrow"],
)
