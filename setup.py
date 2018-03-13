#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io
import sys

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

needs_wheel = {'release', 'bdist_wheel', 'dists'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []

name = 'vr.events'
description = ''

setup_params = dict(
    name=name,
    use_scm_version=True,
    author="YouGov, Plc.",
    author_email="dev@yougov.com",
    description=description or name,
    long_description=long_description,
    url="https://github.com/yougov/" + name,
    packages=setuptools.find_packages(),
    include_package_data=True,
    namespace_packages=name.split('.')[:-1],
    install_requires=[
        'vr.common>=4.3.0',
        'six',
        'redis>=2.4.13',
    ],
    extras_require={
    },
    setup_requires=[
        'setuptools_scm>=1.15.0',
    ] + wheel,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
    },
)
if __name__ == '__main__':
    setuptools.setup(**setup_params)
