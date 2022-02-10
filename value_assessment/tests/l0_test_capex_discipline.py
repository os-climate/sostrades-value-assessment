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
import pandas as pd
from sos_trades_core.execution_engine.execution_engine import ExecutionEngine


class CAPEXDiscTest(unittest.TestCase):

    def setUp(self):

        self.name = 'CAPEXDiscTest'
        self.ee = ExecutionEngine(self.name)
        self.model_name = 'CAPEX_Discipline'

        ns_dict = {
            'ns_data_product': f'{self.name}.{self.model_name}',
            'ns_product': f'{self.name}.{self.model_name}',
            'ns_capex': f'{self.name}.{self.model_name}',
            'ns_public': f'{self.name}',
            'ns_capex_input_details': f'{self.name}.{self.model_name}',
            'ns_capex_results': f'{self.name}.{self.model_name}',
        }

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'value_assessment.sos_wrapping.capex.capex_discipline.CAPEXDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        self.launch_year = 2030
        self.year_start = 2018
        self.year_end = 2036

        self.escalation_capex_df = pd.DataFrame({
            'year_economical_conditions': [2030],
            'yearly_escalation_rate': [2.0]})

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
        self.capex_multiplier = 100.0

        self.values_dict = {
            f'{self.name}.{self.model_name}.launch_year': self.launch_year,
            f'{self.name}.{self.model_name}.escalation_capex_df': self.escalation_capex_df,
            f'{self.name}.year_start': self.year_start,
            f'{self.name}.year_end': self.year_end,
            f'{self.name}.{self.model_name}.capex_multiplier': self.capex_multiplier,

            f'{self.name}.{self.model_name}.capex_input_values': self.capex_input_values,
            f'{self.name}.{self.model_name}.capex_distrib_categories': self.capex_distrib_categories,
        }

    def test_01_compute_by_category(self):

        self.ee.load_study_from_input_dict(self.values_dict)

        self.ee.execute()

        capex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.capex')

        capex_ref = pd.DataFrame({
            'capex': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 208001080.47744018, 338681733.18132013, 430829771.35490876, 513023836.98577464, 389019607.8431372, 60400000.0, 61608000.0, 31420080.0, 0.0, 0.0, 0.0, 0.0]})
        pd.util.testing.assert_frame_equal(
            capex[['capex']], capex_ref[['capex']])

        disc = self.ee.dm.get_disciplines_with_name(
            f'{self.name}.{self.model_name}')[0]
        filter = disc.get_chart_filter_list()
        graph_list = disc.get_post_processing_list(filter)
        # for graph in graph_list:
        #     graph.to_plotly().show()

    def test_02_launch_year_before_year_start(self):

        self.values_dict.update(
            {f'{self.name}.{self.model_name}.launch_year': 2010})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        capex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.capex')

        capex_ref = pd.DataFrame({'capex': [
                                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]})
        pd.util.testing.assert_frame_equal(
            capex[['capex']], capex_ref[['capex']], 'Error : Launch year can not be set before year start')

    def test_03_launch_year_after_year_end(self):

        self.values_dict.update(
            {f'{self.name}.{self.model_name}.launch_year': 2070})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        capex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.capex')

        capex_ref = pd.DataFrame({'capex': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                                  })

        pd.util.testing.assert_frame_equal(
            capex[['capex']], capex_ref[['capex']], 'Error : Launch year can not be set after year end')

    def test_04_year_esc_before_year_start(self):
        self.values_dict.update(
            {f'{self.name}.{self.model_name}.escalation_capex_df': pd.DataFrame({
                'year_economical_conditions': [2010],
                'yearly_escalation_rate': [2.0]})})
        self.ee.load_study_from_input_dict(self.values_dict)
        self.ee.execute()

        capex = self.ee.dm.get_value(f'{self.name}.{self.model_name}.capex')

        capex_ref = pd.DataFrame({'capex': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 309078663.8961364, 503263239.4862185, 640190376.8547766,
                                            762326434.643836, 578062673.2590306, 89751222.71709263, 91546247.17143448, 46688586.057431586, 0.0, 0.0, 0.0, 0.0]})

        pd.util.testing.assert_frame_equal(
            capex[['capex']], capex_ref[['capex']], 'Error : year_start_escalation can not be set before year start')


if __name__ == "__main__":
    unittest.main()
