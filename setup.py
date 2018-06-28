"""
ACHTUNG: You *must* adapt the "install_requires", "setup_requires",
         and "tests_require" sections!
         Pin you dependencies!
         Classifiers are optional but recommended!
         I'll stop being excited now!
"""

import re
import os

from setuptools import setup, find_packages

def package_files(directory_list):
    paths = []
    for directory in directory_list:
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join('..', path, filename))
    return paths

project_package = 'sbs'
project_info = {}

db_models_dir = os.path.join(project_package, "models")
oidc_dir = os.path.join(project_package, "oidc")
tools_dir = os.path.join(project_package, "tools")
extra_files = package_files([db_models_dir, oidc_dir, tools_dir])

classifiers = """
Development Status :: 1 - Planning
Intended Audience :: Science/Research
Topic :: Software Development
License :: Other/Proprietary License
Programming Language :: Python :: 3.6
"""

with open('{}/__init__.py'.format(project_package), 'r') as f:
    for _ in f.read().splitlines():
        b = re.search(r'^__(.*)__\s*=\s*[\'"]([^\'"]*)[\'"]', _)
        if b:
            project_info[b.group(1)] = b.group(2)


setup(
    name=project_info['title'],
    version=project_info['version'],
    author=project_info['author'],
    author_email=project_info['author_email'],
    url=project_info['url'],
    license=project_info['license'],
    description=project_info['description'],
    long_description=open('README.md').read(),
    packages=find_packages(),
    include_package_data=True,
    package_data={'sbs': extra_files},
    keywords='cli',
    install_requires=[
        'click',
    ],
    setup_requires=[
        'pytest-runner',
        'wheel',
        'Sphinx',
        'sphinx_rtd_theme',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-flake8',
        'pytest-watch',
    ],
    entry_points={
        'console_scripts': [
            "hello = sbs.sample_module:hello_world",
        ]
    },
    classifiers=classifiers.splitlines()[1:]
)
