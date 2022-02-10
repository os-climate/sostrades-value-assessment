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


class IRR():
    """
    Class to compute IRR
    """

    def __init__(self, cashflow):
        """
        Init of the IRR class 
        ::params:: cashflow : array of cashflow 
        """
        self.cashflow = cashflow

    def compute_irr(self):
        """
        Method to compute internal rate of return, returns the first real positive root of the npv, 'NA' if no positive value / no solution
        """
        res = np.roots(self.cashflow[::-1])
        mask = (res.imag == 0) & (res.real > 0)
        # if no root is real, return NA
        if not mask.any():
            return 'NA'
        res = res[mask].real
        # NPV(rate) = 0 can have more than one solution so we return
        # only the solution closest to zero.
        rate = 1 / res - 1
        filtered_rates = [value for value in rate if value >= 0]
        # sort list
        filtered_rates.sort()
        if len(filtered_rates) > 0:
            return filtered_rates[0]
        else:
            return 'NA'
