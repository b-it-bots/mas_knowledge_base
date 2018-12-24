#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['mas_knowledge_utils', 'mas_knowledge_base'],
    package_dir={'mas_knowledge_utils': 'common/mas_knowledge_utils',
                 'mas_knowledge_base': 'ros/src/mas_knowledge_base'}
)

setup(**d)
