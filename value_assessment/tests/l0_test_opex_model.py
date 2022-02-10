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
from value_assessment.core.opex import Opex


class OpexModelTest(unittest.TestCase):
    def setUp(self):

        self.launch_year = 2030
        self.year_start = 2025
        self.year_end = 2050
        self.learning_curve_dict = {
            'percentage_make': 0., 'learning_curve_coefficient': [0.8, 0.9], 'until_product_rank': [50., 200], }
        self.opex_by_category = pd.DataFrame({'components': ['comp1', 'comp2', 'comp3',
                                                             'comp4',  'comp5'],
                                              'opex': [1863.,  1864.,  1683.,
                                                       909., 341.]})
        # self.escalation_opex_df = pd.DataFrame({
        #     'year_economical_conditions': [2021],
        #     'yearly_escalation_rate': [2.0]})

        self.sales_df = pd.DataFrame(
            {'years': np.arange(2020, 2051), 'quantity': 50.0})
        self.sales_df.loc[self.sales_df['years'] < 2030, 'quantity'] = 0
        self.opex_multiplier = 100.0
        self.year_escalation_opex = 2021
        self.escalation_opex = 2.0

        # instantiate Opex model
        self.opex_model = Opex(
            escalation_rate=self.escalation_opex / 100.,
            year_start_escalation_rate=self.year_escalation_opex,
            launch_year=self.launch_year,
            year_start=self.year_start,
            year_end=self.year_end,
            learning_curve_dict=self.learning_curve_dict
        )

        self.ref_opex = pd.DataFrame(
            {
                'years': {0: 2025, 1: 2026, 2: 2027, 3: 2028, 4: 2029, 5: 2030, 6: 2031, 7: 2032, 8: 2033, 9: 2034, 10: 2035, 11: 2036, 12: 2037, 13: 2038, 14: 2039, 15: 2040, 16: 2041, 17: 2042, 18: 2043, 19: 2044, 20: 2045, 21: 2046, 22: 2047, 23: 2048, 24: 2049, 25: 2050},
                'opex_wo_escalation': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 6660.0, 6: 6660.0, 7: 6660.0, 8: 6660.0, 9: 6660.0, 10: 6660.0, 11: 6660.0, 12: 6660.0, 13: 6660.0, 14: 6660.0, 15: 6660.0, 16: 6660.0, 17: 6660.0, 18: 6660.0, 19: 6660.0, 20: 6660.0, 21: 6660.0, 22: 6660.0, 23: 6660.0, 24: 6660.0, 25: 6660.0},
                'learning_curve_coef': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 1.7504758369369793, 6: 1.163459820395767, 7: 1.0746639903174695, 8: 1.0206701531218665, 9: 1.0, 10: 1.0, 11: 1.0, 12: 0.9999999999999989, 13: 1.0000000000000022, 14: 1.0, 15: 1.0, 16: 1.0, 17: 1.0, 18: 1.0, 19: 1.0, 20: 1.0000000000000022, 21: 0.9999999999999978, 22: 1.0, 23: 1.0000000000000022, 24: 0.9999999999999954, 25: 1.0},
                'opex_Make': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0},
                'opex_Buy': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 7959.316507024591, 6: 8118.502837165084, 7: 8280.872893908385, 8: 8446.490351786553, 9: 8615.420158822284, 10: 8787.72856199873, 11: 8963.483133238706, 12: 9142.75279590348, 13: 9325.607851821549, 14: 9512.12000885798, 15: 9702.36240903514, 16: 9896.409657215843, 17: 10094.33785036016, 18: 10296.224607367363, 19: 10502.149099514712, 20: 10712.192081505005, 21: 10926.435923135106, 22: 11144.964641597808, 23: 11367.863934429764, 24: 11595.22121311836, 25: 11827.125637380728},
                'opex': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 7959.316507024591, 6: 8118.502837165084, 7: 8280.872893908385, 8: 8446.490351786553, 9: 8615.420158822284, 10: 8787.72856199873, 11: 8963.483133238706, 12: 9142.75279590348, 13: 9325.607851821549, 14: 9512.12000885798, 15: 9702.36240903514, 16: 9896.409657215843, 17: 10094.33785036016, 18: 10296.224607367363, 19: 10502.149099514712, 20: 10712.192081505005, 21: 10926.435923135106, 22: 11144.964641597808, 23: 11367.863934429764, 24: 11595.22121311836, 25: 11827.125637380728},
                'opex_after_sales': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 1512.2701363346725, 6: 893.0353120881592, 7: 662.4698315126708, 8: 591.2543246250588, 9: 516.925209529337, 10: 439.3864280999365, 11: 448.1741566619352, 12: 457.137639795174, 13: 466.2803925910775, 14: 475.606000442899, 15: 485.118120451757, 16: 494.8204828607922, 17: 504.71689251800797, 18: 514.8112303683681, 19: 525.1074549757355, 20: 535.6096040752503, 21: 546.3217961567553, 22: 557.2482320798904, 23: 568.3931967214883, 24: 579.7610606559181, 25: 591.3562818690364}
            })

        self.ref_opex = self.ref_opex.astype({'years': 'int32'})

        self.after_sales_opex_unit_dict = {'launch_year': 19., 'launch_year+1': 11., 'launch_year+2': 8., 'launch_year+3': 7.,
                                           'launch_year+4': 6., 'launch_year+5': 5., 'launch_year+6': 5., 'launch_year+7': 5., 'launch_year+8': 5., 'launch_year+9': 5., 'launch_year+10 onwards': 5.}

        self.after_sales_opex_unit = np.array(
            list(self.after_sales_opex_unit_dict.values())) / 100.0

    def test_01_compute(self):

        opex_df = self.opex_model.compute_opex_by_category(
            opex_by_category=self.opex_by_category,
            sales=self.sales_df,
            opex_multiplier=self.opex_multiplier / 100.0,
            distrib_after_sales_opex_unit=self.after_sales_opex_unit)

        opex_df = opex_df.astype({'years': 'int32'})

        assert_frame_equal(opex_df[['years', 'opex_wo_escalation',
                                    'learning_curve_coef', 'opex_Make', 'opex_Buy', 'opex', 'opex_after_sales']], self.ref_opex)

    def test_02_apply_ratio(self):
        new_opex_multiplier = 5.0 / 100
        opex_df = self.opex_model.compute_opex_by_category(
            opex_by_category=self.opex_by_category,
            sales=self.sales_df,
            opex_multiplier=new_opex_multiplier,
            distrib_after_sales_opex_unit=self.after_sales_opex_unit)

        opex_df = opex_df.astype({'years': 'int32'})

        new_ref_opex = self.ref_opex.copy(deep=True)
        for col in ['opex_wo_escalation', 'opex_Make', 'opex_Buy', 'opex', 'opex_after_sales']:
            new_ref_opex[col] = new_ref_opex[col] * new_opex_multiplier

        assert_frame_equal(opex_df[['years', 'opex_wo_escalation',
                                    'learning_curve_coef', 'opex_Make', 'opex_Buy', 'opex', 'opex_after_sales']], new_ref_opex)


if __name__ == "__main__":
    unittest.main()
