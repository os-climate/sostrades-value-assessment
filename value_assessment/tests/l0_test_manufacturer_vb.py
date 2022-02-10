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
from sos_trades_core.execution_engine.execution_engine import ExecutionEngine
import pandas as pd
from os.path import join, dirname


class ManufacturerVBDisciplineTest(unittest.TestCase):
    """
    Test of ManufacturerVBDiscipline
    """

    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.data_dir = join(dirname(__file__), 'data')
        self.name = 'Manufacturer_model'
        self.namespace = 'Sales'
        self.subsystem = 'Subsystem'
        self.repos = f'Product.{self.subsystem}'

        # Try to overwrite v_max mtow but not dmc_components

        sale_price_ref = pd.read_csv(
            join(dirname(__file__), 'data', 'sale_price_ref.csv'))

        sales_qty_df_ref = pd.read_csv(
            join(dirname(__file__), 'data', 'sale_quantity_ref.csv'))

        opex_ref = pd.read_csv(
            join(dirname(__file__), 'data', 'opex_ref.csv'))

        capex_ref = pd.read_csv(
            join(dirname(__file__), 'data', 'capex_ref.csv'))

        nb_years_capex_amort = pd.DataFrame({
            'Distribution Category': ['type1', 'type2', 'type3'],
            'Nb years': [0, 5, 2]})

        opex_advanced_payment_percentage = pd.DataFrame({
            'percentage_at_delivery_year-1': [20.],
            'percentage_at_delivery_year-2': [10.]})

        self.private_values = {
            f'{self.namespace}.{self.repos}.capex': capex_ref,
            f'{self.namespace}.{self.repos}.nb_years_capex_amort': nb_years_capex_amort,
            f'{self.namespace}.{self.repos}.product_sale_price': sale_price_ref,
            f'{self.namespace}.{self.repos}.product_sales_df': sales_qty_df_ref,
            f'{self.namespace}.{self.repos}.WACC_actor': 8.0,
            f'{self.namespace}.year_start': 2020,
            f'{self.namespace}.year_end': 2025,
            f'{self.namespace}.{self.repos}.launch_year': 2021,
            f'{self.namespace}.{self.repos}.sales_by_subsystem': True,
            f'{self.namespace}.{self.repos}.opex': opex_ref,
            f'{self.namespace}.{self.repos}.opex_advanced_payment_percentage': opex_advanced_payment_percentage,
            f'{self.namespace}.{self.repos}.escalation_capex_df': pd.DataFrame({'year_economical_conditions': [2020],
                                                                                'yearly_escalation_rate': [2], }),
            f'{self.namespace}.{self.repos}.escalation_opex_df': pd.DataFrame({'year_economical_conditions': [2020],
                                                                               'yearly_escalation_rate': [2], }),

        }

    def test_01_execute_discipline(self):

        exec_eng = ExecutionEngine(self.namespace)
        ns_dict = {'ns_product': f'{self.namespace}.{self.repos}',
                   'ns_data_product': f'{self.namespace}.{self.repos}',
                   'ns_public': f'{self.namespace}',
                   'ns_va_product': f'{self.namespace}.{self.repos}',
                   'ns_opex': f'{self.namespace}.{self.repos}',
                   'ns_sales_rate_effect': f'{self.namespace}.{self.repos}',
                   'ns_product_subsystem': f'{self.namespace}.{self.repos}',
                   'ns_subsystem': f'{self.namespace}.{self.repos}',
                   'ns_capex_subsystem': f'{self.namespace}.{self.repos}',
                   'ns_capex': f'{self.namespace}.{self.repos}',
                   'ns_capex_results': f'{self.namespace}.{self.repos}',
                   'ns_sales_input': f'{self.namespace}.{self.repos}',
                   'ns_opex_results': f'{self.namespace}.{self.repos}',
                   'ns_capex_details': f'{self.namespace}.{self.repos}',
                   }

        exec_eng.ns_manager.add_ns_def(ns_dict)

        factory = exec_eng.factory

        business_model_builder = factory.get_builder_from_module(
            self.repos, 'value_assessment.sos_wrapping.valueblock_disciplines.manufacturer_vb_discipline.ManufacturerValueBlockDiscipline')

        factory.set_builders_to_coupling_builder(business_model_builder)

        exec_eng.configure()
        exec_eng.display_treeview_nodes()

        exec_eng.load_study_from_input_dict(self.private_values)

        res = exec_eng.execute()

        cf_df = exec_eng.dm.get_value(
            f'{self.namespace}.{self.repos}.cashflow_product')

        output_cashflow_dcf = list(cf_df['cumulative_discounted_cf'])[-1]
        ref_cashflow = 620270.3330214443
        self.assertAlmostEqual(output_cashflow_dcf, ref_cashflow, delta=7)

#         # Charts
#         disc = exec_eng.dm.get_disciplines_with_name(
#             f'{self.namespace}.{self.repos}')[0]
#         filter = disc.get_chart_filter_list()
#         graph_list = disc.get_post_processing_list(filter)
#         for graph in graph_list:
#             graph.to_plotly().show()


if __name__ == "__main__":
    unittest.main()
