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


from sos_trades_core.sos_wrapping.valueblock_discipline import ValueBlockDiscipline
from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, TwoAxesInstanciatedChart
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from value_assessment.sos_wrapping.post_processing.post_proc_output import ValueAssessmentCharts
from value_assessment.core.value_blocks.manufacturer_VB import ManufacturerVB
import numpy as np
import pandas as pd
from copy import deepcopy


class ManufacturerValueBlockDiscipline(ValueBlockDiscipline):
    """
    Sales value block that can be used either at product level or subcomponent level
    """

    # ontology information
    _ontology_data = {
        'label': 'Value Assessment Manufacturer Value Block Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fas fa-file-invoice-dollar fa-fw',
        'version': '',
    }
    _maturity = 'Research'

    DESC_IN = {
        'WACC_actor': {'type': 'float', 'unit': '%', 'default': 8., 'range': [0.0, 100.0], 'visibility': ValueBlockDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_public'},
        'year_start': {'default': 2020, 'type': 'int', 'unit': 'year', 'range': [1950, 2100], 'visibility': ValueBlockDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_public'},
        'year_end': {'default': 2050, 'type': 'int', 'unit': 'year', 'range': [1950, 2100], 'visibility': ValueBlockDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_public'},
        'launch_year': {'default': 2025, 'type': 'int', 'unit': 'year', 'range': [1950, 2100], 'visibility': ValueBlockDiscipline.SHARED_VISIBILITY, 'namespace': 'ns_data_product'},
        'opex_advanced_payment_percentage': {
            'type': 'dataframe',
            'unit': '%',
            'dataframe_descriptor': {
                'percentage_at_delivery_year-1': ('float', [0, 100], True),
                'percentage_at_delivery_year-2': ('float', [0, 100], True),
            },
            'dataframe_edition_locked': False,
            'default': pd.DataFrame({'percentage_at_delivery_year-1': [0.],
                                     'percentage_at_delivery_year-2': [0.]}),
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_va_product', 'user_level': 2},
        'nb_years_capex_amort': {
            'type': 'dataframe',
            'unit': 'years',
            'dataframe_descriptor': {
                'Distribution Category': ('string', None, True),
                'Nb years': ('int', [0, 100], True),
            },
            'default': pd.DataFrame({'Distribution Category': ['development1', 'development2'],
                                     'Nb years': [10, 5]}),
            'dataframe_edition_locked': False,
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_va_product', 'user_level': 2},
        'escalation_opex_df': {
            'type': 'dataframe',
            'unit': '',
            'visibility':  ValueBlockDiscipline.SHARED_VISIBILITY,
            'dataframe_descriptor': {
                'year_economical_conditions': ('int', None, True),
                'yearly_escalation_rate': ('float', [0.0, 100.0], True),
            },
            'dataframe_edition_locked': False,
            'namespace': 'ns_opex'
        },
        'escalation_capex_df': {
            'type': 'dataframe',
            'unit': '',
            'visibility':  ValueBlockDiscipline.SHARED_VISIBILITY,
            'dataframe_descriptor': {
                'year_economical_conditions': ('int', None, True),
                'yearly_escalation_rate': ('float', [0.0, 100.0], True),
            },
            'dataframe_edition_locked': False,
            'namespace': 'ns_capex'
        },
        'capex': {
            'type': 'dataframe',
            'unit': '€/year',
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_capex_results'
        },
        'product_sale_price': {
            'type': 'dataframe',
            'unit': '€/year',
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_product',
            'default': pd.DataFrame(
                {
                    'years': np.arange(2025, 2051),
                    'sale_price': [120.0] * 26
                }),
            'dataframe_descriptor': {
                'years': ('int', None, True),
                'sale_price': ('float', None, True)},
            'dataframe_edition_locked': False
        },
        'product_sales_df': {
            'type': 'dataframe',
            'unit': '#product/year',
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_product',
            'default': pd.DataFrame(
                {
                    'years': np.arange(2025, 2051),
                    'quantity': [100.0] * 26
                }),
            'dataframe_descriptor': {
                'years': ('int', None, True),
                'quantity': ('float', None, True)},
            'dataframe_edition_locked': False
        },
        'opex': {
            'type': 'dataframe',
            'unit': '€/year',
            'visibility': ValueBlockDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_results'
        },
    }

    DESC_OUT = {'cashflow_product': {'type': 'dataframe', 'unit': 'euros/year'},
                'cashflow_infos': {'type': 'dict', 'unit': ''},
                'hypothesis_summary': {'type': 'dict', 'unit': ''},
                'pnl_product': {'type': 'dataframe', 'unit': 'euros/year'}}

    def init_execution(self):
        input_data_dict = self.get_sosdisc_inputs(in_dict=True)

        product_sale_dict = {
            'opex_payment_term_percentage': input_data_dict['opex_advanced_payment_percentage'],
            'nb_years_capex_amort': input_data_dict['nb_years_capex_amort']
        }

        if input_data_dict['WACC_actor'] and input_data_dict['WACC_actor'] != 0:
            wacc = input_data_dict['WACC_actor'] / 100.
        else:
            wacc = 0

        self.sales_vb_model = ManufacturerVB(input_data_dict['year_start'], input_data_dict['year_end'],
                                             input_data_dict['launch_year'], product_sale_dict,
                                             None, wacc, 1)

    def run(self):

        # get inputs
        input_data_dict = self.get_sosdisc_inputs(in_dict=True)

        self.sales_vb_model.configure_data(
            input_data_dict['product_sales_df'],
            input_data_dict['opex'], input_data_dict['capex'],
            input_data_dict['product_sale_price'])

        self.sales_vb_model.compute_cashflow()

        cashflow_product = self.sales_vb_model.convert_cf_USD_EUR()
        cashflow_infos = self.sales_vb_model.convert_cf_infos_USD_EUR()

        self.sales_vb_model.compute_PnL()
        EBIT_product = self.sales_vb_model.convert_cf_USD_EUR()

        # hypothesis_summary
        sales = cashflow_product['quantity'].to_list()
        total_sales = np.cumsum(sales)[-1]
        capex = input_data_dict['capex']['capex'].to_list()
        total_capex = np.cumsum(capex)[-1]
        year_start_escalation_capex = input_data_dict['escalation_capex_df']['year_economical_conditions']
        opex = input_data_dict['opex']['opex'].to_list()
        year_start_escalation_opex = input_data_dict['escalation_opex_df']['year_economical_conditions']
        sale_price = cashflow_product['sale_price'].to_list()
        if sale_price[-1] != 0:
            contribution_margin = (sale_price[-1] - opex[-1]) / sale_price[-1]
        else:
            contribution_margin = 0.
        last_year = cashflow_product['years'].to_list()[-1]

        hypothesis_summary = {'total_cumul_sales': int(total_sales), 'year_start_escalation_capex': int(year_start_escalation_capex), 'total_cumul_capex': total_capex,
                              'year_start_escalation_opex': int(year_start_escalation_opex), 'last_year': int(last_year), 'opex_last_year': opex[-1], 'sale_price_last_year': sale_price[-1], 'contribution_margin_last_year': contribution_margin}

        dict_values = {
            f'cashflow_product': cashflow_product.loc[:, cashflow_product.columns.isin(['years', 'cash_flow', 'cumulative_cash_flow', 'discounted_cf', 'cumulative_discounted_cf',
                                                                                        'cash_in', 'cash_out', 'sale_price', 'quantity',
                                                                                        'capex_amort', 'capex_non_amort', 'capex', 'Inventory',
                                                                                        'opex', 'opex_total_pay', 'opex_total', 'opex_after_sales'])],
            f'cashflow_infos': cashflow_infos,
            f'hypothesis_summary': hypothesis_summary,

            f'pnl_product': EBIT_product.loc[:, EBIT_product.columns.isin(['years', 'EBIT', 'cumulative_EBIT',
                                                                           'cash_in_PnL', 'cash_out_PnL', 'sale_price', 'quantity',
                                                                           'capex_amort_EBIT', 'capex_non_amort', 'capex', 'Inventory',
                                                                           'opex', 'opex_total', 'opex_after_sales'])]

        }

        self.store_sos_outputs_values(dict_values)

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = [
            'Cashflow',
            'Cash_in / Cash_out',
            'Detailed Cashflow',
            'Summary infos table',
            'Quantity',
            'Price and Cost',
            'Profit and Loss',
            'Profit and Loss Waterfall',
            'OPEX',
            'CAPEX',
        ]

        chart_filters.append(ChartFilter(
            'Charts', chart_list, chart_list, 'Charts'))

        chart_filters.append(ChartFilter(name='Currency', filter_values=[
                             '€'], selected_values='€', filter_key='Currency', multiple_selection=False))

        return chart_filters

    def get_post_processing_list(self, chart_filters=None):

        instanciated_charts = []
        currency = '€'

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'Charts':
                    graphs_list = chart_filter.selected_values
                if chart_filter.filter_key == 'Currency':
                    currency = chart_filter.selected_values

        name = self.sos_name.split('.')[-1]
        bc_charts = ValueAssessmentCharts()
        cashflow_info = None
        cashflow_product = None
        EBIT_product = None
        hypothesis_summary = None

        # handle retrieval of all outputs depending on the currency selected
        if currency == '€':
            if 'cashflow_infos' in self.get_sosdisc_outputs():
                cashflow_info = deepcopy(
                    self.get_sosdisc_outputs(f'cashflow_infos'))
            if 'cashflow_product' in self.get_sosdisc_outputs():
                cashflow_product = self.get_sosdisc_outputs(
                    f'cashflow_product')
            if 'pnl_product' in self.get_sosdisc_outputs():
                EBIT_product = self.get_sosdisc_outputs(f'pnl_product')

        elif currency == '$':
            if 'cashflow_infos_dollars' in self.get_sosdisc_outputs():
                cashflow_info = deepcopy(self.get_sosdisc_outputs(
                    f'cashflow_infos_dollars'))
            if 'cashflow_product_dollars' in self.get_sosdisc_outputs():
                cashflow_product = self.get_sosdisc_outputs(
                    f'cashflow_product_dollars')
            if 'pnl_product_dollars' in self.get_sosdisc_outputs():
                EBIT_product = self.get_sosdisc_outputs(f'pnl_product_dollars')

        if 'hypothesis_summary' in self.get_sosdisc_outputs():
            hypothesis_summary = deepcopy(
                self.get_sosdisc_outputs(f'hypothesis_summary'))

        annotation_upper_left = {}
        annotation_upper_right = {}

        if cashflow_info is not None:
            annotation_upper_left, annotation_upper_right = bc_charts.generate_annotations(
                cashflow_info, currency=currency)

        # sales_by_subsystem = self.get_sosdisc_inputs('sales_by_subsystem')
        opex = self.get_sosdisc_inputs('opex')
        # if sales_by_subsystem:
        #     subsystem_name = self.sos_name
        opex_max = opex['opex'].max()
        # convert to k€
        opex_max /= 1000
        capex = self.get_sosdisc_inputs('capex')
        # else:
        #     capex = None

        if 'Summary infos table' in graphs_list:
            # setup df
            if hypothesis_summary is not None:
                total_summary = deepcopy(hypothesis_summary)
            total_summary.update(cashflow_info)
            new_table = bc_charts.generate_total_table(
                {name: total_summary}, name, currency, graph_data='Total')
            instanciated_charts.append(new_table)
            # new_table.to_plotly().show()

        if 'Cashflow' in graphs_list and cashflow_product is not None:
            cashflow_chart = bc_charts.generate_cashflow_chart(
                cashflow_product, name, annotation_upper_left, annotation_upper_right, currency=currency, add_cumulated=True)
            if cashflow_chart:
                instanciated_charts.append(cashflow_chart)

        if 'Cash_in / Cash_out' in graphs_list and cashflow_product is not None:
            cashflow_chart = bc_charts.generate_cashin_cashout_chart(
                cashflow_product, name, annotation_upper_left, annotation_upper_right, currency=currency, add_cumulated=True)
            if cashflow_chart:
                instanciated_charts.append(cashflow_chart)

        if 'Profit and Loss' in graphs_list and EBIT_product is not None:
            pnl_chart = bc_charts.generate_pnl_chart(
                EBIT_product, name, {}, {}, currency=currency, add_cumulated=True)
            if pnl_chart:
                instanciated_charts.append(pnl_chart)

        if 'Profit and Loss Waterfall' in graphs_list and EBIT_product is not None:

            pnl_df_dict = {name: EBIT_product}
            pnl_waterfall_chart_chart = bc_charts.generate_pnl_waterfall_chart(
                pnl_df_dict, name, currency=currency)
            if pnl_waterfall_chart_chart:
                instanciated_charts.append(pnl_waterfall_chart_chart)

        if 'Quantity' in graphs_list and cashflow_product is not None:
            quantity_chart = bc_charts.generate_quantity_chart(
                cashflow_product, name, {}, {}, add_cumulated=True)
            if pnl_chart:
                instanciated_charts.append(quantity_chart)

        if 'Price and Cost' in graphs_list and cashflow_product is not None:
            price_and_cost_chart = bc_charts.generate_price_and_cost_chart(
                cashflow_product, name, currency=currency)
            if price_and_cost_chart:
                instanciated_charts.append(price_and_cost_chart)

        if 'OPEX' in graphs_list and cashflow_product is not None:
            if 'opex_total' in cashflow_product.columns:
                max_value = max(
                    cashflow_product['opex_total'].values.tolist()) * 1.05

                if max_value >= 1.0e9:
                    max_value = max_value / 1.0e9
                    legend_letter = 'bn'
                    factor = 1.0e9
                elif max_value < 1.0e9 and max_value >= 1.0e6:
                    max_value = max_value / 1.0e6
                    legend_letter = 'M'
                    factor = 1.0e6
                elif max_value < 1.0e6 and max_value >= 1.0e3:
                    max_value = max_value / 1.0e3
                    legend_letter = 'k'
                    factor = 1.0e3
                else:
                    legend_letter = ''
                    factor = 1.0
                chart_name = f'{self.sos_name} Total OpEx Costs'

                new_chart_opex = TwoAxesInstanciatedChart('Years', f'OpEx({legend_letter}€)',
                                                          [],
                                                          [],
                                                          chart_name, stacked_bar=True)

                opex_wo_cont_supp = InstanciatedSeries(cashflow_product['years'].values.tolist(
                ), (cashflow_product['opex_total'].values / factor).tolist(), 'OpEx', 'bar')

                new_chart_opex.series.append(opex_wo_cont_supp)

                opex_after_sales = InstanciatedSeries(cashflow_product['years'].values.tolist(
                ), (cashflow_product['opex_after_sales'].values * cashflow_product['quantity'].values / factor).tolist(), 'OpEx after Sales', 'bar')

                new_chart_opex.series.append(opex_after_sales)

                instanciated_charts.append(new_chart_opex)

        if 'CAPEX' in graphs_list and cashflow_product is not None:
            if 'capex' in cashflow_product.columns:
                total_capex = cashflow_product['capex'].sum()
                if total_capex >= 1.0e9:
                    total_capex = total_capex / 1.0e9
                    legend_letter2 = 'bn'
                elif total_capex < 1.0e9 and total_capex >= 1.0e6:
                    total_capex = total_capex / 1.0e6
                    legend_letter2 = 'M'
                elif total_capex < 1.0e6 and total_capex >= 1.0e3:
                    total_capex = total_capex / 1.0e3
                    legend_letter2 = 'k'
                else:
                    legend_letter2 = ''

                chart_name = f'{self.sos_name} CapEx'
                new_chart_sales = TwoAxesInstanciatedChart('Years', f'CapEx ({legend_letter}€)',
                                                           [],
                                                           [],
                                                           chart_name, stacked_bar=True)

                new_chart_sales.annotation_upper_left = {
                    'Total CapEx': f'{round(total_capex,2)} {legend_letter2}€'}

                years_values = cashflow_product['years'].values.tolist()

                # if sales_by_subsystem:

                labels_dict = {
                    'contingency': 'Contingency',
                    'capex': 'CapEx'}
                for column in labels_dict:
                    if column in capex:
                        capex_values = np.array(capex[column].values) / factor
                        product_serie = InstanciatedSeries(
                            abscissa=years_values,
                            ordinate=capex_values.tolist(),
                            series_name=labels_dict.get(column, column),
                            display_type='bar',
                            visible=True,
                            y_axis=InstanciatedSeries.Y_AXIS_PRIMARY)

                        new_chart_sales.series.append(product_serie)

                instanciated_charts.append(new_chart_sales)

        return instanciated_charts
