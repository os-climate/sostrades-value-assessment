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

from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from sos_trades_core.tools.post_processing.plotly_native_charts.instantiated_plotly_native_chart import \
    InstantiatedPlotlyNativeChart
import plotly.graph_objects as go
from copy import deepcopy


def get_chart_filter_list(discipline):

    chart_filters = []

    chart_list = ['Operating Expenditure per product',
                  'Total Operating Expenditure']

    chart_filters.append(ChartFilter(
        'Charts', chart_list, chart_list, 'Charts'))

    opex_dict = discipline.get_sosdisc_outputs(
        'opex_dict')

    dict_keys = list(opex_dict.keys())
    if len(dict_keys) > 0:
        # calculate the number of gather levels
        levels = len(dict_keys[0].split('.'))

        for level in range(0, levels):
            # create a set containing all possible values for the current level
            level_keys = set()
            for key in dict_keys:
                key_level_list = key.split('.')
                try:
                    level_keys.add(key_level_list[level])
                except:
                    pass
            level_values_list = list(level_keys)
            group_name = f'Group{level+1}'

            chart_filters.append(ChartFilter(
                f'{group_name}', level_values_list, level_values_list, f'{group_name}'))

    return chart_filters


def get_instanciated_charts(discipline, filters=None):

    instanciated_charts = []
    graphs_list = []

    # Overload default value with chart filter
    if filters is not None:
        group_lists = []
        for chart_filter in filters:
            if chart_filter.filter_key == 'Charts':
                graphs_list = chart_filter.selected_values
            if chart_filter.filter_key[0:5] == 'Group':
                group_lists.append(chart_filter.selected_values)
    selected_group_combined = []
    for filter_list in group_lists:
        if len(selected_group_combined) == 0:
            selected_group_combined = filter_list
        else:
            selected_group_combined = [
                f'{gfc}.{fv}' for gfc in selected_group_combined for fv in filter_list]
    # clean combined values
    for v in selected_group_combined:
        if v[0:1] == '.':
            v = v[1:]
        if v[-1] == '.':
            v = v[0:-1]

    opex_unit_dict = discipline.get_sosdisc_outputs(
        'opex_dict')

    opex_total_dict = deepcopy(discipline.get_sosdisc_outputs(
        'opex_total_dict'))

    if 'Operating Expenditure per product' in graphs_list:

        # Create figure
        fig = go.Figure()

        for product in selected_group_combined:
            if product in opex_unit_dict:
                opex_unit = opex_unit_dict[product]

                years = opex_unit['years'].values
                opex_values = opex_unit['opex'].values
                after_sales_values = opex_unit['opex_after_sales'].values

                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=opex_values.tolist(),
                        visible=True,
                        name=f'OpEx {product}'
                    )
                )

                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=after_sales_values.tolist(),
                        visible=True,
                        name=f'After Sales {product}'
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
        chart_name = f'Operating Expenditure per product'
        new_chart = InstantiatedPlotlyNativeChart(
            fig=fig, chart_name=chart_name, default_legend=False, with_default_annotations=False)

        if new_chart:
            instanciated_charts.append(new_chart)

    if 'Total Operating Expenditure' in graphs_list:

        # Create figure
        fig = go.Figure()

        for product in selected_group_combined:
            if product in opex_total_dict:
                opex_total = opex_total_dict[product]

                years = opex_unit['years'].values
                opex_values = opex_total['opex'].values
                after_sales_values = opex_total['opex_after_sales'].values

                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=opex_values.tolist(),
                        visible=True,
                        name=f'Total OpEx {product}'
                    )
                )
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=after_sales_values.tolist(),
                        visible=True,
                        name=f'Total After Sales {product}'
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

    return instanciated_charts
