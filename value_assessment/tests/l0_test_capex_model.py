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
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from value_assessment.core.capex import Capex
from sos_trades_core.api import get_sos_logger


class CapexModelTest(unittest.TestCase):

    def setUp(self):

        self.launch_year = 2030
        self.year_start = 2025
        self.year_end = 2050

        self.sales_df = pd.DataFrame(
            {'years': np.arange(2020, 2051), 'quantity': 50.0})
        self.sales_df.loc[self.sales_df['years'] < 2030, 'quantity'] = 0
        self.capex_multiplier = 100.0
        self.year_start_escalation_rate = 2019
        self.escalation_rate = 0.02
        self.logger = get_sos_logger('capex')

        # instantiate Opex model
        self.capex_model = Capex(
            escalation_rate=self.escalation_rate,
            year_start_escalation_rate=self.year_start_escalation_rate,
            launch_year=self.launch_year,
            year_start=self.year_start,
            year_end=self.year_end,
            logger=self.logger)

        self.capex_distrib_categories = pd.DataFrame({
            'Distribution Category': ['development1', 'development2'],
            'launch_year-6': [0, 0],
            'launch_year-5': [15, 0],
            'launch_year-4': [20, 10],
            'launch_year-3': [20, 25],
            'launch_year-2': [25, 25],
            'launch_year-1': [20, 15],
            'launch_year': [0, 10],
            'launch_year+1': [0, 10],
            'launch_year+2': [0, 5],
            'launch_year+3': [0, 0],
            'launch_year+4 onwards': [0, 0],
        })

        self.capex_input_values = pd.DataFrame(
            {'Distribution Category': ['development1', 'development1', 'development2'],
             'Capex Component':  ['comp1', 'comp2', 'comp3'],
             'Capex value':  [1053.0, 478.0, 604.0],
             'Contingency (%)': [0.0, 0.0, 0.0]
             })

        self.capex_input_values['Capex value'] = self.capex_input_values['Capex value'] * 1000000
        self.ref_capex = pd.DataFrame(
            {
                'years': {0: 2025, 1: 2026, 2: 2027, 3: 2028, 4: 2029, 5: 2030, 6: 2031, 7: 2032, 8: 2033, 9: 2034, 10: 2035, 11: 2036, 12: 2037, 13: 2038, 14: 2039, 15: 2040, 16: 2041, 17: 2042, 18: 2043, 19: 2044, 20: 2045, 21: 2046, 22: 2047, 23: 2048, 24: 2049, 25: 2050},
                'capex': {0: 2.586232e+08, 1: 4.211082e+08, 2: 5.356827e+08, 3: 6.378807e+08, 4: 4.836970e+08, 5: 7.509981e+07, 6: 7.660180e+07, 7: 3.906692e+07, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0},
                'contingency': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0},
                'capex_development1': {0: 2.586232e+08, 1: 3.517276e+08, 2: 3.587621e+08, 3: 4.574217e+08, 4: 3.732561e+08, 5: 0.0, 6: 0.0, 7: 0.0,  8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0},
                'capex_development2': {0: 0.0, 1: 69380614.32601652, 2: 176920566.53134212, 3: 180458977.86196896, 4: 110440894.45152502, 5: 75099808.22703701, 6: 76601804.39157775, 7:  39066920.23970465, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0},
            })
        self.ref_capex = self.ref_capex.astype({'years': 'int32'})

    def test_01_compute(self):

        capex_df = self.capex_model.compute_capex_by_category(
            capex_input_values=self.capex_input_values,
            capex_distrib_categories=self.capex_distrib_categories)

        capex_df = capex_df.astype({'years': 'int32'})

        assert_frame_equal(capex_df[['years', 'capex', 'contingency', 'capex_development1',
                                     'capex_development2']], self.ref_capex)


if __name__ == "__main__":
    unittest.main()
