#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('requirements.txt', encoding='utf-8') as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name='ritter_digital_auswertung',
    version='1.0.0',
    description='Auswertungstool für das Raumbuch-System',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Damjan Petrovic',
    author_email='petrovic@ritter-digital.de',
    url='https://github.com/damjan1996/RitterAuswertung',
    packages=find_packages(include=['src', 'src.*', 'config']),
    include_package_data=True,
    install_requires=requirements,
    license='Proprietary',
    zip_safe=False,
    keywords='raumbuch, auswertung, ritter, digital',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: German',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'ritter-auswertung=scripts.run_app:main',
        ],
    },
    python_requires='>=3.8',
)