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

import plotly.graph_objects as go
from sos_trades_core.tools.post_processing.post_processing_tools import align_two_y_axes, format_currency_legend
from sos_trades_core.tools.post_processing.plotly_native_charts.instantiated_plotly_native_chart import \
    InstantiatedPlotlyNativeChart
import pandas as pd
from copy import deepcopy


class ValueAssessmentCharts(InstantiatedPlotlyNativeChart):

    """ Class to host standard ValueAssessment post post processing charts
    """

    def __init__(self):
        super().__init__(go.Figure())
        self.default_chart = InstantiatedPlotlyNativeChart(go.Figure())
        self.default_legend = self.default_chart.get_default_legend_layout()

    def generate_annotations(self, cashflow_info_dict, currency):
        annotation_upper_left = {}
        annotation_upper_right = {}

        npv = cashflow_info_dict.get('npv', 0)
        mpe = cashflow_info_dict.get('max_peak_exposure', 0)
        irr = cashflow_info_dict.get('irr', 0)
        if irr != 'NA':
            irr = round(cashflow_info_dict.get('irr', 0) * 100.0, 2)

        annotation_upper_left = {f'IRR from {cashflow_info_dict.get("year_min_irr","")} to {cashflow_info_dict.get("year_max_irr","")}': '{} %'.format(irr),
                                 'NPV': f'{format_currency_legend(round(npv, 2), currency)}'}

        annotation_upper_right = {
            'Year break even': cashflow_info_dict.get('year_break_even', ''),
            'Max Peak Exposure': f'{format_currency_legend(round(mpe, 2), currency)}'}
        return annotation_upper_left, annotation_upper_right

    def generate_cashflow_chart(self, cf_df, name, annotation_upper_left, annotation_upper_right, currency, add_cumulated=False):

        # Create figure
        fig = go.Figure()

        if 'years' in cf_df:

            # Free Cashflow
            if 'cash_flow' in cf_df:
                years = cf_df['years'].values
                free_cashflow = cf_df['cash_flow'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=free_cashflow.tolist(),
                        name=f'Free Cashflow',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                    )
                )

            if 'cumulative_discounted_cf' in cf_df and add_cumulated:
                # Cumulative Discounted CashFlow
                years = cf_df['years'].values
                cumul_discout_cashflow = cf_df['cumulative_discounted_cf'].values
                fig.add_trace(
                    go.Scatter(
                        x=years.tolist(),
                        y=cumul_discout_cashflow.tolist(),
                        name=f'Cumulative Discounted CashFlow',
                        xaxis='x',
                        yaxis='y2',
                        visible=True,
                        mode='lines',
                    )
                )

            if 'cumulative_cash_flow' in cf_df and add_cumulated:
                # Cumulative Free CashFlow
                years = cf_df['years'].values
                cumul_free_cashflow = cf_df['cumulative_cash_flow'].values
                fig.add_trace(
                    go.Scatter(
                        x=years.tolist(),
                        y=cumul_free_cashflow.tolist(),
                        name=f'Cumulative Free CashFlow',
                        xaxis='x',
                        yaxis='y2',
                        visible=True,
                        mode='lines',
                    )
                )
        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Cashflow',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,

            ),
            yaxis2=dict(
                title='Cumulative Cashflow',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,
                anchor="x",
                overlaying="y",
                side="right",
            ),
            legend=self.default_legend,
            barmode='group',
            # gap between bars of adjacent location coordinates.
            bargap=0.15,
            # gap between bars of the same location coordinate.
            bargroupgap=0.1
        )

        new_chart = None
        if len(fig.data):
            if add_cumulated:
                fig = align_two_y_axes(fig, GRIDLINES=4)

            # Create native plotly chart
            chart_name = f'Total Cashflows {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)
            new_chart.annotation_upper_left = annotation_upper_left
            new_chart.annotation_upper_right = annotation_upper_right

            if ('years' in cf_df) & ('cash_flow' in cf_df):
                new_chart.set_csv_data_from_dataframe(
                    cf_df[['years', 'cash_flow']])
        return new_chart

    def generate_cashin_cashout_chart(self, cf_df, name, annotation_upper_left, annotation_upper_right, currency, add_cumulated=False):

        # Create figure
        fig = go.Figure()

        if 'years' in cf_df:

            if 'cash_in' in cf_df:
                years = cf_df['years'].values
                cash_in = cf_df['cash_in'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=cash_in.tolist(),
                        name=f'Cash in',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                        offsetgroup='a',
                    )
                )
            if 'cash_out' in cf_df:
                years = cf_df['years'].values
                cash_out = cf_df['cash_out'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=cash_out.tolist(),
                        name=f'Cash out',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                        offsetgroup='a',
                    )
                )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Cash in / Cash out',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,

            ),
            legend=self.default_legend,
            barmode='group',
        )

        new_chart = None
        if len(fig.data):
            if add_cumulated:
                fig = align_two_y_axes(fig, GRIDLINES=4)

            # Create native plotly chart
            chart_name = f'Cash in / Cash out {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)

            if ('years' in cf_df) & ('cash_in' in cf_df) & ('cash_out' in cf_df):
                new_chart.set_csv_data_from_dataframe(
                    cf_df[['years', 'cash_in', 'cash_out']])
        return new_chart

    def generate_cumulated_cashflow_chart(self, cf_df_dict, name, annotation_upper_left, annotation_upper_right, currency):
        # Create figure
        fig = go.Figure()

        for key, cf_df in cf_df_dict.items():
            if 'years' in cf_df:

                if 'cumulative_discounted_cf' in cf_df:
                    # Cumulative Discounted CashFlow
                    years = cf_df['years'].values
                    cumul_discout_cashflow = cf_df['cumulative_discounted_cf'].values
                    fig.add_trace(
                        go.Scatter(
                            x=years.tolist(),
                            y=cumul_discout_cashflow.tolist(),
                            name=f'{key}',
                            xaxis='x',
                            yaxis='y',
                            visible=True,
                            mode='lines',
                        )
                    )

                if 'cumulative_cash_flow' in cf_df:
                    # Cumulative Free CashFlow
                    years = cf_df['years'].values
                    cumul_free_cashflow = cf_df['cumulative_cash_flow'].values
                    fig.add_trace(
                        go.Scatter(
                            x=years.tolist(),
                            y=cumul_free_cashflow.tolist(),
                            name=f'{key}',
                            xaxis='x',
                            yaxis='y',
                            visible=False,
                            mode='lines',
                        )
                    )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Cumulative Cashflow',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,
            ),
            legend=self.default_legend
        )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(
                            args=[{'visible': [True, False] * int(len(fig.data) / 2)},
                                  {'yaxis.title': f'Cumulative Discounted Cashflow'}],
                            label="Discounted Cashflow",
                            method="update"
                        ),
                        dict(
                            args=[{'visible': [False, True] * int(len(fig.data) / 2)},
                                  {'yaxis.title': f'Cumulative Free Cashflow'}],
                            label="Free Cashflow",
                            method="update"
                        ),
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
            ]
        )

        new_chart = None
        if len(fig.data):
            # Create native plotly chart
            chart_name = f'Cumulated Cashflows {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)
            new_chart.annotation_upper_left = annotation_upper_left
            new_chart.annotation_upper_right = annotation_upper_right

            # new_chart.set_csv_data_from_dataframe(cf_df_dict)
        return new_chart

    def generate_detailed_cashflow_chart(self, cf_df_dict, name, annotation_upper_left, annotation_upper_right, currency):
        # Create figure
        fig = go.Figure()

        for granularity, cf_df in cf_df_dict.items():
            # Free Cashflow
            if 'cash_flow' in cf_df and 'years' in cf_df:
                years = cf_df['years'].values
                free_cashflow = cf_df['cash_flow'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=free_cashflow.tolist(),
                        name=f'{granularity} Free Cashflow',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                    )
                )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Cashflow',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,

            ),
            legend=self.default_legend,
            barmode='stack',
            # gap between bars of adjacent location coordinates.
            bargap=0.15,
            # gap between bars of the same location coordinate.
            bargroupgap=0.1
        )

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(
                            args=['barmode', 'stack'],
                            label="Sum",
                            method="relayout"
                        ),
                        dict(
                            args=['barmode', 'group'],
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
            ]
        )

        new_chart = None
        if len(fig.data):

            # Create native plotly chart
            chart_name = f'Detailed Cashflows {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)

            export_data = pd.DataFrame()
            for granularity, cf_df in cf_df_dict.items():
                if ('years' in cf_df) & ('cash_flow' in cf_df):
                    g = pd.Series(granularity, range(len(cf_df)))
                    df_csv = pd.concat(
                        [g, cf_df[['years', 'cash_flow']]], axis=1)
                    df_csv.rename(columns={0: "scenario_id"})
                    export_data = export_data.append(
                        df_csv, ignore_index=True)
            new_chart.set_csv_data_from_dataframe(export_data)

        return new_chart

    def generate_pnl_chart(self, pnl_df, name, annotation_upper_left, annotation_upper_right, currency, add_cumulated=False):
        # Create figure
        fig = go.Figure()

        if 'years' in pnl_df:

            # Free Cashflow
            if 'EBIT' in pnl_df:
                years = pnl_df['years'].values
                EBIT = pnl_df['EBIT'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=EBIT.tolist(),
                        name=f'EBIT',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                    )
                )

            if 'cumulative_EBIT' in pnl_df and add_cumulated:
                # Cumulative Discounted CashFlow
                years = pnl_df['years'].values
                EBIT_cumul = pnl_df['cumulative_EBIT'].values
                fig.add_trace(
                    go.Scatter(
                        x=years.tolist(),
                        y=EBIT_cumul.tolist(),
                        name=f'Cumulative EBIT',
                        xaxis='x',
                        yaxis='y2',
                        visible=True,
                        mode='lines',
                    )
                )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='EBIT',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,

            ),
            yaxis2=dict(
                title='Cumulative EBIT',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,
                anchor="x",
                overlaying="y",
                side="right",
            ),
            legend=self.default_legend,
            barmode='group',
            # gap between bars of adjacent location coordinates.
            bargap=0.15,
            # gap between bars of the same location coordinate.
            bargroupgap=0.1
        )

        new_chart = None
        if len(fig.data):
            if add_cumulated:
                fig = align_two_y_axes(fig, GRIDLINES=4)

            # Create native plotly chart
            chart_name = f'Profit & Loss {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)
            new_chart.annotation_upper_left = annotation_upper_left
            new_chart.annotation_upper_right = annotation_upper_right

            if ('years' in pnl_df) & ('EBIT' in pnl_df) & ('cumulative_EBIT' in pnl_df):
                new_chart.set_csv_data_from_dataframe(
                    pnl_df[['years', 'EBIT', 'cumulative_EBIT']])
        return new_chart

    def generate_quantity_chart(self, cf_df, name, annotation_upper_left, annotation_upper_right, add_cumulated=False):
        # Create figure
        fig = go.Figure()

        if 'years' in cf_df:

            # Quantity
            if 'quantity' in cf_df:
                years = cf_df['years'].values
                quantity = cf_df['quantity'].values
                fig.add_trace(
                    go.Bar(
                        x=years.tolist(),
                        y=quantity.tolist(),
                        name=f'Product quantities',
                        xaxis='x',
                        yaxis='y',
                        visible=True,
                    )
                )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Product quantities',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True,

            ),
            legend=self.default_legend,
            barmode='group',
            # gap between bars of adjacent location coordinates.
            bargap=0.15,
            # gap between bars of the same location coordinate.
            bargroupgap=0.1
        )

        new_chart = None
        if len(fig.data):
            if add_cumulated:
                fig = align_two_y_axes(fig, GRIDLINES=4)

            # Create native plotly chart
            chart_name = f'Quantities of product sold {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)
            new_chart.annotation_upper_left = annotation_upper_left
            new_chart.annotation_upper_right = annotation_upper_right

            if ('years' in cf_df) & ('quantity' in cf_df):
                new_chart.set_csv_data_from_dataframe(
                    cf_df[['years', 'quantity']])
        return new_chart

    def generate_total_table(self, info_dict, name, currency, info_df=None, graph_data='Cashflow'):

        # hypothesis summary
        if info_df is None and info_dict is not None:
            info_df = pd.DataFrame.from_dict(
                data=info_dict, orient='index').reset_index()

        last_year = int(info_df['last_year'].values[0])
        year_start_escalation_opex = int(
            info_df['year_start_escalation_opex'].values[0])
        year_start_escalation_capex = int(
            info_df['year_start_escalation_capex'].values[0])

        total_hypothesis_df = deepcopy(info_df)

        del total_hypothesis_df['last_year']
        del total_hypothesis_df['year_start_escalation_opex']
        del total_hypothesis_df['year_start_escalation_capex']

        data_info = {}

        data_info_output = {
            'index': {'label': 'Name', 'format': None},
            'scenario_id': {'label': 'Scenario', 'format': None},
            'irr': {'label': 'Internal Rate of Return (IRR)', 'format': 'percent'},
            'year_min_irr': {'label': 'Year Min IRR', 'format': None},
            'year_max_irr': {'label': 'Year Max IRR', 'format': None},
            'npv': {'label': 'Net Present Value (NPV)', 'format': 'currency'},
            'year_break_even': {'label': 'Year Break Even', 'format': None},
            'max_peak_exposure': {'label': 'Maximum Peak Exposure', 'format': 'currency'},
            'total_free_cash_flow': {'label': 'Total Free Cashflow', 'format': 'currency'},
        }

        data_info_input = {
            'product_list': {'label': 'Product List', 'format': None},
            'total_cumul_sales': {'label': 'Total Cumulative Sales', 'format': None},
            'total_cumul_capex': {'label': f'Total Cumulative CapEx <br> (ec {year_start_escalation_capex}) ', 'format': 'currency'},
            'total_cumul_opex': {'label': f'Total Cumulative OpEx <br> (ec {year_start_escalation_opex})', 'format': 'currency'},
            'opex_last_year': {'label': f'OpEx in {last_year}', 'format': 'currency'},
            'capex_last_year': {'label': f'CapEx in {last_year}', 'format': 'currency'},
            'sale_price_last_year': {'label': f'Sale Price in {last_year}', 'format': 'currency'},
            'contribution_margin_last_year': {'label': f'Contribution Margin in {last_year}', 'format': 'percent'},
        }

        data_info.update(data_info_input)
        data_info.update(data_info_output)

        # Create figure
        fig = go.Figure()

        if 'index' in total_hypothesis_df:
            total_hypothesis_df['index'] = total_hypothesis_df['index'].replace(
                regex=r'\.', value=' ')
            if len(total_hypothesis_df.loc[total_hypothesis_df['index'] == 'Total', 'index'].values) > 0:
                total_hypothesis_df.loc[total_hypothesis_df['index'] == 'Total', 'index'] = '<br>' + \
                    total_hypothesis_df.loc[total_hypothesis_df['index']
                                            == 'Total', 'index'] + '</br>'

        columns_names = []
        columns_data = []
        if 'scenario_id' in total_hypothesis_df.keys():
            total_hypothesis_df_t = total_hypothesis_df.set_index(
                'scenario_id').transpose()
        else:
            total_hypothesis_df_t = total_hypothesis_df.set_index(
                'index').transpose()

        # table colors
        fill_color = []
        color = []
        for i in range(len(total_hypothesis_df_t.index)):
            if total_hypothesis_df_t.index[i] in data_info_output:
                color.append('lavender')
            else:
                color.append('floralwhite')

        for (key, data) in total_hypothesis_df_t.iteritems():
            columns_names.append(f'<b>{key}</b>')
            rows_name = []
            col_data = []
            for val in data.index:
                rows_name.append(
                    f'<b>{data_info[val].get("label", val)}</b>')
                data_series = pd.Series(data=data[val])
                if data_info[val].get('format', None) == 'currency':
                    col_data.append(data_series.apply(
                        format_currency_legend, args=(currency)).values[0])
                elif data_info[val].get('format', None) == 'percent':
                    col_data.append(data_series.apply(lambda x: "{0:.2f}%".format(
                        x * 100) if not isinstance(x, str) else x).values[0])
                else:
                    col_data.append(data_series.values[0])
            columns_data.append(col_data)
            fill_color.append(color)

        columns_names.insert(0, [])
        columns_data.insert(0, rows_name)

        fig.add_trace(
            go.Table(
                header=dict(
                    values=columns_names,
                    fill_color='midnightblue',
                    align='center',
                    font_color='white'),
                cells=dict(
                    values=columns_data,
                    fill_color=fill_color,
                    align='center',
                )
            )
        )

        chart_name = f'{name} ' + graph_data + ' Summary'
        number_of_rows = len(columns_data[0])
        fig.update_layout(
            title_text=chart_name,
            # plot_bgcolor='rgba(228, 222, 249, 0.65)',
            showlegend=False,
            autosize=True,
            height=number_of_rows * 30 + 250,
        )

        if len(fig.data):

            # Create native plotly chart
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False, default_font=True, with_default_annotations=False)

            if total_hypothesis_df_t is not None:
                new_chart.set_csv_data_from_dataframe(total_hypothesis_df_t)

        return new_chart
    # new_chart.to_plotly().show()

    def generate_pnl_waterfall_chart(self, pnl_df_dict, name, currency):
        # Create figure
        fig = go.Figure()

        key_list = list(pnl_df_dict.keys())

        if len(key_list):
            if 'years' in pnl_df_dict[key_list[0]]:
                year_list = list(pnl_df_dict[key_list[0]]['years'].unique())

                for year_current in year_list:
                    revenues_list = []
                    costs_list = []
                    measure_list = []
                    measure_revenues_list = []
                    measure_costs_list = []
                    x_list = []
                    x_revenues_list = []
                    x_costs_list = []
                    for key in key_list:
                        lisible_key = key.replace('.', ' ')
                        yearly_cashflow = pnl_df_dict[key]
                        if all(['cash_in_PnL' in yearly_cashflow, 'cash_out_PnL' in yearly_cashflow]):
                            revenues_list.append(yearly_cashflow.loc[(
                                yearly_cashflow['years'] == year_current)]['cash_in_PnL'].sum())
                            measure_revenues_list.append('relative')
                            x_revenues_list.append(f'Revenues {lisible_key}')

                            costs_list.append(yearly_cashflow.loc[(
                                yearly_cashflow['years'] == year_current)]['cash_out_PnL'].sum())
                            measure_costs_list.append('relative')
                            x_costs_list.append(f'Direct Costs {lisible_key}')

                    y_values = [*revenues_list, 0, *costs_list, 0]
                    if sum(revenues_list) > 0:
                        margin = round(
                            (sum(revenues_list) + sum(costs_list)) / sum(revenues_list) * 100)
                    else:
                        margin = 'N/A'
                    y_text = [
                        *[format_currency_legend(v, currency)
                            for v in revenues_list],
                        f'{format_currency_legend(sum(revenues_list), currency)}',
                        *[format_currency_legend(v, currency)
                            for v in costs_list],
                        f'{format_currency_legend(sum(y_values), currency)} ({margin}%)',
                    ]
                    measure_list = [*measure_revenues_list,
                                    'total', *measure_costs_list, 'total']
                    x_list = [*x_revenues_list, 'Total Revenues',
                              *x_costs_list, 'Profit Margin']

                    waterfall = go.Waterfall(
                        name=f'<b>Profit and loss {name} Year {year_current}</b>',
                        orientation='h',
                        measure=measure_list,
                        x=y_values,
                        textposition='auto',
                        text=y_text,
                        y=x_list,
                        connector={"mode": "between", "line": {
                            "width": 2, "color": "rgb(0, 0, 0)", "dash": "solid"}},
                        visible=False
                    )
                    fig.add_trace(waterfall)
                if len(fig.data):
                    fig.data[-1].visible = True

                    # Create and add slider
                    steps = []
                    for i in range(len(fig.data)):
                        step = dict(
                            method='update',
                            args=[{'visible': [False] * len(fig.data)},
                                  {'title': f'Profit and loss {name} Year {year_list[i]}'}],  # layout attribute
                            label=f'{year_list[i]}'
                        )
                        # Toggle i'th trace to 'visible'
                        step['args'][0]['visible'][i] = True
                        steps.append(step)

                    sliders = [dict(
                        active=len(steps) - 1,
                        currentvalue={'prefix': 'Select Year, currently: '},
                        steps=steps
                    )]

                    fig.update_layout(
                        sliders=sliders,
                        xaxis=dict(
                            ticksuffix=currency,
                            automargin=True
                        ),
                        yaxis=dict(
                            automargin=True
                        ),
                        showlegend=False,
                        autosize=True,
                    )

        new_chart = None
        if len(fig.data):

            # Create native plotly chart
            chart_name = f'Profit & Loss {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)

            export_data = pd.DataFrame()
            for granularity, pnl_df in pnl_df_dict.items():
                if ('years' in pnl_df) & ('cash_in_PnL' in pnl_df) & ('cash_out_PnL' in pnl_df):
                    g = pd.Series(granularity, range(len(pnl_df)))
                    df_csv = pd.concat(
                        [g, pnl_df[['years', 'cash_in_PnL', 'cash_out_PnL']]], axis=1)
                    df_csv.rename(columns={0: "scenario_id"})
                    export_data = export_data.append(
                        df_csv, ignore_index=True)

            new_chart.set_csv_data_from_dataframe(export_data)
        return new_chart

    def generate_price_and_cost_chart(self, cf_df, name, currency, cf_df_dict=None):
        # Create figure
        fig = go.Figure()

        if all(['years' in cf_df, 'sale_price' in cf_df, 'opex' in cf_df]):

            # Price
            years = cf_df['years'].values
            price = cf_df['sale_price'].values
            fig.add_trace(
                go.Scatter(
                    x=years.tolist(),
                    y=price.tolist(),
                    name=f'Price',
                    xaxis='x',
                    yaxis='y',
                    visible=True,
                    mode='lines'
                )
            )

            # Cost
            years = cf_df['years'].values
            opex = cf_df['opex'].values
            fig.add_trace(
                go.Scatter(
                    x=years.tolist(),
                    y=opex.tolist(),
                    name=f'OpEx',
                    xaxis='x',
                    yaxis='y',
                    visible=True,
                    line=dict(dash='dash'),
                    mode='lines'
                )
            )

        fig.update_layout(
            autosize=True,
            xaxis=dict(
                title='Years',
                titlefont_size=12,
                tickfont_size=10,
                automargin=True
            ),
            yaxis=dict(
                title='Amount',
                titlefont_size=12,
                tickfont_size=10,
                ticksuffix=f'{currency}',
                automargin=True,

            ),
            legend=self.default_legend,
        )

        if cf_df_dict is not None:
            for key, cf_df in cf_df_dict.items():
                if all(['years' in cf_df, 'sale_price' in cf_df, 'opex' in cf_df]):

                    # Price
                    years = cf_df['years'].values
                    price = cf_df['sale_price'].values
                    fig.add_trace(
                        go.Scatter(
                            x=years.tolist(),
                            y=price.tolist(),
                            name=f'Price {key}',
                            xaxis='x',
                            yaxis='y',
                            visible=False,
                            mode='lines'
                        )
                    )

                    # Cost
                    years = cf_df['years'].values
                    opex = cf_df['opex'].values
                    fig.add_trace(
                        go.Scatter(
                            x=years.tolist(),
                            y=opex.tolist(),
                            name=f'OpEx {key}',
                            xaxis='x',
                            yaxis='y',
                            visible=False,
                            line=dict(dash='dash'),
                            mode='lines'
                        )
                    )

            fig.update_layout(
                updatemenus=[
                    dict(
                        buttons=list([
                            dict(
                                args=[{'visible': [True, True] +
                                       [False] * 2 * len(cf_df_dict)}],
                                label="Sum",
                                method="update"
                            ),
                            dict(
                                args=[{'visible': [False, False] +
                                       [True] * 2 * len(cf_df_dict)}],
                                label="Compare",
                                method="update"
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
                ]
            )

        new_chart = None
        if len(fig.data):

            # Create native plotly chart
            chart_name = f'{name} Price and OpEx'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)
            new_chart.annotation_upper_left = {}
            new_chart.annotation_upper_right = {}

            if ('years' in cf_df) & ('sale_price' in cf_df) & ('opex' in cf_df):
                new_chart.set_csv_data_from_dataframe(
                    cf_df[['years', 'sale_price', 'opex']])
        return new_chart

    def generate_value_assessment_chart(self, total_cashflow_dict, name, currency, scenario_list=[]):
        # Create figure
        fig = go.Figure()

        if len(scenario_list) == 0:
            scenario_list = [f'{name}']

        abs_value = scenario_list

        dic = {}
        for j in range(len(scenario_list)):
            tot = sum(list(total_cashflow_dict.values())[
                i][j] for i in range(len(total_cashflow_dict)))
            if 'Total' in total_cashflow_dict.keys():
                tot = total_cashflow_dict['Total'][j]
            dic[scenario_list[j]] = tot

        if 'Total' in total_cashflow_dict.keys():
            total_cashflow_dict.pop('Total')

        for key, fcf in total_cashflow_dict.items():
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
        if len(total_cashflow_dict) > 0:
            # Create annotations
            count = 0
            for scen, total in dic.items():
                annotation = dict(
                    x=count,
                    yref="y",
                    y=total,
                    text=format_currency_legend(total, '€'),
                    xanchor='auto',
                    yanchor='bottom',
                    showarrow=False,
                    font=dict(
                        family="Arial",
                        size=max(min(16, 100 / len(scenario_list)), 6),
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
                title='Total Free Cashflow',
                ticksuffix='€',
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
            # barmode='relative',
            autosize=True,
            annotations=annotations,
            margin=dict(l=0.25, b=0.25)
        )

        new_chart = None
        if len(fig.data):
            # Create native plotly chart
            chart_name = f'Value Assessment {name}'
            new_chart = InstantiatedPlotlyNativeChart(
                fig=fig, chart_name=chart_name, default_legend=False)

            export_data = pd.DataFrame(
                total_cashflow_dict)
            export_data['scenario_id'] = scenario_list
            new_chart.set_csv_data_from_dataframe(
                export_data)

        return new_chart
