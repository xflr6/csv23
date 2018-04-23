# setup.py

import io
from setuptools import setup, find_packages

setup(
    name='csv23',
    version='0.1.3',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Python 2/3 unicode CSV compatibility layer',
    keywords='unicode csv reader writer',
    license='MIT',
    url='https://github.com/xflr6/csv23',
    packages=find_packages(),
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'mock; python_version < "3"',
    ],
    extras_require={
        'dev': ['tox>=3.0', 'flake8', 'pep8-naming', 'wheel', 'twine'],
        'test': ['mock>=2', 'pytest>=3.4', 'pytest-mock>=1.8', 'pytest-cov'],
        'docs': ['sphinx>=1.3', 'sphinx-rtd-theme'],
    },
    long_description=io.open('README.rst', encoding='utf-8').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
