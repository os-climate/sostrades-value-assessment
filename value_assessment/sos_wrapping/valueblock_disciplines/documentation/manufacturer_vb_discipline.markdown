# Manufacturer Value Block  
A complete cash flow and P\&L model is implemented. 
All values are available in euros (€).

## Revenues :
Product price is given as input in a table with a price per year.


## Operating Expenditure (OpEx) : 
OpEx payment terms before deliveries can be applied as a percentage of OpEx for year before delivery and two years before delivery. 

## Capital Expenditure (CapEx) :
For further accounting purposes, CapEx will be split in two kinds : CapEx which are amortizable and other which are not.

$$CapEx = CapEx\_amort + CapEx\_Non\_amort$$

CapEx non amortizable contains Contingency if calculated by the CapEx discipline.

## Capital Depreciation
Capital depreciation is calculated for each CapEx Category with a given number of years of amortization.

$$Capital\_dep = 0$$

For i in [year_start; year_end] :

$$Capital\_dep(year \geq i \space \& \space year < i + nb\_years\_amort) = \\ Capital\_dep(year \geq i \space \& \space year < i + nb\_years\_amort) + \frac{CapEx\_Category(year ==i) }{ nb\_years\_amort}$$

## Inventories
We hereafter refer to "Inventory" model as the way to assess the cash advances to suppliers, hence the Account Payables assumptions to convert OpEx from P&L approach into Cash Out and vice-versa.

A first inventories model is defined by :

$$Inventories(year_n) = \sum_{k=year\_start}^{year_n} OpEx\_payment\_terms(year_k)*Quantities(year_k) \\ - \sum_{k=year\_start}^n OpEx(year_k)*Quantities(year_k)$$

## Cash Flow approach

- Cash in: Qty delivered x Escalated price with down-payment effect.
- Cost of Good Sold (COGS) = Qty delivered x OpEx escalated with Account Payables effect (Inventory model)
- CapEx: as is (spread per year) 

Cash flow is updated with equation :

$$Cashflow = Cash\_in + Cash\_out$$

with :

$$Cash\_in = Revenues$$
$$Cash\_out = - CapEx - OpEx\_payment\_terms*quantity - OpEx\_after\_sales * quantity$$

Standard cumulative cash flows and Discounted Cash Flows are computed from the free cash flow :

$$Cumulative\_Cashflow(year_n) = \sum_{k=year\_start}^n Cashflow(year_k)$$

$$Discounted\_Cashflow(year_n) = Cashflow*(\frac{1}{1+WACC})^{year_n - year\_start}$$

$$Cumulative\_Discounted\_Cashflow(year_n) = \sum_{k=year\_start}^n Discounted\_Cashflow(year_k)$$

## Profit & Loss approach (P\&L)

- Cost of Good Sold (COGS) = Qty delivered x OpEx escalated.
- Total Costs: Cash\_out\_EBIT. Includes direct, indirect and depreciation of assets.
- CapEx: amortized per category (see above) 

P\&L (Profit and Loss) is defined by : 

$$EBIT =  Cash\_in\_EBIT + Cash\_out\_EBIT$$
with
$$Cash\_in\_EBIT = Revenues$$
$$Cash\_out\_EBIT = - CapEx\_amort\_EBIT - CapEx\_non\_amort \\- OpEx*quantity - OpEx\_after\_sales * quantity$$

$$Cumulative\_EBIT(year_n) = \sum_{k=year\_start}^n EBIT(year_k)$$

## Global parameters

Other parameters are calculated :
- NPV (Net Present Value) is the Cumulative Discounted Cashflow value at year_end.
- IRR (Internal Rate of Return) is the solution of : 
  
$$\sum_{k=0}^{n} \frac{Cashflow(year_k)}{(1 + IRR)^k} = 0$$

- Maximum peak exposure is the minimal value of Cumulative Cashflow.
- Break even is the first year at which Cumulative Discounted Cashflow is positive if possible, else it is year_end.





 
