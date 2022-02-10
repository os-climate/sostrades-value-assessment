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
'''
mode: python; py-indent-offset: 4; tab-width: 8; coding: utf-8
'''




import unittest
import pprint
from sos_trades_core.sos_processes.multiple_configure_and_run_tools import run_twice_all_usecases_and_compare_dm, configure_twice_all_usecases_and_compare_dm
class TestUseCases(unittest.TestCase):
    """
    Usecases test class
    """

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.pp = pprint.PrettyPrinter(indent=4, compact=True)
        self.processes_repo = 'value_assessment.sos_processes'
        self.maxDiff = None

    def test_01_configure_usecases_twice(self):
        test_passed, output_error = configure_twice_all_usecases_and_compare_dm(
            self.processes_repo)
        if not test_passed:
            raise Exception(f'{output_error}')

    def test_02_run_usecases_twice(self):
        test_passed, output_error = run_twice_all_usecases_and_compare_dm(
            self.processes_repo)
        if not test_passed:
            raise Exception(f'{output_error}')


if __name__ == "__main__":
    unittest.main()
