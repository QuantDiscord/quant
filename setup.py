from setuptools import setup

from quant import __version__

with open("README.md", "r") as file:
    readme_text = file.read()

setup(
    name="quant",
    version=__version__,
    description="Quantum Symphony in Discord Bot Creation.",
    long_description=readme_text,
    author="MagMigo",
    requires=["aiohttp", "attrs"]
)
