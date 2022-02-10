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

from sos_trades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, TwoAxesInstanciatedChart
from sos_trades_core.tools.post_processing.charts.chart_filter import ChartFilter
from sos_trades_core.tools.post_processing.plotly_native_charts.instantiated_plotly_native_chart import \
    InstantiatedPlotlyNativeChart
import plotly.graph_objects as go


def get_chart_filter_list(discipline):

    # For the outputs, making a graph for tco vs year for each range and for specific
    # value of ToT with a shift of five year between then

    chart_filters = []
    # chart_list = ['Non Recurring Cost']
    chart_list = ['CapEx', 'CapEx by family',
                  'CapEx by category']

    chart_filters.append(ChartFilter(
        'Graphs', chart_list, chart_list, 'Charts'))

    capex_dict = discipline.get_sosdisc_outputs('capex_dict')

    dict_keys = list(capex_dict.keys())
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

    # For the outputs, making a graph for tco vs year for each range and for specific
    # value of ToT with a shift of five year between then

    instanciated_charts = []

    # Overload default value with chart filter
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

    # Get desired Outputs
    capex_dict = discipline.get_sosdisc_outputs('capex_dict')

    # Get Order of magnitude
    min_value = 0.
    max_value = 0.
    max_program = [0.]
    for product in selected_group_combined:
        if product in capex_dict:

            capex_tmp = capex_dict[product]['capex'].values
            year_list = capex_dict[product]['years'].values
            max_program.append(capex_tmp.max())
    max_value = sum(max_program) * 1.05

    legend_letter, factor, max_value = get_order_of_magnitude(max_value)

    if 'CapEx' in graphs_list:

        chart_name = 'CapEx'

        new_chart = TwoAxesInstanciatedChart('Years', 'CapEx (' + legend_letter + ' €)',
                                             [],
                                             [],
                                             chart_name, stacked_bar=True)
        for product in selected_group_combined:
            if product in capex_dict:
                capex = capex_dict[product]['capex'].values / factor
                year_list = capex_dict[product]['years'].values
                serie = InstanciatedSeries(
                    year_list.tolist(),
                    capex.tolist(), f'{product} capex', 'bar')
                new_chart.series.append(serie)

                # new_chart.to_plotly().show()

        instanciated_charts.append(new_chart)

    if 'CapEx by family' in graphs_list:

        fig = go.Figure()
        if len(group_lists) > 0:
            for product in group_lists[0]:
                capex_product_df = None
                for key, capex_group_df in capex_dict.items():
                    if key in selected_group_combined:
                        if product in key:
                            if capex_product_df is None:
                                capex_product_df = capex_group_df.loc[:, [
                                    'years', 'capex']]
                            else:
                                capex_product_df['capex'] += capex_group_df['capex']
                if capex_product_df is not None:
                    years_values = capex_product_df['years'].astype(
                        int)
                    capex_values = capex_product_df['capex'].values / factor

                    fig.add_trace(
                        go.Bar(
                            x=years_values.tolist(),
                            y=capex_values.tolist(),
                            name=f'{product}',
                            xaxis='x',
                            yaxis='y',
                            visible=True
                        )
                    )
        fig.update_layout(
            xaxis=dict(
                title='Years',
                automargin=True,
                visible=True,
            ),
            yaxis=dict(
                title='CapEx',
                ticksuffix=f' {legend_letter}€',
                automargin=True
            ),
            showlegend=True,
            barmode='stack',
            autosize=True,
            # annotations=total_labels
        )
        # Create native plotly chart
        chart_name = 'CapEx by Family'
        new_chart = InstantiatedPlotlyNativeChart(
            fig=fig, chart_name=chart_name)
        # new_chart.to_plotly().show()
        if len(fig.data) > 0:
            instanciated_charts.append(new_chart)

    if 'CapEx by category' in graphs_list:

        fig = go.Figure()
        if len(capex_dict) > 0:
            ayd = capex_dict[list(capex_dict.keys())[0]]
            list_categories = [
                col for col in ayd.columns if col not in ['years', 'capex']]

            for category in list_categories:
                capex_cat_df = None
                for key, capex_group_df in capex_dict.items():
                    if key in selected_group_combined:
                        if category in capex_group_df:
                            if capex_cat_df is None:
                                capex_cat_df = capex_group_df.loc[:, [
                                    'years', category]]
                            else:
                                capex_cat_df[category] += capex_group_df[category]
                if capex_cat_df is not None:

                    years_values = capex_cat_df['years'].astype(
                        int)
                    capex_values = capex_cat_df[category].values / factor

                    fig.add_trace(
                        go.Bar(
                            x=years_values.tolist(),
                            y=capex_values.tolist(),
                            # name=f'{label}',
                            name=f'{category}',
                            xaxis='x',
                            yaxis='y',
                            visible=True
                        )
                    )

        # Chart Layout update
        fig.update_layout(
            xaxis=dict(
                title='Years',
                automargin=True,
                visible=True,
            ),
            yaxis=dict(
                title='CapEx',
                ticksuffix=f'{legend_letter}€',
                automargin=True
            ),
            showlegend=True,
            barmode='stack',
            autosize=True,
        )
        # Create native plotly chart
        chart_name = 'CapEx by Category'
        new_chart = InstantiatedPlotlyNativeChart(
            fig=fig, chart_name=chart_name)
        # new_chart.to_plotly().show()
        if len(fig.data) > 0:
            instanciated_charts.append(new_chart)

    return instanciated_charts


def get_order_of_magnitude(maxvalue):

    if maxvalue >= 1.0e9:
        maxvalue = maxvalue / 1.0e9
        legend_letter = 'B'
        factor = 1.0e9
    elif maxvalue < 1.0e9 and maxvalue >= 1.0e6:
        maxvalue = maxvalue / 1.0e6
        legend_letter = 'M'
        factor = 1.0e6
    elif maxvalue < 1.0e6 and maxvalue >= 1.0e3:
        maxvalue = maxvalue / 1.0e3
        legend_letter = 'k'
        factor = 1.0e3
    else:
        legend_letter = ''
        factor = 1.0

    return legend_letter, factor, maxvalue
