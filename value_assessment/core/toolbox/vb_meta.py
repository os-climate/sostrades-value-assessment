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

import numpy as np
import pandas as pd
from copy import deepcopy
from value_assessment.core.toolbox.IRR import IRR


class ValueBlock(object):
    '''
    classdocs
    '''

    def __init__(self, year_start, year_end, actor_name, actor_wacc, exchange_rate_USD_EUR):
        '''
        Constructor
        '''
        self.actor_name = actor_name

        self.year_start = year_start
        self.year_end = year_end
        self.actor_wacc = actor_wacc
        self.exchange_rate_USD_EUR = exchange_rate_USD_EUR
        self.cf_df = None
        self.cf_infos = None
        self.quarterly_rate = None
        self.init_dataframe()

    def init_dataframe(self):
        self.cf_df = pd.DataFrame(
            {'years': np.arange(self.year_start, self.year_end + 1)})
        self.init_additional_column()

    def configure_actor_wacc(self, wacc):
        self.actor_wacc = wacc

    def init_additional_column(self):
        pass

    def compute_cashflow(self):
        """
        Method to compute cashflow for the value block 
        """
        self._compute_costs()
        self._compute_revenues()

        self.cf_df['cash_flow'] = self.cf_df['cash_in'] + \
            self.cf_df['cash_out']

        self.cf_df['cumulative_cash_flow'] = self.cf_df['cash_flow'].cumsum()
        years = self.cf_df['years'].astype(int)
        year_range = pd.Series(
            range(int(years.values[-1]) - int(years.values[0]) + 1))
        self.cf_df['discounted_cf'] = self.cf_df['cash_flow'] * \
            (1 / (1 + self.actor_wacc))**year_range
        self.cf_df['cumulative_discounted_cf'] = self.cf_df['discounted_cf'].cumsum()

        self.compute_cf_df_info()

    def compute_cashflow_quarter(self):
        """
        Method to compute cashflow for the value block by quarter
        """
        # compute quarterly rate using the actor_wacc
        self.quarterly_rate = (1 + self.actor_wacc)**(1 / 4) - 1

        self._compute_costs()
        self._compute_revenues()

        self.cf_df['cash_flow'] = self.cf_df['cash_in'] + \
            self.cf_df['cash_out']

        self.cf_df['cumulative_cash_flow'] = self.cf_df['cash_flow'].cumsum()
        # years = self.cf_df['years'].astype(int)
        year_size = len(list(self.cf_df['years']))
        year_range = pd.Series(range(year_size))

        self.cf_df['discounted_cf'] = self.cf_df['cash_flow'] * \
            (1 / (1 + self.quarterly_rate))**year_range
        self.cf_df['cumulative_discounted_cf'] = self.cf_df['discounted_cf'].cumsum()

        self.compute_cf_df_info()

    def compute_PnL(self):
        """
        Method to compute PnL for the value block 
        """
        self._compute_costs()
        self._compute_revenues()

        self.cf_df['EBIT'] = self.cf_df['cash_in_PnL'] + \
            self.cf_df['cash_out_PnL']

        self.cf_df['cumulative_EBIT'] = self.cf_df['EBIT'].cumsum()

    def compute_cf_df_info(self):
        # define it at value block level
        cf_df = self.cf_df

        cf_info = {}
        # IRR on all years
        irr_ob = IRR(cf_df['cash_flow'])
        cf_info['irr'] = irr_ob.compute_irr()
        # cf_info['year_min_irr'] = cf_df['years'].values[0]
        # cf_info['year_max_irr'] = cf_df['years'].values[-1]

        if cf_info['irr'] is np.nan:
            # if irr is nan return -99999
            cf_info['irr'] = -99999.

        cf_info['npv'] = cf_df['cumulative_discounted_cf'].values[-1]

        if cf_df['years'][cf_df['cumulative_discounted_cf'] > 0].empty:
            cf_info['year_break_even_discounted_cashflow'] = 'NA'
        else:
            cf_info['year_break_even_discounted_cashflow'] = int(
                min(cf_df['years'][cf_df['cumulative_discounted_cf'] > 0])
            )
        if cf_df['years'][cf_df['cumulative_cash_flow'] > 0].empty:
            cf_info['year_break_even_cashflow'] = 'NA'
        else:
            cf_info['year_break_even_cashflow'] = int(
                min(cf_df['years'][cf_df['cumulative_cash_flow'] > 0])
            )

        # cf_info['max_peak_exposure'] = min(cf_df['cumulative_cash_flow'])
        cf_info['peak_exposure'] = min(cf_df['cumulative_cash_flow'])
        cf_info['total_free_cash_flow'] = cf_df['cumulative_cash_flow'].values[-1]

        self.cf_infos = cf_info

    def convert_values_USD_EUR(self, initial_values, to_ignore=None, currency_from='USD', currency_to='EUR'):
        """
        Generic conversion function for a dataframe from USD to EUR or EUR to USD
        Handle conversion of int, float, dict and DataFrame

        """
        exchange_rate = 1
        if currency_from == 'USD' and currency_to == 'EUR':
            exchange_rate = self.exchange_rate_USD_EUR
        elif currency_from == 'EUR' and currency_to == 'USD':
            exchange_rate = 1 / self.exchange_rate_USD_EUR

        if isinstance(initial_values, (int, float)):
            converted_values = initial_values * exchange_rate
        elif isinstance(initial_values, dict):
            converted_values = deepcopy(initial_values)

            # verify df_dict
            if all(isinstance(value, pd.DataFrame) for value in initial_values.values()):
                # it is a dict of DataFrame, we recursively call the convert
                # function on each Dataframe
                for key, value in initial_values.items():
                    converted_values[key] = self.convert_values_USD_EUR(
                        initial_values=value, to_ignore=to_ignore, currency_from=currency_from, currency_to=currency_to)
            else:
                # regular dict
                for key, value in initial_values.items():
                    if key not in to_ignore:
                        converted_values[key] = value * exchange_rate
        elif isinstance(initial_values, pd.DataFrame):
            converted_values = deepcopy(initial_values)

            converted_values[[col for col in converted_values.columns if col not in to_ignore]] = converted_values[[
                col for col in converted_values.columns if col not in to_ignore]] * exchange_rate
        else:
            raise f'Cannot convert values of type {type(initial_values)}'

        return converted_values

    def convert_cf_USD_EUR(self):
        """

        """
        col_not_to_convert = ['years', 'year', 'quantity', 'cumulative_quantity',
                              'discount',  'pdp_perc',  'lc_coef_new', 'lc_coef_mod', 'Quarters']

        return self.convert_values_USD_EUR(initial_values=self.cf_df, to_ignore=col_not_to_convert, currency_from='USD', currency_to='EUR')

    def convert_cf_infos_USD_EUR(self):
        """

        """
        col_not_to_convert = ['irr', 'year_min_irr',
                              'year_max_irr', 'year_break_even']

        return self.convert_values_USD_EUR(initial_values=self.cf_infos, to_ignore=col_not_to_convert, currency_from='USD', currency_to='EUR')

    def get_cashflow_df(self):
        return self.cf_df

    def get_cashflow_infos(self):
        return self.cf_infos

    def _compute_revenues(self):
        raise NotImplementedError()

    def _compute_costs(self):
        raise NotImplementedError()
