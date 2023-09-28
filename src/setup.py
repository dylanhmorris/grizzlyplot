from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='grizzlyplot',
   version='0.0.1',
   description='',
   license="BSD 3-clause",
   long_description=long_description,
   author='Dylan H. Morris',
   author_email='foomail@foo.example',
   url="http://www.foopackage.example/",
   packages=['grizzlyplot'],  # same as name
)
