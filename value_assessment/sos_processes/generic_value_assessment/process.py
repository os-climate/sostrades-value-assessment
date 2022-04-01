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

# -- Generate test 2 process
from sos_trades_core.sos_processes.base_process_builder import BaseProcessBuilder
import pandas as pd


class ProcessBuilder(BaseProcessBuilder):

    # ontology information
    _ontology_data = {
        'label': 'Generic Value Assessment Process',
        'description': '',
        'category': '',
        'version': '',
    }

    def get_builders(self):

        study_name = self.ee.study_name
        opex_name = 'OpEx'
        capex_name = 'CapEx'
        business_name = 'Business_Manufacturer'

        builder_list = []

        ns_dict = {
            'ns_barrier': study_name,
            'ns_data_product': f'{study_name}',
            'ns_product': f'{study_name}',
            'ns_opex': f'{study_name}.{opex_name}',
            'ns_capex': f'{study_name}.{capex_name}',
            'ns_public': f'{study_name}',
            'ns_opex_input_details': f'{study_name}.{opex_name}',
            'ns_capex_input_details': f'{study_name}.{capex_name}',
            'ns_opex_results': f'{study_name}',
            'ns_capex_results': f'{study_name}',
            'ns_va_product': f'{study_name}.{business_name}.Manufacturer',
        }

        # scatter on Product list
        product_list_map_dict = {
            'input_name': 'Product_list',
            'input_type': 'string_list',
            'input_ns': 'ns_barrier',
            'output_name': 'Product_name',
            'scatter_ns': 'ns_product',
            'gather_ns_in': 'ns_barrier',
            'ns_to_update': [
                'ns_data_product',
                'ns_opex_input_details',
                'ns_opex_results',
                'ns_capex_results',
                'ns_va_product',
                'ns_capex_input_details',
                'ns_product',
            ],
        }
        # add product list map
        self.ee.smaps_manager.add_build_map('Product_list', product_list_map_dict)

        mods_dict = {
            'OpEx': 'value_assessment.sos_wrapping.opex.opex_discipline.OPEXDiscipline',
            'CapEx': 'value_assessment.sos_wrapping.capex.capex_discipline.CAPEXDiscipline',
        }

        opex_capex_builder_list = self.create_builder_list(mods_dict, ns_dict=ns_dict)

        # create scatter on cost category list
        opex_capex_scatter_builder = (
            self.ee.factory.create_multi_scatter_builder_from_list(
                'Product_list', opex_capex_builder_list, autogather=True
            )
        )

        builder_list.append(opex_capex_scatter_builder)

        # Value block architecture
        archi_name = 'Business_Manufacturer'

        architecture_df = pd.DataFrame(
            {
                'Parent': [None, archi_name],
                'Current': [archi_name, 'Manufacturer'],
                'Type': [
                    'SumValueAssessmentActorValueBlockDiscipline',
                    'SumValueAssessmentValueBlockDiscipline',
                ],
                'Action': [
                    ('standard'),
                    ('scatter', 'Product_list', 'ManufacturerValueBlockDiscipline'),
                ],
                'Activation': [True, False],
            }
        )

        vb_folder_list = ['value_assessment.sos_wrapping.valueblock_disciplines']
        vb_architecture_builder = self.ee.factory.create_architecture_builder(
            archi_name, architecture_df, vb_folder_list
        )

        builder_list.append(vb_architecture_builder)

        return builder_list
