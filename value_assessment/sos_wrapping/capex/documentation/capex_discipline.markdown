# Capital Expenditure Model
All input and output values are in EUR (€).

## Escalation
CapEx input are escalated with the parameters from  **escalation_capex_df**.
The escalation process is similar to the concept of inflation but takes into account changes in technology, practices, and particularly supply-demand imbalances.
The calculation is based on the **year_economical_conditions** as well as the **yearly_escalation_rate**.

$$CapEx_{escalated} = CapEx * (1 + \frac {yearly\_escalation\_rate} {100} )^{year-year\_economical\_conditions}$$


CapEx are calculated from launch year - 6 to year_end with a total CapEx value given in € multiply by a percentage.
Default percentages of CapEx total value for each year are : {'launch_year-6': 10, 'launch_year-5': 15, 'launch_year-4': 15, 'launch_year-3': 30, 'launch_year-2': 15, 'launch_year-1': 15, 'launch_year': 5, 'launch_year+1': 5, 'launch_year+2': 5, 'launch_year+3': 5, 'launch_year+4 onwards': 1}.

If CapEx are given by category, a different CapEx distribution can be given to each category via the variable **CapEx Distribution by Category**


A Contingency can be added on top of CapEx via a percentage of CapEx (15% by default).


## Outputs

The output calculated : 
 - CapEx per product with the details concerning distribution categories.