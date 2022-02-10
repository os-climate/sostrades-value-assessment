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
from sos_trades_core.study_manager.study_manager import StudyManager


class Study(StudyManager):

    def __init__(self):
        super().__init__(__file__)

    def setup_usecase(self):

        setup_data_dict = {}
        setup_data_dict[f'{self.study_name}.Business_Manufacturer.Manufacturer.Product_list'] = [
            'Ratatouille', 'Tomato sauce']
        setup_data_dict[f'{self.study_name}.Business_Manufacturer.activation_df'] = pd.DataFrame({
            'Business_Manufacturer': [True, True],
            'Product_list': ['Ratatouille', 'Tomato sauce'],
            'Manufacturer': [True, True],
        })
        setup_data_dict[f'{self.study_name}.CapEx.Ratatouille.capex_distrib_categories'] = pd.DataFrame({
            'Distribution Category': ['Cuisine setup', 'Facility'],
            'launch_year-6': [0, 0],
            'launch_year-5': [0, 0],
            'launch_year-4': [0, 0],
            'launch_year-3': [0, 0],
            'launch_year-2': [0, 0],
            'launch_year-1': [0, 0],
            'launch_year': [100, 100],
            'launch_year+1': [0, 0],
            'launch_year+2': [0, 0],
            'launch_year+3': [0, 0],
            'launch_year+4 onwards': [0, 0],
        })
        setup_data_dict[f'{self.study_name}.CapEx.Ratatouille.capex_input_values'] = pd.DataFrame({
            'Distribution Category': ['Cuisine setup', 'Facility'],
            'Capex Component': ['Cuisine tools', 'Room'],
            'Capex value': [10000, 400000],
            'Contingency (%)': [0, 0],
        })
        setup_data_dict[f'{self.study_name}.CapEx.Tomato sauce.capex_distrib_categories'] = pd.DataFrame({
            'Distribution Category': ['Cuisine setup', 'Facility'],
            'launch_year-6': [0.0, 0.0],
            'launch_year-5': [0.0, 0.0],
            'launch_year-4': [0.0, 0.0],
            'launch_year-3': [0.0, 0.0],
            'launch_year-2': [0.0, 0.0],
            'launch_year-1': [0.0, 0.0],
            'launch_year': [100.0, 100.0],
            'launch_year+1': [0.0, 0.0],
            'launch_year+2': [0.0, 0.0],
            'launch_year+3': [0.0, 0.0],
            'launch_year+4 onwards': [0.0, 0.0],
        })
        setup_data_dict[f'{self.study_name}.CapEx.Tomato sauce.capex_input_values'] = pd.DataFrame({
            'Distribution Category': ['Cuisine setup', 'Facility'],
            'Capex Component': ['Cuisine tools', 'Room'],
            'Capex value': [10000, 400000],
            'Contingency (%)': [0, 0],
        })
        setup_data_dict[f'{self.study_name}.CapEx.escalation_capex_df'] = pd.DataFrame({
            'year_economical_conditions': [2020],
            'yearly_escalation_rate': [2.0],
        })
        setup_data_dict[f'{self.study_name}.OpEx.Ratatouille.opex_by_category'] = pd.DataFrame({
            'components': ['Tomato', 'Zucchini', 'Eggplant', 'Garlic', 'Rosemary', 'Glass jar', 'Preparation workload'],
            'opex': [2000, 1000, 1000, 30, 30, 500, 100],
        })
        setup_data_dict[f'{self.study_name}.OpEx.Tomato sauce.opex_by_category'] = pd.DataFrame({
            'components': ['Tomato', 'Garlic', 'Glass jar', 'Preparation workload'],
            'opex': [4000, 30, 500, 100],
        })
        setup_data_dict[f'{self.study_name}.OpEx.escalation_opex_df'] = pd.DataFrame({
            'year_economical_conditions': [2020],
            'yearly_escalation_rate': [2.0],
        })
        setup_data_dict[f'{self.study_name}.Product_list'] = [
            'Ratatouille', 'Tomato sauce']
        setup_data_dict[f'{self.study_name}.Ratatouille.launch_year'] = 2020
        setup_data_dict[f'{self.study_name}.Ratatouille.product_sale_price'] = pd.read_csv(
            join(dirname(__file__), 'data', 'Ratatouille_product_sale_price.csv'))
        setup_data_dict[f'{self.study_name}.Ratatouille.product_sales_df'] = pd.read_csv(
            join(dirname(__file__), 'data', 'Ratatouille_product_sales_df.csv'))
        setup_data_dict[f'{self.study_name}.Tomato sauce.launch_year'] = 2025
        setup_data_dict[f'{self.study_name}.Tomato sauce.product_sale_price'] = pd.read_csv(
            join(dirname(__file__), 'data', 'Tomato sauce_product_sale_price.csv'))
        setup_data_dict[f'{self.study_name}.Tomato sauce.product_sales_df'] = pd.read_csv(
            join(dirname(__file__), 'data', 'Tomato sauce_product_sales_df.csv'))

        return [setup_data_dict]


if '__main__' == __name__:
    uc_cls = Study()
    uc_cls.load_data()
    uc_cls.run(logger_level='DEBUG', for_test=False)
