Constraints
=======================

## Potential restricition rule

In {eq}`eq_one` you can see the potential of the jth heat generator defines the upper bound for the sum over all the thermal energy values. 
If  $potential_j >  0$ , then {eq}`eq_one`is used.

$$
\sum_t (Cap_j - x_{{th}_{j,t}}) \le potential_j 
$$ (eq_one)

## Power restriction rule
If  $pow_{cap_{j}} >  0$ , then {eq}`eq_two` is used.

$$
\sum_t (Cap_j - x_{{th}_{j,t}}) \le pow_{cap_{j}} 
$$ (eq_two)

## Electrical power generation
If *j* is valid or $n_{{th}_{j,t}} \neq 0$ , then {eq}`eq_three`is used.

$$
x_{{el}_{j,t}} = \frac{x_{{th}_{j,t}}}{n_{{th}_{j,t}}}\  \cdot n_{{el}_{j}} 
$$ (eq_three)


## Heating generation covers demand 
At any time, the heating generation must cover the heating demand.

$$
\sum_t (x_{{th}_{j,t}}) - \sum_{hs} (x_{{load}_{hs,t}}) = demand_{f} \cdot demand_{th_{t}}
$$ (eq_four)


## Capacity restriction rule - maximum

If the *inv_flag* is set *true*, then the rule in {eq}`eq_five` is valid, otherwise {eq}`eq_six` is valid.

$$
Cap_j \le demand_{f} \cdot max_{demand} 
$$ (eq_five)

$$
Cap_j = x_{{th}_{cap,j}} 
$$ (eq_six)


## Capacity restriction rule - minimum

$$
Cap_j \ge x_{{th}_{cap,j}} 
$$ (eq_six)


## Generation restriction rule
The amount of heat energy generated must not exceed the installed capacities.
$$
x_{{th}_{j,t}} \le  \frac{Cap_{j}}{n_{{th}_{nom,jt}}}\  \cdot n_{{th}_{j,t}} \cdot Active_{j,t} \cdot restrictionfactor_{j,t}
$$ (eq_seven)


## Generation rule - minimum operating power
All generators have a *minimum operating power*.

$$
x_{{th}_{j,t}} \ge \frac{Cap_{j}}{n_{{th}_{nom,jt}}}\ \cdot n_{{th}_{j,t}} \cdot Active_{j,t} \cdot min_{out_{factor,j}}
$$ (eq_eight)


### Must run rule
$$
x_{{th}_{j,t}} \ge \frac{mr_{j} \cdot Cap_j}{n_{{th}_{nom,jt}}}\ \cdot n_{{th}_{j,t}} \cdot restrictionfactor_{j,t} \cdot Active3_{j,t} 
$$ (eq_nine)



### Must run rule 2

$$
x_{{th}_{j,t}} \ge demand_{th_{t}}  \cdot Active2_{j,t} 
$$ (eq_eleven)

### Must run rule 3
$$
Active2_{j,t} + Active3_{j,t} = 1
$$ (eq_twelf)


## Solar restriction rule
Solar gains depend on the installed capacity and the solar radiation. The value `1000` represents the radiation at wich the solar plant has *maximal power*, see {eq}`eq_thirteen`.

$$
x_{{th}_{j,t}} \le \frac{Cap_{j} \cdot radiation_t}{max(radiation_t)}\ 
$$ (eq_thirteen)

## Waste incineration restriction rule
No investment in waste incineration plants possible, thus geneartion can't exeed already installed capacities.
$$
x_{{th}_{j,t}} \le x_{{th}_{cap,j}}
$$ (eq_fourteen)

## Power loss when full heat extraction
With full heat extraction, a loss of power can occur which, only reduces the maximum power.

### CHP generation restriction rule 1

$$
sv_{chp} = \frac{ratioPMaxFW - ratioPMax}{ratioPMax \cdot ratioPMaxFW}\
$$ (eq_fifteen)

$$
x_{{el}_{j,t}} \le \frac{Cap_j}{ratioPMax}\ - (sv_{chp} \cdot x_{{th}_{j,t}})
$$ (eq_sixteen)


### CHP generation restriction rule 2

$$
P_{min_{el,chp}} \le x_{{el}_{j,t}}  
$$ (eq_seventeen)

### CHP generation restriction rule 5

$$
Q_{min_{th,chp}} \le x_{{th}_{j,t}}  
$$ (eq_eighteen)

