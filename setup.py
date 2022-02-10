'''
Copyright 2022 Airbus SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


# coding: utf-8

from setuptools import setup, find_packages
from datetime import date
import os
import platform

def __path(filename):
    ''''Build a full absolute path using the given filename

        :params filename : filename to ass to the path of this module
        :returns: full builded path
    '''
    return os.path.join(os.path.dirname(__file__), filename)


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


# Manage module version using date
today = date.today()

# formating the date as yy.mm.dd
version = today.strftime('%y.%m.%d')

reqs_list = ['nose2==0.9.1',
             'plotly==5.3.0',
             'pandas==1.3.0',
             'numpy==1.20.3',
             ]

if platform.system() != 'Windows':
    reqs_list += 'petsc==3.12.3'
    reqs_list += 'petsc4py==3.12.0'


setup(
    name='value_assessment',
    version=version,
    description='Package to evaluate the economic viability used in SoSTrades project',
    long_description=readme,
    author='Airbus SAS',
    url='https://idas661.eu.airbus.corp/sostrades/value_assessment.git', 
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=reqs_list
)

