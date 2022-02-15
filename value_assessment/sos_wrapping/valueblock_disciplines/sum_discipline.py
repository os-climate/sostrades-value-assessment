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

from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from value_assessment.core.toolbox.toolboxsumCF import toolboxsumCF
from sos_trades_core.sos_wrapping.sum_valueblock_discipline import SumValueBlockDiscipline
from value_assessment.sos_wrapping.post_processing.post_proc_output import ValueAssessmentCharts
from copy import deepcopy


class SumValueAssessmentValueBlockDiscipline(SumValueBlockDiscipline):
    """
    """

    # ontology information
    _ontology_data = {
        'label': 'Value Assessment Value Block Sum Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': '',
        'version': '',
    }
    _maturity = 'Research'

    def init_execution(self):
        self.toolboxsumcf = toolboxsumCF()

    def run(self):

        SumValueBlockDiscipline.run(self)
        output_dict_generic = self.get_sosdisc_outputs()
        if 'cashflow_product' in output_dict_generic:
            cf_product_dict = output_dict_generic['cashflow_product']

            cashflow_infos = self.toolboxsumcf.compute_cf_df_info(
                cf_product_dict)

            dict_values = {f'cashflow_infos': cashflow_infos
                           }
    #         if 'pnl_product' in output_dict_generic:
    #             pnl_product_dict = output_dict_generic['pnl_product']
    #             toolboxsumcf = toolboxsumCF()
    #
    #             pnl_product = toolboxsumcf.compute_cf_df_info(pnl_product_dict)
    #             dict_values.update({f'pnl_product': pnl_product})

            self.store_sos_outputs_values(dict_values)

        if 'percentage_ressource' in output_dict_generic:
            dict_values = {
                f'percentage_ressource': output_dict_generic['percentage_ressource']}
            self.store_sos_outputs_values(dict_values)

        if ('hypothesis_summary' in output_dict_generic) & ('hypothesis_summary_gather' in output_dict_generic):
            hypothesis = output_dict_generic['hypothesis_summary']
            hypothesis_gather = output_dict_generic['hypothesis_summary_gather']

            hypothesis_summary = self.toolboxsumcf.compute_hypothesis_df_info(
                hypothesis, hypothesis_gather)

            dict_values = {f'hypothesis_summary': hypothesis_summary
                           }

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = [
            'Cashflow',
            'Cash_in / Cash_out',
            'Detailed Cashflow',
            'Summary infos table',
            'Value Assessment'
        ]

        if 'pnl_product' in self.get_sosdisc_outputs():
            chart_list.append('Profit and Loss')
            chart_list.append('Profit and Loss Waterfall')

        chart_filters.append(ChartFilter(
            'Charts sum', chart_list, chart_list, 'Charts sum'))

        if 'cashflow_product_gather' in self.get_sosdisc_outputs():
            cashflow_product_gather = self.get_sosdisc_outputs(
                f'cashflow_product_gather')
            granularity = {}
            for k in cashflow_product_gather.keys():
                g = len(k.split('.'))
                if g in granularity:
                    granularity[g].append(k)
                else:
                    granularity[g] = [k]

            # add granularity 0
            granularity[0] = ['Total']
            granularity_sorted = dict(sorted(granularity.items()))
            selected_granularity = 0 if 0 in granularity_sorted else min(
                list(granularity_sorted.keys()))

            chart_filters.append(ChartFilter(f'Output Granularity details', filter_values=list(granularity_sorted.keys()),
                                             selected_values=selected_granularity, filter_key=f'Output Granularity details', multiple_selection=False))

        chart_filters.append(ChartFilter(name='Currency', filter_values=[
                             '€', '$'], selected_values='€', filter_key='Currency', multiple_selection=False))
        return chart_filters

    def get_post_processing_list(self, chart_filters=None):

        instanciated_charts = []
        currency = '€'

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'Charts sum':
                    graphs_list = chart_filter.selected_values
                if chart_filter.filter_key == 'Output Granularity details':
                    granularity_level = chart_filter.selected_values
                if chart_filter.filter_key == 'Currency':
                    currency = chart_filter.selected_values

        name = self.sos_name.split('.')[-1]
        va_charts = ValueAssessmentCharts()

        cashflow_info = None
        cashflow_product = None
        cashflow_product_gather = None
        cashflow_infos_gather = None
        EBIT_product = None
        EBIT_product_gather = None

        # handle retrieval of all outputs depending on the currency selected
        if currency == '€':
            if 'cashflow_infos' in self.get_sosdisc_outputs():
                cashflow_info = deepcopy(
                    self.get_sosdisc_outputs(f'cashflow_infos'))
            if 'cashflow_infos_gather' in self.get_sosdisc_outputs():
                cashflow_infos_gather = deepcopy(self.get_sosdisc_outputs(
                    f'cashflow_infos_gather'))
            if 'cashflow_product' in self.get_sosdisc_outputs():
                cashflow_product = self.get_sosdisc_outputs(
                    f'cashflow_product')
            if 'cashflow_product_gather' in self.get_sosdisc_outputs():
                cashflow_product_gather = self.get_sosdisc_outputs(
                    f'cashflow_product_gather')
            if 'pnl_product' in self.get_sosdisc_outputs():
                EBIT_product = self.get_sosdisc_outputs(f'pnl_product')
            if 'pnl_product_gather' in self.get_sosdisc_outputs():
                EBIT_product_gather = self.get_sosdisc_outputs(
                    f'pnl_product_gather')

        elif currency == '$':
            if 'cashflow_infos_dollars' in self.get_sosdisc_outputs():
                cashflow_info = deepcopy(self.get_sosdisc_outputs(
                    f'cashflow_infos_dollars'))
            if 'cashflow_infos_dollars_gather' in self.get_sosdisc_outputs():
                cashflow_infos_gather = deepcopy(self.get_sosdisc_outputs(
                    f'cashflow_infos_dollars_gather'))
            if 'cashflow_product_dollars' in self.get_sosdisc_outputs():
                cashflow_product = self.get_sosdisc_outputs(
                    f'cashflow_product_dollars')
            if 'cashflow_product_dollars_gather' in self.get_sosdisc_outputs():
                cashflow_product_gather = self.get_sosdisc_outputs(
                    f'cashflow_product_dollars_gather')
            if 'pnl_product_dollars' in self.get_sosdisc_outputs():
                EBIT_product = self.get_sosdisc_outputs(f'pnl_product_dollars')
            if 'pnl_product_dollars_gather' in self.get_sosdisc_outputs():
                EBIT_product_gather = self.get_sosdisc_outputs(
                    f'pnl_product_dollars_gather')

        annotation_upper_left = {}
        annotation_upper_right = {}
        hypothesis_summary = None
        hypothesis_summary_gather = None

        if 'hypothesis_summary' in self.get_sosdisc_outputs():
            hypothesis_summary = deepcopy(self.get_sosdisc_outputs(
                f'hypothesis_summary'))
        if 'hypothesis_summary_gather' in self.get_sosdisc_outputs():
            hypothesis_summary_gather = deepcopy(self.get_sosdisc_outputs(
                f'hypothesis_summary_gather'))

        if cashflow_info is not None:
            annotation_upper_left, annotation_upper_right = va_charts.generate_annotations(
                cashflow_info, currency=currency)

        granularity_to_draw = []
        if cashflow_product_gather is not None:
            granularity = {}
            for k in cashflow_product_gather.keys():
                g = len(k.split('.'))
                if g in granularity:
                    granularity[g].append(k)
                else:
                    granularity[g] = [k]
            if granularity_level in granularity:
                granularity_to_draw = granularity[granularity_level]

        if 'Summary infos table' in graphs_list and hypothesis_summary_gather is not None and cashflow_infos_gather is not None and cashflow_info is not None:
            # setup df
            cf_info_dict = {}
            if granularity_level == 0:
                if (hypothesis_summary is not None) & (cashflow_info is not None):
                    total_summary = deepcopy(hypothesis_summary)
                    total_summary.update(cashflow_info)
                    cf_info_dict[name] = total_summary
            else:
                total_summary_gather = deepcopy(hypothesis_summary_gather)
                for g in cashflow_infos_gather.keys():
                    if (g in granularity_to_draw) & (g in hypothesis_summary_gather.keys()):
                        total_summary_gather[g].update(
                            cashflow_infos_gather[g])
                        cf_info_dict[g] = total_summary_gather[g]
            new_table = va_charts.generate_total_table(
                cf_info_dict, name, currency, graph_data='Total')
            instanciated_charts.append(new_table)

        if 'Cashflow' in graphs_list and cashflow_product is not None:
            cashflow_chart = va_charts.generate_cashflow_chart(
                cashflow_product, name, annotation_upper_left, annotation_upper_right, currency=currency, add_cumulated=True)
            if cashflow_chart:
                instanciated_charts.append(cashflow_chart)

        if 'Cash_in / Cash_out' in graphs_list and cashflow_product is not None:
            cashflow_chart = va_charts.generate_cashin_cashout_chart(
                cashflow_product, name, annotation_upper_left, annotation_upper_right, currency=currency, add_cumulated=True)
            if cashflow_chart:
                instanciated_charts.append(cashflow_chart)

        if 'Detailed Cashflow' in graphs_list and cashflow_product_gather is not None:
            cf_df_dict = {}
            for g in cashflow_product_gather.keys():
                if g in granularity_to_draw:
                    cf_df_dict[g] = cashflow_product_gather[g]

            detailed_cashflow_chart = va_charts.generate_detailed_cashflow_chart(
                cf_df_dict, name, {}, {}, currency=currency)
            if detailed_cashflow_chart:
                instanciated_charts.append(detailed_cashflow_chart)

        if 'Profit and Loss' in graphs_list and EBIT_product is not None:
            pnl_chart = va_charts.generate_pnl_chart(
                EBIT_product, name, {}, {}, currency=currency, add_cumulated=True)
            if pnl_chart:
                instanciated_charts.append(pnl_chart)

        if 'Profit and Loss Waterfall' in graphs_list and EBIT_product_gather is not None:
            pnl_df_dict = {}
            for g in EBIT_product_gather.keys():
                if g in granularity_to_draw:
                    pnl_df_dict[g] = EBIT_product_gather[g]

            pnl_waterfall_chart_chart = va_charts.generate_pnl_waterfall_chart(
                pnl_df_dict, name, currency=currency)
            if pnl_waterfall_chart_chart:
                instanciated_charts.append(pnl_waterfall_chart_chart)

        if 'Value Assessment' in graphs_list and cashflow_infos_gather is not None:
            cf_info_dict = {}
            if granularity_level == 0:
                cf_info_dict[name] = [cashflow_info['total_free_cash_flow']]
            else:
                for g in cashflow_infos_gather.keys():
                    if g in granularity_to_draw:
                        cf_info_dict[g] = [
                            cashflow_infos_gather[g]['total_free_cash_flow']]
            value_assessment_chart = va_charts.generate_value_assessment_chart(
                cf_info_dict, name, currency)
            instanciated_charts.append(value_assessment_chart)

        return instanciated_charts
