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
class Capex():
    '''
    Class that implements CAPEX model
    '''
    MODEL_NAME = ""
    model_type = "CAPEX"

    def __init__(self, escalation_rate, year_start_escalation_rate, launch_year, year_start, year_end, logger=None):

        # init dataframes
        self.year_end = year_end
        self.year_start = year_start
        self.launch_year = launch_year
        self.escalation_rate = escalation_rate
        self.year_start_escalation_rate = year_start_escalation_rate
        self.years = self.year_end - self.year_start + 1
        self.year_vector = np.arange(self.year_start, self.year_end + 1)
        self.capex_df = pd.DataFrame({'years': self.year_vector})
        self.logger = logger

    def compute_capex_by_category(self, capex_input_values, capex_distrib_categories):
        capex_df = self.capex_df
        capex_df['capex'] = 0
        capex_df['contingency'] = 0
        # calculate capex for each defined category
        categories_list = capex_distrib_categories['Distribution Category'].values.tolist(
        )

        for category in capex_input_values['Distribution Category'].values.tolist():
            if category not in categories_list:
                self.logger.info(
                    f'capex Distribution Category <<{category}>> does not exist in inputcapex_input_values dataframe')

        for category in categories_list:
            capex_sum = capex_input_values.loc[capex_input_values[
                'Distribution Category'] == category, 'Capex value'].sum()
            capex_category_value = capex_input_values.loc[capex_input_values[
                'Distribution Category'] == category, 'Capex value'].sum()
            category_distribution_records = capex_distrib_categories.loc[capex_distrib_categories['Distribution Category']
                                                                         == category, capex_distrib_categories.columns != 'Distribution Category']

            if capex_sum != 0:
                contingency_cat = (capex_input_values.loc[capex_input_values[
                    'Distribution Category'] == category, 'Capex value'] * capex_input_values.loc[capex_input_values[
                        'Distribution Category'] == category, 'Contingency (%)'] / 100).sum() / capex_sum
            else:
                contingency_cat = 0

            if len(category_distribution_records) == 1:
                # convert percentage
                category_distribution_records /= 100.
                capex_category_distribution = category_distribution_records.values.tolist()[
                    0]
            else:
                raise Exception(
                    f'There is an issue with the inputs for capex category {category}')

            capex_df[f'capex_{category}'] = self.value_vs_time(
                capex_category_value, capex_category_distribution)

            # apply escalation
            capex_df[f'capex_{category}'] = self.apply_escalation(
                capex_df[f'capex_{category}'])

            capex_df['capex'] += capex_df[f'capex_{category}']

            capex_df['contingency'] += capex_df[f'capex_{category}'] * \
                contingency_cat

        # apply contingency
        capex_df['capex'] += capex_df['contingency']

        return capex_df

    def value_vs_time(self, value, distribution):

        d = pd.Series(0, index=np.arange(
            max(self.year_end, self.launch_year + 4) + 1))
        d[self.launch_year - 6:self.launch_year +
            4] = value * np.array(distribution[:-1])
        if self.year_end >= self.launch_year + 4:
            d[self.launch_year + 4:] = value * distribution[-1]

        updated_value = np.asarray(d[self.year_start: self.year_end + 1])

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

    def apply_ratio(self, capex_input_values, capex_ratio):
        # apply ratio on column 'Capex value'
        capex_input_values_modified = capex_input_values.copy(deep=True)
        capex_input_values_modified['Capex value'] = capex_input_values_modified[
            'Capex value'] * capex_ratio / 100

        return capex_input_values_modified
