import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="PyCyRest",
    version="1.0.1",
    description="A python CyREST library for Cytoscape.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Zachary Juang",
    author_email="zacharyjuang@gmail.com",
    url="https://github.com/zachary822/PyCyRest",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['pycyrest'],
    install_requires=[
        'requests',
        'lxml'
    ]
)
