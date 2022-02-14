# ValueAssessment

Repository containing simple Value Assessment disciplines

## Description
SoSTrades value assessment is the Python package to evaluate the economic viability used in SoSTrades project

## Packages installation
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

## Value Blocks
This package contains some Value Block disciplines that can be used via the Architecture Value Block mechanism from sos-trades-core.
To be able to access these values blocks, the folder containing them must be set in:
`sostrades-core\sos_trades_core\execution_engine\archi_builder.py`

The folder `'value_assessment.sos_wrapping.valueblock_disciplines'` must be added to the variable **`FULL_VB_FOLDER_LIST`**
                           

## Overview
This package is divided in 4 parts:

- core: contains all the methods and wrapped class of value-asessment tools necessary to implement processes and studies in SoSTrades
- sos_processes: contains test processes built with disciplines from sos_wrapping
- sos_wrapping: contains test disciplines covering value assessment functionalities
- tests: contains tests on value assessment functionalities, based on sos_processes and sos_wrapping
