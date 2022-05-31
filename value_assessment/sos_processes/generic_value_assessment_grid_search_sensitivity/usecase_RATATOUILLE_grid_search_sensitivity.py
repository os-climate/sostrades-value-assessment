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
# mode: python; py-indent-offset: 4; tab-width: 8; coding:utf-8

from os.path import join, dirname
import pandas as pd

from value_assessment.sos_processes.generic_value_assessment.usecase_RATATOUILLE import (
    Study as ratatouille_usecase,
)
from sos_trades_core.study_manager.study_manager import StudyManager


class Study(StudyManager):
    def __init__(self, run_usecase=False, execution_engine=None):
        super().__init__(
            __file__, run_usecase=run_usecase, execution_engine=execution_engine
        )
        self.data_dir = join(dirname(__file__), 'data')

    def setup_usecase(self):

        usecase = ratatouille_usecase()
        grid_search_name = 'GridSearch'
        usecase.study_name = f'{self.study_name}.{grid_search_name}'
        setup_data_list = usecase.setup_usecase()

        eval_inputs = pd.read_csv(
            join(dirname(__file__), 'data', f'eval_inputs.csv'), encoding="latin-1"
        )

        eval_outputs = pd.read_csv(
            join(dirname(__file__), 'data', f'eval_outputs.csv'),
            encoding="latin-1",
        )

        dspace = pd.read_csv(
            join(dirname(__file__), 'data', f'design_space.csv'),
            encoding="latin-1",
        )

        dict_values = {
            f'{self.study_name}.cache_type': 'SimpleCache',
            f'{usecase.study_name}.eval_inputs': eval_inputs,
            f'{usecase.study_name}.eval_outputs': eval_outputs,
            f'{usecase.study_name}.design_space': dspace,
        }

        setup_data_list[0].update(dict_values)

        return setup_data_list


if '__main__' == __name__:
    uc_cls = Study(run_usecase=True)
    uc_cls.load_data()
    uc_cls.run(logger_level='DEBUG', for_test=True)
    print('DONE')
