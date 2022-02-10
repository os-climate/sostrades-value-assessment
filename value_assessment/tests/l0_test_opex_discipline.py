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
from sos_trades_core.execution_engine.execution_engine import ExecutionEngine


class OPEXDiscTest(unittest.TestCase):

    def setUp(self):

        self.name = 'OPEXDiscTest'
        self.ee = ExecutionEngine(self.name)
        self.model_name = 'OPEX_Discipline'

        ns_dict = {
            'ns_data_product': f'{self.name}.{self.model_name}',
            'ns_product': f'{self.name}.{self.model_name}',
            'ns_opex': f'{self.name}.{self.model_name}',
            'ns_public': f'{self.name}',
            'ns_opex_input_details': f'{self.name}.{self.model_name}',
            'ns_opex_results': f'{self.name}.{self.model_name}',
        }

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'value_assessment.sos_wrapping.opex.opex_discipline.OPEXDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        self.launch_year = 2030
        self.year_start = 2025
        self.year_end = 2050
        self.opex_by_category = pd.DataFrame({'components': ['comp1', 'comp2', 'comp3',
                                                             'comp4',  'comp5'],
                                              'opex': [1863.,  1864.,  1683.,
                                                       909., 341.]})
        self.escalation_opex_df = pd.DataFrame({
            'year_economical_conditions': [2021],
            'yearly_escalation_rate': [2.0]})

        self.sales_df = pd.DataFrame(
            {'years': np.arange(2020, 2051), 'quantity': 50.0})
        self.sales_df.loc[self.sales_df['years'] < 2030, 'quantity'] = 0
        self.opex_multiplier = 100.0

        self.values_dict = {
            f'{self.name}.{self.model_name}.launch_year': self.launch_year,
            f'{self.name}.{self.model_name}.escalation_opex_df': self.escalation_opex_df,
            f'{self.name}.year_start': self.year_start,
            f'{self.name}.year_end': self.year_end,
            f'{self.name}.{self.model_name}.opex_by_category': self.opex_by_category,
            f'{self.name}.{self.model_name}.product_sales_df': self.sales_df,
            f'{self.name}.{self.model_name}.opex_multiplier': self.opex_multiplier,
        }

    def test_01_compute_at_product_level(self):

        self.ee.load_study_from_input_dict(self.values_dict)

        self.ee.execute()

        opex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.opex')

        opex_ref = pd.DataFrame({
            'opex': [0.0, 0.0, 0.0, 0.0, 0.0, 7959.316507024591, 8118.502837165084, 8280.872893908385, 8446.490351786553, 8615.420158822284, 8787.72856199873, 8963.483133238706, 9142.75279590348, 9325.607851821549, 9512.12000885798, 9702.36240903514, 9896.409657215843, 10094.33785036016, 10296.224607367363, 10502.149099514712, 10712.192081505005, 10926.435923135106, 11144.964641597808, 11367.863934429764, 11595.22121311836, 11827.125637380728]
        })
        pd.util.testing.assert_frame_equal(
            opex[['opex']], opex_ref[['opex']])

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0]
        filter = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filter)
        # for graph in graph_list:
        #     graph.to_plotly().show()

    def test_03_launch_year_before_year_start(self):

        self.values_dict.update(
            {f'{self.name}.{self.model_name}.launch_year': 2010})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        opex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.opex')

        opex_ref = pd.DataFrame({'opex': [7208.9981855999995, 7353.178149312, 7500.241712298241, 7650.246546544205, 7803.25147747509, 7959.316507024591, 8118.502837165084, 8280.872893908385, 8446.490351786553, 8615.420158822284, 8787.72856199873, 8963.483133238706, 9142.75279590348, 9325.607851821549, 9512.12000885798, 9702.36240903514, 9896.409657215843, 10094.33785036016, 10296.224607367363, 10502.149099514712, 10712.192081505005, 10926.435923135106, 11144.964641597808, 11367.863934429764, 11595.22121311836, 11827.125637380728]
                                 })
        pd.util.testing.assert_frame_equal(
            opex[['opex']], opex_ref[['opex']], 'Error : Launch year can not be set before year start')

    def test_04_launch_year_after_year_end(self):

        self.values_dict.update(
            {f'{self.name}.{self.model_name}.launch_year': 2070})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        opex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.opex')

        opex_ref = pd.DataFrame({'opex': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                                 })

        pd.util.testing.assert_frame_equal(
            opex[['opex']], opex_ref[['opex']], 'Error : Launch year can not be set after year end')

    def test_05_year_esc_before_year_start(self):
        self.values_dict.update(
            {f'{self.name}.{self.model_name}.escalation_opex_df': pd.DataFrame({
                'year_economical_conditions': [2010],
                'yearly_escalation_rate': [2.0]})})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        opex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.opex')

        opex_ref = pd.DataFrame({'opex': [0.0, 0.0, 0.0, 0.0, 0.0, 9896.409657215843, 10094.33785036016, 10296.224607367363, 10502.149099514712, 10712.192081505005, 10926.435923135106, 11144.964641597808, 11367.863934429764, 11595.22121311836, 11827.125637380728, 12063.668150128344, 12304.94151313091, 12551.040343393528, 12802.0611502614, 13058.102373266627, 13319.26442073196, 13585.649709146599, 13857.362703329532, 14134.509957396122, 14417.200156544044, 14705.544159674924]
                                 })

        pd.util.testing.assert_frame_equal(
            opex[['opex']], opex_ref[['opex']], 'Error : year_start_escalation can not be set before year start')

    def test_07_learning_curve(self):
        self.values_dict.update(
            {f'{self.name}.percentage_Make': 70.})

        self.ee.load_study_from_input_dict(self.values_dict)

        self.ee.execute()

        opex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.opex')

        opex_ref = pd.DataFrame({
            'opex': [0.0, 0.0, 0.0, 0.0, 0.0, 7959.316507024591, 8118.502837165084, 8280.872893908385, 8446.490351786553, 8615.420158822284, 8787.72856199873, 8963.483133238706, 9142.75279590348, 9325.607851821549, 9512.12000885798, 9702.36240903514, 9896.409657215843, 10094.33785036016, 10296.224607367363, 10502.149099514712, 10712.192081505005, 10926.435923135106, 11144.964641597808, 11367.863934429764, 11595.22121311836, 11827.125637380728]
        })
        pd.util.testing.assert_frame_equal(
            opex[['opex']], opex_ref[['opex']])


if __name__ == "__main__":
    unittest.main()
