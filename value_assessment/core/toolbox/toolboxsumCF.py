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




from sos_trades_core.tools.sumdfdict.toolboxsum import toolboxsum
from value_assessment.core.toolbox.IRR import IRR
class toolboxsumCF(toolboxsum):
    '''
    classdocs
    '''

    def __init__(self, timeframe='years'):
        '''
        Constructor
        '''
        toolboxsum.__init__(self)
        self.cf_infos = None
        self.timeframe = timeframe

    def compute_sum_vb(self, list_df, not_sum):
        cf_df, percent = self.compute_sum_df(list_df, not_sum)
        cf_info = self.compute_cf_df_info(cf_df)

        return cf_df, cf_info, percent

    def compute_cf_df_info(self, cf_df):
        # define it at value block level

        cf_info = {}

        # IRR on all years
        irr_ob = IRR(cf_df['cash_flow'])
        cf_info['irr'] = irr_ob.compute_irr()
        # cf_info['year_min_irr'] = cf_df['years'].values[0]
        # cf_info['year_max_irr'] = cf_df['years'].values[-1]

        cf_info['npv'] = cf_df['cumulative_discounted_cf'].values[-1]
        if cf_df['years'][cf_df['cumulative_discounted_cf'] > 0].empty:
            cf_info['year_break_even_discounted_cashflow'] = cf_df['years'].values[-1]
        else:
            cf_info['year_break_even_discounted_cashflow'] = min(
                cf_df['years'][cf_df['cumulative_discounted_cf'] > 0])
            
        if cf_df['years'][cf_df['cumulative_discounted_cf'] > 0].empty:
            cf_info['year_break_even_cashflow'] = cf_df['years'].values[-1]
        else:
            cf_info['year_break_even_cashflow'] = min(
                cf_df['years'][cf_df['cumulative_discounted_cf'] > 0])
        # cf_info['max_peak_exposure'] = min(cf_df['cumulative_cash_flow'])
        cf_info['peak_exposure'] = min(cf_df['cumulative_cash_flow'])
        cf_info['total_free_cash_flow'] = cf_df['cumulative_cash_flow'].values[-1]

        return cf_info

    def compute_hypothesis_df_info(self, cf_df, cf_df_gather):
        # define it at value block level

        cf_df['year_start_escalation_capex'] = int(
            cf_df_gather[list(cf_df_gather.keys())[0]]['year_start_escalation_capex'])
        cf_df['year_start_escalation_opex'] = int(
            cf_df_gather[list(cf_df_gather.keys())[0]]['year_start_escalation_opex'])
        cf_df['last_year'] = int(
            cf_df_gather[list(cf_df_gather.keys())[0]]['last_year'])

        if 'sale_price_last_year' in cf_df and cf_df['sale_price_last_year'] != 0:
            cf_df['contribution_margin_last_year'] = (
                cf_df['sale_price_last_year'] - cf_df['opex_last_year']) / cf_df['sale_price_last_year']
        else:
            cf_df['contribution_margin_last_year'] = 0

        return cf_df
