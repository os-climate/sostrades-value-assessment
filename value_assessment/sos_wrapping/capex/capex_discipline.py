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


from sos_trades_core.api import get_sos_logger
from sos_trades_core.execution_engine.sos_discipline import SoSDiscipline
from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, TwoAxesInstanciatedChart
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from sos_trades_core.tools.post_processing.plotly_native_charts.instantiated_plotly_native_chart import \
    InstantiatedPlotlyNativeChart
from sos_trades_core.tools.post_processing.post_processing_tools import format_currency_legend
from value_assessment.core.capex import Capex
import pandas as pd
import numpy as np
import plotly.graph_objects as go


class CAPEXDiscipline(SoSDiscipline):

    # ontology information
    _ontology_data = {
        'label': 'Value Assessment CapEx Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fas fa-money-bill-alt fa-fw',
        'version': '',
    }

    _maturity = 'Research'

    DESC_IN = {
        'launch_year': {
            'default': 2025,
            'type': 'int',
            'unit': 'year',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_data_product'
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

        'escalation_capex_df': {
            'type': 'dataframe',
            'unit': '',
            'visibility':  SoSDiscipline.SHARED_VISIBILITY,
            'dataframe_descriptor': {
                'year_economical_conditions': ('int', None, True),
                'yearly_escalation_rate': ('float', [0.0, 100.0], True),
            },
            'dataframe_edition_locked': False,
            'namespace': 'ns_capex',
            'default': pd.DataFrame(
                {
                    'year_economical_conditions': [2010],
                    'yearly_escalation_rate': [0.]
                }),
        },

        'capex_multiplier': {
            'type': 'float',
            'default': 100.0,
            'unit': '%',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_capex_input_details',
            'user_level': 2,
        },

        'capex_distrib_categories': {
            'default': pd.DataFrame({
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
            }),
            'type': 'dataframe',
            'unit': '%',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'dataframe_descriptor': {
                'Distribution Category': ('string', None, True),
                'launch_year-6': ('float', [0, 100], True),
                'launch_year-5': ('float', [0, 100], True),
                'launch_year-4': ('float', [0, 100], True),
                'launch_year-3': ('float', [0, 100], True),
                'launch_year-2': ('float', [0, 100], True),
                'launch_year-1': ('float', [0, 100], True),
                'launch_year': ('float', [0, 100], True),
                'launch_year+1': ('float', [0, 100], True),
                'launch_year+2': ('float', [0, 100], True),
                'launch_year+3': ('float', [0, 100], True),
                'launch_year+4 onwards': ('float', [0, 100], True),
            },
            'dataframe_edition_locked': False,
            'namespace': 'ns_capex_input_details'
        },

        'capex_input_values': {
            'type': 'dataframe',
            'unit': '€',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'default': pd.DataFrame(
                {'Distribution Category': ['development1', 'development2'],
                    'Capex Component': ['component1', 'component2'],
                    'Capex value': [100.0, 50.],
                    'Contingency (%)': [15.0, 0.],
                 }),
            'dataframe_descriptor': {
                'Distribution Category': ('string', None, True),
                'Capex Component': ('string', None, True),
                'Capex value': ('float', None, True),
                'Contingency (%)': ('float', [0, 100], True)},
            'dataframe_edition_locked': False,
            'namespace': 'ns_capex_input_details'
        },

    }

    DESC_OUT = {
        'capex': {
            'type': 'dataframe',
            'unit': '€',
            'visibility': SoSDiscipline.SHARED_VISIBILITY,
            'namespace': 'ns_capex_results'
        }
    }

    def run(self):
        # -- retrieve input data
        inputs_dict = self.get_sosdisc_inputs()

        if 'year_economical_conditions' in inputs_dict['escalation_capex_df']:
            year_economical_conditions = int(
                inputs_dict['escalation_capex_df'].iloc[0]['year_economical_conditions'])
        else:
            year_economical_conditions = 2010.
            print(
                f'Column year_economical_conditions is not in dataframe escalation_capex_df')
        if 'yearly_escalation_rate' in inputs_dict['escalation_capex_df']:
            yearly_escalation_rate = inputs_dict['escalation_capex_df'].iloc[0]['yearly_escalation_rate'] / 100.
        else:
            yearly_escalation_rate = 0.
            print(
                f'Column yearly_escalation_rate is not in dataframe escalation_capex_df')

        self.logger = get_sos_logger(f'{self.ee.logger.name}.capex')

        self.capex_model = Capex(
            escalation_rate=yearly_escalation_rate,
            year_start_escalation_rate=year_economical_conditions,
            launch_year=inputs_dict['launch_year'],
            year_start=inputs_dict['year_start'],
            year_end=inputs_dict['year_end'],
            logger=self.logger
        )

        capex_input_values_modified = self.capex_model.apply_ratio(
            inputs_dict['capex_input_values'], inputs_dict['capex_multiplier'])

        capex_df = self.capex_model.compute_capex_by_category(
            capex_input_values=capex_input_values_modified,
            capex_distrib_categories=inputs_dict['capex_distrib_categories']
        )

        # -- Store computed data
        dict_values = {
            'capex': capex_df
        }

        self.store_sos_outputs_values(dict_values)

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = [
            'CapEx',
            'CapEx Breakdown',
            'Cumulated CapEx Breakdown',
            'Total Cumulated CapEx Breakdown',
            'CapEx by Category'
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

        capex_input_values = self.get_sosdisc_inputs('capex_input_values')
        capex = self.get_sosdisc_outputs('capex')
        total_capex = capex['capex'].sum()

        if 'CapEx' in chart_list:

            chart_name = 'CapEx per year'

            product_serie = InstanciatedSeries(
                capex['years'].values.tolist(),
                capex['capex'].values.tolist(), 'capex', 'bar')

            capex_cumul_values = capex['capex'].cumsum(
            ).values
            cumulative_serie = InstanciatedSeries(
                capex['years'].values.tolist(),
                capex_cumul_values.tolist(
                ), f'Cumulative capex', 'lines',
                y_axis=InstanciatedSeries.Y_AXIS_SECONDARY)

            new_chart = TwoAxesInstanciatedChart(abscissa_axis_name='Years',
                                                 primary_ordinate_axis_name=f'CapEx (€)',
                                                 abscissa_axis_range=[],
                                                 primary_ordinate_axis_range=[],
                                                 chart_name=chart_name,
                                                 stacked_bar=False,
                                                 bar_orientation='v',
                                                 cumulative_surface=False,
                                                 secondary_ordinate_axis_name=f'Cumulative Values (€)',
                                                 secondary_ordinate_axis_range=[capex_cumul_values.min() * 0.95, capex_cumul_values.max() * 1.05])
            new_chart.series.append(product_serie)
            new_chart.series.append(cumulative_serie)

            new_chart.annotation_upper_left = {
                'Total CapEx ': f'{format_currency_legend(round(total_capex, 2), "€")}',
            }

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'CapEx Breakdown' in chart_list:

            chart_name = 'CapEx breakdown per year '
            new_chart = TwoAxesInstanciatedChart('Years', f'CapEx (€)',
                                                 [],
                                                 [],
                                                 chart_name, stacked_bar=True)

            new_chart.annotation_upper_left = {
                'Total CapEx': f'{format_currency_legend(round(total_capex, 2), "€")}',
            }

            for column in capex.columns:
                if column not in ['years', 'capex']:
                    capex_values = np.array(
                        capex[column].values)
                    product_serie = InstanciatedSeries(
                        abscissa=capex['years'].values.tolist(
                        ),
                        ordinate=capex_values.tolist(),
                        series_name=column,
                        display_type='bar',
                        visible=True,
                        y_axis=InstanciatedSeries.Y_AXIS_PRIMARY)

                    new_chart.series.append(product_serie)

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Cumulated CapEx Breakdown' in chart_list:

            chart_name = 'Cumulative CapEx breakdown per year '
            new_chart = TwoAxesInstanciatedChart('Years', f'Cumulative CapEx Values (€)',
                                                 [],
                                                 [],
                                                 chart_name, stacked_bar=True)

            new_chart.annotation_upper_left = {
                'Total CapEx': f'{format_currency_legend(round(total_capex, 2), "€")}',
            }

            for column in capex.columns:
                if column not in ['years', 'capex']:
                    cumulative_serie = InstanciatedSeries(
                        abscissa=capex['years'].values.tolist(
                        ),
                        ordinate=capex[column].cumsum(
                        ).values.tolist(),
                        series_name=f'Cumulative {column}',
                        display_type='lines',
                        visible=True,
                        y_axis=InstanciatedSeries.Y_AXIS_PRIMARY)

                    new_chart.series.append(cumulative_serie)

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'Total Cumulated CapEx Breakdown' in chart_list:
            fig = go.Figure()

            product_list = ['Product']
            abs_value = product_list

            df_dic = {}
            for column in capex.columns:
                if column not in ['years', 'capex']:
                    df_dic[f'{column}'] = [
                        capex[column].cumsum().values[-1]]

            dic = {}
            for j in range(len(product_list)):
                tot = sum(list(df_dic.values())[
                    i][j] for i in range(len(df_dic)))
                dic[product_list[j]] = tot

            for key, fcf in df_dic.items():
                # category bar
                fig.add_trace(
                    go.Bar(
                        x=abs_value,
                        y=fcf,
                        name=f'{key}',
                        text=f'{key}',
                        textposition='inside',
                        xaxis='x',
                        yaxis='y',
                        visible=True
                    )
                )

            annotations = []
            if len(df_dic) > 0:
                # Create annotations
                count = 0
                for scen, total in dic.items():
                    annotation = dict(
                        x=count,
                        yref="y",
                        y=total,
                        text=f'{format_currency_legend(total, "€")}',
                        xanchor='auto',
                        yanchor='bottom',
                        showarrow=False,
                        font=dict(
                            family="Arial",
                            size=max(min(16, 100 / len(product_list)), 6),
                            color="#000000"
                        ),
                    )
                    annotations.append(annotation)
                    count += 1

            # Chart Layout update
            fig.update_layout(
                xaxis=dict(
                    automargin=True,
                    visible=True,
                    # type='multicategory'
                ),
                yaxis=dict(
                    title='Total CapEx (€)',
                    # ticksuffix='',
                    titlefont=dict(
                        color="#1f77b4"
                    ),
                    tickfont=dict(
                        color="#1f77b4"
                    ),
                    automargin=True
                ),
                updatemenus=[
                    dict(
                        buttons=list([
                            dict(
                                args=[{
                                    'annotations': annotations, 'barmode': 'stack'}],
                                label="Sum",
                                method="relayout"
                            ),
                            dict(
                                args=[{'annotations': [], 'barmode': 'group'}],
                                label="Compare",
                                method="relayout"
                            )
                        ]),
                        direction='down',
                        type='dropdown',
                        pad={"r": 0, "t": 0},
                        showactive=True,
                        active=0,
                        x=1.0,
                        y=1.01,
                        yanchor='bottom',
                        xanchor='right'
                    ),
                ],
                showlegend=False,
                barmode='stack',
                autosize=True,
                annotations=annotations,
                margin=dict(l=0.25, b=0.25)
            )

            new_chart = None
            last_year = capex['years'].values[-1]
            if len(fig.data):
                # Create native plotly chart
                chart_name = f'Total Cumulative CapEx Breakdown (escalated) in {last_year}'
                new_chart = InstantiatedPlotlyNativeChart(
                    fig=fig, chart_name=chart_name, default_legend=False)

            if new_chart:
                instanciated_charts.append(new_chart)

        if 'CapEx by Category' in chart_list:

            # Create figure
            fig = go.Figure()

            unique_categories_list = capex_input_values['Distribution Category'].unique(
            ).tolist()
            unique_categories_list_rename = [
                val + ' Category' for val in unique_categories_list]
            component_list = capex_input_values['Capex Component'].values.tolist(
            )
            parent_cat_list = capex_input_values['Distribution Category'].values.tolist(
            )
            parent_cat_list_rename = [
                val + ' Category' for val in parent_cat_list]

            sunburst_labels = [total_capex, *
                               unique_categories_list_rename, *component_list]
            sunburst_parents = ['',
                                *(len(unique_categories_list_rename) * [total_capex]), *parent_cat_list_rename]
            categories_values = [capex_input_values.loc[capex_input_values['Distribution Category'] == cat, 'Capex value'].sum(
            ) for cat in unique_categories_list]
            component_values = capex_input_values['Capex value'].values.tolist(
            )

            sunburst_values = [capex_input_values['Capex value'].sum(), *
                               categories_values, *component_values]
            sunburst_text = [
                f'{format_currency_legend(round(val, 2), "€")}' for val in sunburst_values]

            # category bar
            fig.add_trace(
                go.Sunburst(
                    labels=sunburst_labels,
                    parents=sunburst_parents,
                    values=sunburst_values,
                    text=sunburst_text,
                    hovertext=sunburst_text,
                    branchvalues="total",
                    textinfo='label+text',
                    hoverinfo='label+text+percent parent'
                )
            )

            # Chart Layout update
            fig.update_layout(
                autosize=True,
                margin=dict(t=60, l=0, r=0, b=0)
            )

            # Create native plotly chart
            chart_name = 'CapEx by Category'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name)

        if new_chart:
            instanciated_charts.append(new_chart)

        return instanciated_charts
