from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='map-tools-twh',
    version='0.0',
    author='Timothy W. Hilton',
    author_email='thilton@ucmerced.edu',
    packages=find_packages(exclude=['docs']),
    url='https://github.com/Timothy-W-Hilton/maptoolstwh',
    license='MIT',
    description='framework for plotting data on maps with cartopy, matplotlib',
    long_description=long_description,
    install_requires=[
    ]
)
