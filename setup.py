#!/usr/bin/env python3

from setuptools import setup


setup(
    name='dockhub',
    author='ckolos',
    version='1.0.0',
    url='https://github.com/ckolos/dockhub.py/',
    install_requires=[
        'requests<3.0.0',
        'click<8.0.0'
    ],
    license='MPLv2',
    packages=['dockhub'],
    entry_points="""
    [console_scripts]
    dockhub=dockhub:main
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