## Decrese of maximum heat decoupling
The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling with the produced electrical net power

### CHP generation restriction rule 3

Depending on the value of *j*, {eq}`eq_nineteen` or {eq}`eq_twenty` will be taken.


$$
x_{{el}_{j,t}} \ge \frac{x_{{th}_{j,t}}}{ratioPMaxFW}\
$$ (eq_nineteen)


$$
x_{{el}_{j,t}} == \frac{x_{{th}_{j,t}}}{n_{{th}_{j,t}}}\ \cdot n_{{el}_{j}}
$$ (eq_twenty)

### CHP generation restriction rule 4
Setting capacity  for *chp generation*.

$$
x_{{th}_{j,t}} \le demand_{th_t} + \sum_{hs} x_{load_{hs,t}}
$$ (eq_twentyone)



### Storage state heat storage rule 
*Heat storage level* = *old_level* + *pumping*  - *turbining*
Depending on the value of *t* there is one special condition rule. If *t* is equal to *1*, {eq}`eq_twentytwo` is taken, otherwise {eq}`eq_twentythree`. 

$$
store_{level_{hs,t}}(hs,t) == store_{level_{hs,t}}(hs,8760)
$$ (eq_twentytwo)


$$
store_{level_{hs,t}}(hs,t) == store_{level_{hs,t-1}}(hs,8760) \cdot (1- cap_{losse_{hs}}) + x_{load_{hs,t}} (hs, t-1) \cdot n_hs
$$ (eq_twentythree)


### Storage capacity restriction heat storage rule
Installed capcities must be greater or equal to the pre-installed capacities. If the *inv_flag* is set, then {eq}`eq_twentyfour` is taken, otherwise {eq}`eq_twentyfive`. 

$$
Cap_{hs} \ge cap_hs
$$ (eq_twentyfour)

$$
Cap_{hs} == cap_hs
$$ (eq_twentyfive)

### Storage state capacity restriction heat storage rule

$$
store_{level_{hs,t}}(hs,t) \le Cap_hs
$$ (eq_twentysix)


### Load heat storage restriction rule
The discharge and charge amounts are limited

$$
x_{load_{hs,t}}(hs,t) \le load_{cap_{hs}}
$$ (eq_twentyseven)


### Unload heat storage restriction rule
If the *flag* is set, then the {eq}`eq_twentyeight` is taken, otherwise {eq}`eq_twentynine`. 

$$
x_{load_{hs,t}}(hs,t) \ge -unload_{cap_{hs}}
$$ (eq_twentyeight)


$$
x_{load_{hs,t}}(hs,t) \ge -store_{level_{hs,t}}(hs,t)
$$ (eq_twentynine)


## Ramp CHP rule
If *t* is equal to *1*, {eq}`eq_thirty` is taken, otherwise {eq}`eq_thirtyone`. 

$$
ramp_{j_{waste}} == 0
$$ (eq_thirty)


$$
ramp_{j_{waste}} \ge ( x_{{th}_{j,t}}(j,t) - x_{{th}_{j,t}}(j,t-1))
$$ (eq_thirtyone)

## Ramp waste rule
If *t* is equal to *1*, {eq}`eq_thirtytwo` is taken, otherwise {eq}`eq_twentythree`. 


$$
ramp_{j_{waste,t}} == 0
$$ (eq_thirtytwo)

$$
ramp_{j_{waste,t}} \ge ( x_{{th}_{j,t}}(j,t) - x_{{th}_{j,t}}(j,t-1))
$$ (eq_thirtythree)


## Coldstart rule
If *t* is equal to *1*, {eq}`eq_thirtyfour` is taken, otherwise {eq}`eq_thirtyfive`. 

$$
coldstart_{j,t} == 1
$$ (eq_thirtyfour)

$$
coldstart_{j,t} \ge ( activate_{j,t}(j,t) - activate_{j,t}(j,t-1))
$$ (eq_thirtyfive)

{eq}`eq_thirtyfive` has only a *true* output for coldstarts.


## Renewable factor rule
If   $ \sum_j rf_j \neq 0$, {eq}`eq_thirtysix` is taken.


$$
\sum_j (\sum_t (x_{{th}_{j,t}} + x_{{el}_{j,t}}) \cdot rf_j) \ge rf_{tot} \cdot \sum_j (\sum_t (x_{{th}_{j,t}} + x_{{el}_{j,t}})
$$ (eq_thirtysix)

