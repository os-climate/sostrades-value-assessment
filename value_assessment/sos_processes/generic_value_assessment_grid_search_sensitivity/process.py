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

from sos_trades_core.sos_processes.base_process_builder import BaseProcessBuilder


class ProcessBuilder(BaseProcessBuilder):

    # ontology information
    _ontology_data = {
        'label': 'Generic Value Assessment Grid Search Sensitivity Process',
        'description': '',
        'version': 'Version 1',
    }

    def get_builders(self):

        process_builder = []

        builder_cdf_list = self.ee.factory.get_builder_from_process(
            'value_assessment.sos_processes', 'generic_value_assessment'
        )

        for ns in self.ee.ns_manager.ns_list:
            self.ee.ns_manager.update_namespace_with_extra_ns(
                ns, 'GridSearch', after_name=self.ee.study_name
            )
        grid_search_builder = self.ee.factory.create_evaluator_builder(
            'GridSearch', 'grid_search', builder_cdf_list
        )
        process_builder.append(grid_search_builder)

        uncertainty_quantification = 'UncertaintyQuantification'
        mod_path = 'sos_trades_core.sos_wrapping.analysis_discs.uncertainty_quantification.UncertaintyQuantification'
        uq_builder = self.ee.factory.get_builder_from_module(
            uncertainty_quantification, mod_path
        )
        process_builder.append(uq_builder)

        # add namespaces used by output model
        ns_dict = {
            'ns_uncertainty_quantification': f'{self.ee.study_name}.UncertaintyQuantification',
            'ns_doe_eval': f'{self.ee.study_name}.GridSearch',
            'ns_grid_search': f'{self.ee.study_name}.GridSearch',
        }
        self.ee.ns_manager.add_ns_def(ns_dict)

        return process_builder
