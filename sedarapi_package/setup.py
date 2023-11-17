from setuptools import setup, find_packages

setup(
    name="SedarAPI",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    author="Nico Kuth",
    author_email="nico.kuth@stud.hn.de",
    description="Eine abstrahierende Schnittstelle für die Interaktion mit der API des Data Lakes 'SEDAR'",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)