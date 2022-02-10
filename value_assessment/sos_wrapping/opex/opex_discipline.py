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


from sos_trades_core.execution_engine.sos_discipline import SoSDiscipline
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from sos_trades_core.tools.post_processing.plotly_native_charts.instantiated_plotly_native_chart import \
    InstantiatedPlotlyNativeChart
from sos_trades_core.tools.post_processing.post_processing_tools import format_currency_legend
from value_assessment.core.opex import Opex
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from copy import deepcopy


class OPEXDiscipline(SoSDiscipline):

    _maturity = 'Research'

    # otology metadata for the SoSDiscipline
    _metadata = {
        'label': 'Values Assessment OpEx Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': 'YES',
        'validated_by': 'SoSTrades',
        'last_modification_date': '20/01/2022',
        'category': 'Accounting',
        'definition': 'Model to calculate simple generic Opex with After Sales',
        'icon': 'fas fa-money-bill-alt fa-fw',
    }

    DESC_IN = {
        'launch_year': {
            'default': 2025,
            'type': 'int',
            'unit': 'year',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_data_product'
        },
        'escalation_opex_df': {
            'type': 'dataframe',
            'unit': '',
            'visibility':  SoSDiscipline.SHARED_VISIBILITY,
            'dataframe_descriptor': {
                'year_economical_conditions': ('int', None, True),
                'yearly_escalation_rate': ('float', [0.0, 100.0], True),
            },
            'dataframe_edition_locked': False,
            'namespace': 'ns_opex',
            'default': pd.DataFrame(
                {
                    'year_economical_conditions': [2010],
                    'yearly_escalation_rate': [0.]
                }),
        },
        'year_end': {
            'default': 2050,
            'type': 'int',
            'unit': 'year',
            'range': [1950, 2100],
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_public'
        },
        'year_start': {
            'default': 2020,
            'type': 'int',
            'unit': 'year',
            'range': [1950, 2100],
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_public'
        },
        'product_sales_df': {
            'type': 'dataframe',
            'unit': '#product/year',
            'visibility':  SoSDiscipline.SHARED_VISIBILITY,
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
        'opex_multiplier': {
            'type': 'float',
            'default': 100.0,
            'unit': '%',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_input_details',
            'user_level': 2
        },
        'opex_by_category': {
            'type': 'dataframe',
            'unit': '€',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_input_details',
            'default': pd.DataFrame(
                {
                    'components': ['component1'],
                    'opex': [100.0]
                }),
            'dataframe_descriptor': {
                'components': ('string', None, True),
                'opex': ('float', None, True)},
            'dataframe_edition_locked': False
        },
        'learning_curve_product_dict': {
            'default': {'percentage_make': 0., 'learning_curve_coefficient': [0.8], 'until_product_rank': [50.], },
            'type': 'dict',
            'unit': '',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_input_details',
            'dataframe_descriptor': {
                'variable':  ('string',  None, True),
                'value': ('float',  None, True),
            },
            'dataframe_edition_locked': False,
            'user_level': 2
        },
        'after_sales_opex_unit': {
            'default': {'launch_year': 8., 'launch_year+1': 7., 'launch_year+2': 6., 'launch_year+3': 5.5,
                        'launch_year+4': 5., 'launch_year+5': 5., 'launch_year+6': 5., 'launch_year+7': 5., 'launch_year+8': 5., 'launch_year+9': 5., 'launch_year+10 onwards': 5.},
            'type': 'dict',
            'unit': '%',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_input_details',
            'dataframe_descriptor': {
                'variable': ('string', None, False),
                'value': ('float', None, True)
            },
            'dataframe_edition_locked': False,
            'user_level': 2
        },
    }

    DESC_OUT = {
        'opex': {
            'type': 'dataframe',
            'unit': '€',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_results',
        },
        'opex_total': {
            'type': 'dataframe',
            'unit': '€',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_opex_results',
        },
    }

    def run(self):
        # -- retrieve input data
        inputs_dict = self.get_sosdisc_inputs()

        if 'year_economical_conditions' in inputs_dict['escalation_opex_df']:
            year_economical_conditions = int(
                inputs_dict['escalation_opex_df'].iloc[0]['year_economical_conditions'])
        else:
            year_economical_conditions = 2010.
            print(
                f'Column year_economical_conditions is not in dataframe escalation_opex_df')
        if 'yearly_escalation_rate' in inputs_dict['escalation_opex_df']:
            yearly_escalation_rate = inputs_dict['escalation_opex_df'].iloc[0]['yearly_escalation_rate'] / 100.
        else:
            yearly_escalation_rate = 0.
            print(
                f'Column yearly_escalation_rate is not in dataframe escalation_opex_df')

        learning_curve_product_dict = deepcopy(
            inputs_dict['learning_curve_product_dict'])
        if not isinstance(learning_curve_product_dict['learning_curve_coefficient'], list):
            learning_curve_product_dict['learning_curve_coefficient'] = [
                learning_curve_product_dict['learning_curve_coefficient']]
        if not isinstance(learning_curve_product_dict['until_product_rank'], list):
            learning_curve_product_dict['until_product_rank'] = [
                learning_curve_product_dict['until_product_rank']]

        self.opex_model = Opex(
            escalation_rate=yearly_escalation_rate,
            year_start_escalation_rate=year_economical_conditions,
            launch_year=inputs_dict['launch_year'],
            year_start=inputs_dict['year_start'],
            year_end=inputs_dict['year_end'],
            learning_curve_dict=learning_curve_product_dict
        )

        after_sales_opex_unit = np.array(
            list(inputs_dict['after_sales_opex_unit'].values())) / 100.0

        opex_df = self.opex_model.compute_opex_by_category(
            opex_by_category=inputs_dict['opex_by_category'],
            sales=inputs_dict['product_sales_df'],
            opex_multiplier=inputs_dict['opex_multiplier'] / 100.0,
            distrib_after_sales_opex_unit=after_sales_opex_unit)

        # opex for all products
        opex_total = opex_df.drop(columns=['learning_curve_coef'])

        list_col = list(opex_total.drop(
            columns=['years', 'quantity', 'cumulative_quantity']).columns)

        opex_total[list_col] = opex_total[list_col].multiply(
            opex_total["quantity"], axis="index")

        # -- Store computed data
        dict_values = {
            'opex': opex_df.drop(columns=['quantity', 'cumulative_quantity', 'learning_curve_coef']),
            'opex_total': opex_total,
        }
        self.store_sos_outputs_values(dict_values)

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = [
            'Operating Expenditure per product',
            'Operating Expenditure by Component',
            'Detailed Operating Expenditure',
            'Total Operating Expenditure',
            'Learning Curve effect',
        ]

        chart_filters.append(ChartFilter(
            'Charts', chart_list, chart_list, 'charts'))

        return chart_filters

    def get_post_processing_list(self, filters=None):

        # For the outputs, making a graph for tco vs year for each range and for specific
        # value of ToT with a shift of five year between then

        instanciated_charts = []

        # Overload default value with chart filter
        if filters is not None:
            for chart_filter in filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values

        name = self.sos_name
        opex_unit = self.get_sosdisc_outputs('opex')
        opex_total = self.get_sosdisc_outputs('opex_total')
        year_economical_conditions = int(
            self.get_sosdisc_inputs('escalation_opex_df').iloc[0]['year_economical_conditions'])
        opex_cat_EC = deepcopy(self.get_sosdisc_inputs('opex_by_category'))
        ratio_opex = self.get_sosdisc_inputs('opex_multiplier') / 100.0
        opex_cat_EC['opex'] = opex_cat_EC['opex'] * ratio_opex
        opex_EC = sum(opex_cat_EC['opex'])

        if 'Operating Expenditure per product' in chart_list:

            # Create figure
            fig = go.Figure()

            years = opex_unit['years'].values
            opex_values = opex_unit['opex'].values
            after_sales_values = opex_unit['opex_after_sales'].values

            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=opex_values.tolist(),
                    visible=True,
                    name='OpEx'
                )
            )

            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=after_sales_values.tolist(),
                    visible=True,
                    name='After Sales'
                )
            )

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                ),
                yaxis=dict(
                    title='Operating Expenditure',
                    ticksuffix='€',
                    automargin=True
                ),
                showlegend=True,
                barmode='stack',
                autosize=True,
            )

            annotation_upper_left = {
                'Year of EC ': year_economical_conditions,
                'OpEx in ' + str(year_economical_conditions): f'{format_currency_legend(round(opex_EC, 2), "€")}'
            }

            # Create native plotly chart
            chart_name = f'Operating Expenditure per product'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)
            new_chart.add_annotation(
                new_chart.ANNOTATION_UPPER_LEFT, 'Year of EC:', f'{year_economical_conditions}')
            new_chart.add_annotation(new_chart.ANNOTATION_UPPER_LEFT,
                                     f'OpEx in {year_economical_conditions}:', f'{format_currency_legend(round(opex_EC, 2), "€")}')

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Operating Expenditure by Component' in chart_list:

            # Create figure
            fig = go.Figure()

            # sort
            sorted_opex_by_category = opex_cat_EC.sort_values(
                by=['opex'], axis=0, ascending=False, inplace=False)
            str_total = f'Opex in {str(year_economical_conditions)}: {format_currency_legend(round(opex_EC, 2), "€")}'
            for component in sorted_opex_by_category['components']:
                opex_values = sorted_opex_by_category['opex'].loc[sorted_opex_by_category['components']
                                                                  == component]
                # category bar
                fig.add_trace(
                    go.Bar(
                        x=[name],
                        y=opex_values.values.tolist(),
                        name=f'{component}',
                        text=f'{component}',
                        textposition='inside',
                        xaxis='x',
                        yaxis='y',
                        visible=True
                    )
                )

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                    # type='multicategory'
                ),
                yaxis=dict(
                    title='Operating Expenditure',
                    ticksuffix='€',
                    titlefont=dict(
                        color="#1f77b4"
                    ),
                    tickfont=dict(
                        color="#1f77b4"
                    ),
                    automargin=True
                ),
                showlegend=False,
                barmode='stack',
                autosize=True,
                annotations=[dict(
                    x=0,
                    y=sum(sorted_opex_by_category['opex']),
                    text=str_total,
                    xanchor='auto',
                    yanchor='bottom',
                    showarrow=False,
                    font=dict(
                        family="Arial",
                        size=16,
                        color="#000000"
                    ),
                )],
                margin=dict(l=0, b=0)
            )

            # Create native plotly chart
            chart_name = f'Operating Expenditure by Component'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)
            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Detailed Operating Expenditure' in chart_list:

            # Create figure
            fig = go.Figure()

            years = opex_unit['years'].values
            opex_make_values = opex_unit['opex_Make'].values
            opex_buy_values = opex_unit['opex_Buy'].values
            after_sales_values = opex_unit['opex_after_sales'].values

            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=opex_make_values.tolist(),
                    visible=True,
                    name=f'Operating Expenditure Make',
                )
            )
            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=opex_buy_values.tolist(),
                    visible=True,
                    name=f'Operating Expenditure Buy',
                )
            )

            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=after_sales_values.tolist(),
                    visible=True,
                    name='After Sales'
                )
            )

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                ),
                yaxis=dict(
                    title='Operating Expenditure',
                    ticksuffix='€',
                    automargin=True
                ),
                showlegend=True,
                barmode='stack',
                autosize=True,
            )

            # Create native plotly chart
            chart_name = f'Operating Expenditure breakdown per product'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Total Operating Expenditure' in chart_list:

            # Create figure
            fig = go.Figure()

            years = opex_unit['years'].values
            opex_values = opex_total['opex'].values
            after_sales_values = opex_total['opex_after_sales'].values

            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=opex_values.tolist(),
                    visible=True,
                    name='Total OpEx'
                )
            )
            fig.add_trace(
                go.Bar(
                    x=years.tolist(),
                    y=after_sales_values.tolist(),
                    visible=True,
                    name='Total After Sales'
                )
            )

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                ),
                yaxis=dict(
                    title='Operating Expenditure',
                    ticksuffix='€',
                    automargin=True
                ),
                showlegend=True,
                barmode='stack',
                autosize=True,
            )

            # Create native plotly chart
            chart_name = f'Total Operating Expenditure (all products)'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Learning Curve effect' in chart_list:

            # Create figure
            fig = go.Figure()

            years = opex_unit['years'].values
            opex_make_values = opex_unit['opex_Make'].values
            opex_make_wo_lc_values = opex_unit['opex_Make_wo_LC'].values

            fig.add_trace(
                go.Scatter(
                    x=years.tolist(),
                    y=opex_make_values.tolist(),
                    visible=True,
                    name=f'OpEx Make',
                    mode='lines',
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=years.tolist(),
                    y=opex_make_wo_lc_values.tolist(),
                    visible=True,
                    name=f'OpEx Make without Learning Curve',
                    mode='lines',
                )
            )

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                ),
                yaxis=dict(
                    title='Operating Expenditure',
                    ticksuffix='€',
                    automargin=True
                ),
                showlegend=True,
                barmode='stack',
                autosize=True,
            )

            # Create native plotly chart
            chart_name = f'Learning Curve effect'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)

            if new_chart:
                instanciated_charts.append(new_chart)

        return instanciated_charts
