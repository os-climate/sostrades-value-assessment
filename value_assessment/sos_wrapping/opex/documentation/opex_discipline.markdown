# Operating Expenditure Model
All input and output values are in EUR (€).

## Escalation
OpEx input are escalated with the parameters from  **escalation_opex_df**.
The escalation process is similar to the concept of inflation but takes into account changes in technology, practices, and particularly supply-demand imbalances.
The calculation is based on the **year_economical_conditions** as well as the **yearly_escalation_rate**.

$$OpEx_{escalated} = OpEx * ( 1 + \frac {yearly\_escalation\_rate} {100.})^{year-year\_economical\_condition}$$


## Learning Curve

Using the input **learning_curve_product_dict**, we can apply a simple learning curve (or experience curve) to the OpEx.
The learning curve takes 2 parameters, the product **rank** until which we apply the learning curve and the **coefficient** which configure the characteristics of the learning curve. 

OpEx are split into Make and Buy and learning curve only apply on the Make part. This is specified using the input **learning_curve_product_dict['percentage_make']**.

$$OpEx\_Make = Percentage\_Make*OpEx$$


Exemple:

**learning_curve_product_dict** = {'percentage_make': 0., 'learning_curve_coefficient':[0.8,0.9],'until_product_rank': [50.,200.]}

This means that there is a learning curve with a coefficient of 0.8 until rank 50 and a coefficient of 0.9 for product rank between 51 and 200. 

The calculation detail for a learning curve with coefficient 0.8 for 50 product is detailed below:

$$logvar = \frac{log(0.8)}{log(2)}$$

For each product rank, we have :

$$unit\_opex(rank) = rank^{logvar}$$ 
$$cumul(rank) = unit\_opex(rank) - unit\_opex(rank-1)$$
$$average\_rank = \frac{cumul(rank)}{rank}$$

For each year, we have :
$$sales(year) = sales\_of\_the\_year$$
$$cum\_sales(year) = cumulative\_sales\_of\_the\_year$$
$$average(year) = \frac{average\_rank(cum\_sales(year))} {unit\_opex (50)}$$
$$LearningCurve\_coef(year) = \frac{cum\_sales(year)*average(year) - cum\_sales(year-1)*average(year-1)} {sales(year)}$$
$$OpEx\_with\_learning\_curve(year) = OpEx(year) * LearningCurve\_coef(year)$$


## OpEx After Sales
OpEx After sales can be added using the variable **after_sales_opex_unit** and are calculated from **launch_year** to ending year by applying a percentage of the unit OpEx.


## Synthesis of calculation


```mermaid
graph LR
    A((OpEx)) -- 1- %Make --> D(OpEx Buy)
    A -- %Make --> E(OpEx Make)
    A -- after_sales_opex_unit --> F(OpEx After Sales)
    D --> G[Escalation]
    F --> H[Escalation]
    E --> L[Escalation and Learning Curve]
    G --> I{{OpEx_unit_year}}
    L --> I
    H --> I
    I -- sales_qty --> J{{OpEx_total_year}}
```


## Outputs

Two outputs are calculated : 
 - OpEx per product with the details concerning Make, Buy and After Sales
 - Total OpEx sum for the total quantity of product each year