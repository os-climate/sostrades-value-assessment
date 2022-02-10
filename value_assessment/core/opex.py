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
import math
from copy import deepcopy


class Opex():
    '''
    Class that implements OPEX model
    '''
    MODEL_NAME = ''
    model_type = 'OpEx'

    def __init__(self, escalation_rate, year_start_escalation_rate, launch_year, year_start, year_end,
                 learning_curve_dict):

        # init dataframes
        self.year_end = year_end
        self.year_start = year_start
        self.launch_year = launch_year
        self.escalation_rate = escalation_rate
        self.year_start_escalation_rate = year_start_escalation_rate
        self.years = self.year_end - self.year_start + 1
        self.year_vector = np.arange(self.year_start, self.year_end + 1)
        self.opex_df = pd.DataFrame({'years': self.year_vector})
        self.learning_curve_dict = learning_curve_dict
        self.sales_df = None

    def value_vs_time(self, value):

        updated_value = np.ones(self.years) * value

        if self.launch_year > self.year_start:
            updated_value[0:self.launch_year - self.year_start] = 0

        return updated_value

    def apply_escalation(self, serie_before_escalation):
        '''
        Apply escalation_rate starting at year_start_escalation_rate
        '''

        if isinstance(serie_before_escalation, np.ndarray):
            serie_before_escalation = pd.Series(serie_before_escalation)

        df = pd.DataFrame({'years': range(
            int(self.year_start), int(self.year_end) + 1)})

        df['escalated_list'] = serie_before_escalation.values.tolist()
        df['escalated_list'] = df['escalated_list'] * (1.0 + self.escalation_rate) ** \
            (df['years'] - self.year_start_escalation_rate)

        return np.array(df['escalated_list'])

    def compute_opex(self, sales):

        self.sales_df = deepcopy(sales)
        # compute opex without escalation
        opex = self.value_vs_time(self.opex)
        self.opex_df['opex_wo_escalation'] = opex

        self.apply_learning_curve()

        # apply escalation rate to opex computation to consider inflation
        self.opex_df['opex'] = self.apply_escalation(
            self.opex_df['opex_wo_escalation'])

        list_name_lc = ['opex_Make', 'opex_Buy', 'opex_Make_wo_LC']

        self.opex_df[list_name_lc] = self.opex_df[list_name_lc].apply(
            lambda x: self.apply_escalation(x))

        return self.opex_df

    def apply_learning_curve(self):
        '''
        Compute opex :
            opex = % Make + % Buy

        '''
        # Learning curve coef
        lc_df = self.compute_learning_curve_coef(self.learning_curve_dict)

        self.opex_df = self.opex_df.merge(lc_df, how='left').fillna(0)

        self.opex_df['opex_Make'] = self.learning_curve_dict['percentage_make'] / \
            100. * self.opex_df['opex_wo_escalation']
        self.opex_df['opex_Buy'] = (
            1 - self.learning_curve_dict['percentage_make'] / 100.) * self.opex_df['opex_wo_escalation']

        self.opex_df['opex_Make_wo_LC'] = self.opex_df['opex_Make']
        self.opex_df['opex_Make'] = self.opex_df['opex_Make_wo_LC'] * \
            self.opex_df['learning_curve_coef']

        # compute opex per product unit
        self.opex_df['opex_wo_escalation'] = self.opex_df['opex_Make'] + \
            self.opex_df['opex_Buy']

        return self.opex_df

    def compute_opex_by_category(self, opex_by_category, sales, distrib_after_sales_opex_unit, opex_multiplier=1.0):

        detailed_opex = pd.DataFrame(
            {'years': self.year_vector})

        opex_total = 0
        for index, row in opex_by_category.iterrows():
            opex_total += float(row['opex'])
            detailed_opex[f'opex_{row["components"]}'] = self.apply_escalation(
                self.value_vs_time(row['opex']))

        opex_total = opex_total * opex_multiplier
        self.opex = opex_total

        # compute opex
        self.compute_opex(sales)

        self.opex_df = self.opex_df.merge(detailed_opex)

        self.opex_df = self.compute_after_sales(
            opex_df=self.opex_df, distrib_after_sales_opex_unit=distrib_after_sales_opex_unit)

        # apply escalation on after sales
        self.opex_df['opex_after_sales'] = self.apply_escalation(
            self.opex_df['opex_after_sales'])

        return self.opex_df

    def compute_learning_curve_coef(self, lc_dict):
        '''
        Compute learning curve coefficient :
        '''

        if not 'cumulative_quantity' in self.sales_df:
            self.sales_df['cumulative_quantity'] = self.sales_df['quantity'].cumsum()

        # create a file with one rank per line
        final_df = pd.DataFrame(
            {'until_product_rank': range(1, int(max(self.sales_df['cumulative_quantity'].max(), max(lc_dict['until_product_rank']))) + 1)})
        final_df = final_df.merge(
            self.sales_df, how='left',  left_on='until_product_rank', right_on='cumulative_quantity')
        final_df = final_df.fillna(method='bfill')
        final_df = final_df[final_df['quantity'] != 0]

        # compute learning curve from dictionnary data
        final_df['learning_curve_coef'] = np.NaN
        for i in range(len(lc_dict['until_product_rank'])):
            if i == 0:
                final_df.loc[final_df['until_product_rank'] <= lc_dict['until_product_rank'][i], 'learning_curve_coef'] = final_df.loc[(
                    final_df['until_product_rank'] <= lc_dict['until_product_rank'][i]), 'until_product_rank']**(math.log(lc_dict['learning_curve_coefficient'][i]) / math.log(2))
            else:

                index_i = (final_df['until_product_rank'] <= lc_dict['until_product_rank'][i]) & (
                    final_df['until_product_rank'] > lc_dict['until_product_rank'][i - 1])

                # calculate learning curve coef (optimised version)
                def calc_lc_coef(s):
                    newColumn = [final_df.loc[(
                        final_df['until_product_rank'] == lc_dict['until_product_rank'][i - 1]), 'learning_curve_coef'].values[0]]

                    for j, val in enumerate(s):
                        newColumn.append((val)**(math.log(lc_dict['learning_curve_coefficient'][i]) / math.log(2)) /
                                         (val - 1)**(math.log(lc_dict['learning_curve_coefficient'][i]) / math.log(2)) * newColumn[j])
                    return newColumn[1:]

                final_df.loc[index_i, 'learning_curve_coef'] = final_df.loc[index_i][[
                    'until_product_rank']].apply(calc_lc_coef).values

        final_df = final_df.fillna(method='ffill')
        rank_ref_costing = max(lc_dict['until_product_rank'])
        if len(final_df['until_product_rank']) >= rank_ref_costing:
            final_df['learning_curve_coef'] = (final_df['learning_curve_coef'] / final_df.loc[final_df['until_product_rank']
                                                                                              == rank_ref_costing, 'learning_curve_coef'].values).expanding().mean()

        df = self.sales_df.merge(final_df[['until_product_rank', 'learning_curve_coef']], how='left',
                                 left_on='cumulative_quantity', right_on='until_product_rank').drop(['until_product_rank'], axis=1)

        df['learning_curve_coef'] = (((df['learning_curve_coef'] * df['cumulative_quantity']) - (
            df['learning_curve_coef'].shift(1).fillna(0) * df['cumulative_quantity'].shift(1).fillna(0))) / df['quantity']).fillna(0)

        return df

    def compute_after_sales(self, opex_df, distrib_after_sales_opex_unit):

        # Initialise dataframe
        after_sales_df = pd.DataFrame({'years': range(
            min(self.year_start, self.launch_year - 1), max(self.year_end + 1, self.launch_year + 11))})
        after_sales_df.insert(after_sales_df.columns.size,
                              'opex_after_sales', 0)

        after_sales_df = after_sales_df.merge(
            opex_df[['years', 'opex_wo_escalation']], how='left').fillna(0)

        # compute values on the opex and distribution of opex unit
        after_sales_df.loc[(self.launch_year + 9 >= after_sales_df['years']) & (after_sales_df['years'] >= self.launch_year), 'opex_after_sales'] = after_sales_df.loc[(
            self.launch_year + 9 >= after_sales_df['years']) & (after_sales_df['years'] >= self.launch_year), 'opex_wo_escalation'] * np.array(distrib_after_sales_opex_unit[:-1])

        # from launch_year+10 to year_end use the last element of the
        # distribution
        if self.year_end >= (self.launch_year + 10):
            after_sales_df.loc[after_sales_df['years'] >= self.launch_year + 10, 'opex_after_sales'] = after_sales_df.loc[after_sales_df['years'] >= self.launch_year + 10, 'opex_wo_escalation'] * \
                distrib_after_sales_opex_unit[-1]

        # keep values only between year_start and year_end
        opex_df = opex_df.merge(after_sales_df.loc[(self.year_end >= after_sales_df['years']) & (
            after_sales_df['years'] >= self.year_start), ['years', 'opex_after_sales']])

        return opex_df
