# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from os.path import exists


long_description = ''
if exists('readme.md'):
    with open('readme.md', 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="AVOScript",
    description="little language just4fun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ethosa",
    author_email="social.ethosa@gmail.com",
    version="0.6.1",
    url="https://github.com/ethosa/avoscript",
    install_requires=[
        "colorama",
        "equality",
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.10',
    keywords=['language', 'avocat', 'avoscript', 'script language'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
    ],
    scripts=['avos.py'],
    entry_points={
        'console_script': [
            'avos = avos:main'
        ]
    }
)
