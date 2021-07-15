Objective Function
=======================
For detailed information about the variables, go to  {doc}`Model Description`.

Investment costs in {eq}`first_eq`.


$$
c_{inv} = \sum_j (Cap_j - x_{{th}_{cap,j}}) * IK_j *\alpha_j + \sum_{hs}(Cap_{hs} - cap_{hs}) * IK_{hs} *\alpha_{hs}
$$ (first_eq)



Fixed op price costs in {eq}`second_eq`.


$$
c_{op_{fix}} = \sum_j Cap_j * OP_{{fix}_j} + \sum_{hs} Cap_{hs} * OP_{{fix}_{hs}}
$$ (second_eq)

Variable op costs in {eq}`third_eq`.


$$
c_{op_{var}} = \sum_{j,t} x_{{th}_j,t} * OP_{{var}_j} 
$$ (third_eq)


Variable costs in {eq}`fourth_eq`.


$$
c_{var} = \sum_{j,t} x_{{th}_j,t} * mc_{j,t} 
$$ (fourth_eq)


$$
c_{ramp} = \sum_{j,t} ramp_{{j}_{waste}} * c_{{ramp}_{waste}} + \sum_{j,t} ramp_{{j}_{chp,t}} * ramp_{chp}
$$ (fifth_eq)



$ c_{cold} $ in {eq}`sixth_eq` counts up the coldstarts and multiplies it with the coldstart costs.


$$
c_{cold} = \sum_{j,t} coldstart_{jt} * c_{coldstart_{j}} 
$$ (sixth_eq)

Sum of all costs is calculated in {eq}`seventh_eq`.


$$
c_{tot} =  c_{inv} + c_{var} + c_{op_{fix}} + c_{op_{var}} + c_{cold} + c_{ramp}
$$ (seventh_eq)



$$
rev_{gen_{electricity}} =  \sum_{j,t} x_{el_{jt}} * sale_{electricityprice_{j,t}}
$$ (eighth_eq)



{eq}`ninth_eq`shows all costs which are subtracted by the electricity generation. 


$$
rule =  c_{tot} - rev_{gen_{electricity}}
$$ (ninth_eq)