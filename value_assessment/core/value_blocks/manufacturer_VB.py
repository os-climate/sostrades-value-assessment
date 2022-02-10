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
from value_assessment.core.toolbox.vb_meta import ValueBlock


class ManufacturerVB(ValueBlock):
    '''
    classdocs
    '''

    def __init__(self, year_start, year_end, launch_year, manufacturer_dict, actor_name=None, actor_wacc=None, exchange_rate_USD_EUR=None):
        '''
        Constructor
        '''

        ValueBlock.__init__(self, year_start,
                            year_end, actor_name, actor_wacc, exchange_rate_USD_EUR)

        self.price_product = None
        self.opex = None
        self.capex = None
        self.sales = None
        self.manufacturer_dict = manufacturer_dict
        self.launch_year = launch_year

    def configure_data(self, sales_qty_product, opex_product, capex_product, price_product):
        """
        Configure object
        """

        self.opex = opex_product
        self.capex = capex_product
        self.price_product = price_product
        self.sales = sales_qty_product

        self.sales['quantity'] = np.trunc(self.sales['quantity'])

    def _compute_revenues(self):
        '''
        Compute revenues
        '''

        # Test if data are not already created
        if not 'cash_in' in self.cf_df:
            # multiply quantity by price
            self.cf_df['cash_in'] = self.cf_df['quantity'] * \
                self.cf_df['sale_price']

            self.cf_df['cash_in_PnL'] = self.cf_df['cash_in']

    def _compute_costs(self):

        # Test if data are not already created
        if not 'cash_out' in self.cf_df:

            # Merge dataframe with opex and capex data
            self.cf_df = self.cf_df.merge(self.opex)
            self.cf_df = self.cf_df.merge(self.capex)

            # merge with price df
            self.cf_df = self.cf_df.merge(
                self.price_product, how='left').fillna(0)

            # merge with sales df
            self.cf_df = self.cf_df.merge(self.sales, how='left').fillna(0)

            self.cf_df['cumulative_quantity'] = self.cf_df['quantity'].cumsum()

            # compute opex
            self.cf_df = self.compute_opex(self.cf_df)

            # Capital depreciation and amort/year for capex
            len_y = self.year_end + 1 - self.year_start

            self.cf_df['capex_amort'] = 0.
            self.cf_df['capex_amort_EBIT'] = 0.
            self.cf_df['capex_non_amort'] = self.cf_df['contingency']

            for name, values in self.capex.iteritems():
                if name.startswith('capex_'):
                    short_name = name.lstrip('capex_')

                    if (short_name in self.manufacturer_dict['nb_years_capex_amort']['Distribution Category'].to_list()):

                        nb_years = self.manufacturer_dict['nb_years_capex_amort'].loc[self.manufacturer_dict[
                            'nb_years_capex_amort']['Distribution Category'] == short_name, 'Nb years'].values[0]

                        if nb_years >= 1:
                            self.cf_df['capex_amort'] += self.cf_df[name]
                            # pylint: disable=no-member
                            self.cf_df['capex_amort_EBIT'] += (np.tril(np.triu(np.ones((len_y, len_y)), k=0),
                                                                       k=nb_years - 1).T * np.array(values / nb_years)).T.sum(axis=0)
                            # pylint: enable=no-member
                        else:
                            self.cf_df['capex_non_amort'] += self.cf_df[name]
                    else:
                        self.cf_df['capex_non_amort'] += self.cf_df[name]

            # final cash_out
            self.cf_df['cash_out'] = - self.cf_df['capex_amort'] - self.cf_df['capex_non_amort'] - \
                self.cf_df['opex_total_pay'] - \
                self.cf_df['opex_after_sales'] * self.cf_df['quantity']

            self.cf_df['cash_out_PnL'] = - self.cf_df['capex_non_amort'] - \
                self.cf_df['capex_amort_EBIT'] - \
                self.cf_df['opex_total'] - \
                self.cf_df['opex_after_sales'] * self.cf_df['quantity']

            # Inventory
            self.cf_df['Inventory'] = self.cf_df['opex_total_pay'].cumsum() - \
                self.cf_df['opex_total'].cumsum()

    def compute_opex(self, cf_df):
        '''
        Compute opex 

        '''
        cf_df['opex_total'] = cf_df['opex'] * cf_df['quantity']

        # compute opex payment before deliveries
        cf_df['opex_payment_term_year-1'] = (cf_df['opex_total'] * self.manufacturer_dict['opex_payment_term_percentage']
                                             ['percentage_at_delivery_year-1'][0] / 100.).shift(-1).fillna(0)
        cf_df['opex_payment_term_year-2'] = (cf_df['opex_total'] * self.manufacturer_dict['opex_payment_term_percentage']
                                             ['percentage_at_delivery_year-2'][0] / 100.).shift(-2).fillna(0)
        cf_df['opex_payment_term_at_delivery'] = cf_df['opex_total'] * (1 - self.manufacturer_dict['opex_payment_term_percentage']['percentage_at_delivery_year-1'][0] / 100.
                                                                        - self.manufacturer_dict['opex_payment_term_percentage']['percentage_at_delivery_year-2'][0] / 100.)

        cf_df['opex_total_pay'] = cf_df['opex_payment_term_at_delivery'] + \
            cf_df['opex_payment_term_year-1'] + \
            cf_df['opex_payment_term_year-2']

        return cf_df
