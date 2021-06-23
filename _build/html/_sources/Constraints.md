Constraints
=======================

## Potential restricition rule

## Power restriction rule

## Electrical power generation

## Heating generation covers demand 
At any time, the heating generation must cover the heating demand.


## Capacity restriction rule - maximum

## Capacity restriction rule - minimum



## Generation restriction rule
The amount of heat energy generated must not exceed the installed capacities.

## Generation rule - minimum operating power
All generators have a *minimum operating power*.

### Generation minimum heat power

### Must run rule

### Must run rule 2

### Must run rule 3
`mr` specifies the amount of capacity that has to run all the time (0-1).
## Solar restriction rule
Solar gains depend on the installed capacity and the solar radiation. The value `1000` represents the radiation at wich the solar plant has *maximal power*.

## Waste incineration restriction rule
No investment in waste incineration plants possible, thus geneartion can't exeed already installed capacities.

## Power loss when full heat extraction
With full heat extraction, a loss of power can occur which, only reduces the maximum power.


### CHP generation restriction rule 1

### CHP generation restriction rule 2

### CHP generation restriction rule 5

## Decrese of maximum heat decoupling
The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling with the produced electrical net power

### CHP generation restriction rule 3

### CHP generation restriction rule 4
Setting capacity  for *chp generation*.

### Storage state heat storage rule 
*Heat storage level* = *old_level* + *pumping*  - *turbining*

### Storage capacity restriction heat storage rule
Installed capcities must be greater or equal to the pre-installed capacities.

### Load heat storage restriction rule
The discharge and charge amounts are limited

### Unload heat storage restriction rule

## Ramp CHP rule

## Ramp waste rule

## Coldstart rule

## Renewable factor rule
