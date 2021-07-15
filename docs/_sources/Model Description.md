Model Description
=======================
{numref}`val-tab` shows all the details for the used variables. 

{table} Variables used for mathematical description 
:name: val-tab


| symbols of variables | unit | definition | description |
| ------------------------------ | ---------- | ----------- | ----------- |
| $ x_{{th}_{j,t}} $ | non -negative real | thermal energy fed into the grid                             |             |
| $ Cap_{j} $ | non -negative real | capacity |             |
| $ Cap_{{nom}_{j}} $ | non -negative real | normative capacity |             |
| $ x_{{el}_{j,t}} $ | non -negative real | electrical energy fed into the grid |             |
| $ P_{{el}_{max}} $ | non -negative real | maximum electrical power |             |
| $ x_{{load}_{hs,t}} $ | real | optimization variable depending on the load of heat storages, time-dependent |             |
| $ Cap_{hs} $ | non -negative real | capacity of heat storage |             |
| $ storelevel_{{hs}_{t}} $ | non -negative real | storage level of heat storage, time-dependent |             |
| $ ramp_{{j}_{chp,t}} $ | non -negative real | ramp function, chp (combined heat and power) and time-dependent |             |
| $ ramp_{{j}_{waste,t}} $ | non -negative real | ramp function, waste and time-dependent | |
| $ coldstart_{j,t} $ | boolean | cold start, time-dependent | |
| $ Activate_{j,t} $ | boolean | | |
| $ Activate_{{2}_{j,t}} $ | binary | | |
| $ Activate_{{3}_{j,t}} $ | binary | | |



In {numref}`param-tab`, the parameters are mentioned and described. 

{table} Parameters used for mathematical description 
:name: param-tab



| symbols of parameters | unit | definition | description |
| --------------------- | ---- | ---- | ---- |
| $ demand_{{th}_{t}} $ |  | thermal demand, time-dependent |      |
| $ temp_{river} $     |      | temperature of river water |      |
| $ temp_{ww} $ |  | temperature of waste water |      |
| $ temp_{flow} $ |  | flow temperature |      |
| $ temp_{return} $ |  | return temperature |      |
| $ temp_{ambient} $ |  | ambient temperature |      |
| $ radiation $ |      | solar radiation |             |
| $ max_{demand} $ |  | maximum demand |      |
| $ potential_{j} $ |  | potential of the heat generator *j* |      |
| $ pow_{{cap}_{j}} $ |  |      |      |
| $ radiation_{t} $ |  | radiation, time-dependent |      |
| $ IK_{j} $ |  |      |      |
| $ OP_{{fix}_{j}} $ |  |      |      |
| $ n_{{el}_{j}} $ |  | electrical efficiency of heat generator *j* |      |
| $ elPrice_{jt} $ |  | electricity price for heat generator *j* , time-dependent |      |
| $ P_{{min,el}_{chp}} $ |  | minimum electrical power of chp |      |
| $ Q_{{min,th}_{chp}} $ |  | minimum thermal energy of chp |      |
| $ ratio_{{P,max}_{FW}} $ |  | ratio of maximum power for FW |      |
| $ ratio_{P,max} $ |  | ratio of maximum power |      |
| $ mc_{jt} $ |  | | |
| $ n_{{th}_{jt}} $ |  | thermal efficiency of heat generator *j*, time-dependent | |
| $ hp_{{restrictionfactor}_{jt}} $ |  | restriction factor of heat pump of heat generator *j*, time-dependent | |
| $ nom_{{p}_{th,j}} $ |  | | |
| $ min_{{p}_{th,j}} $ |  | | |
| $ x_{{th}_{cap,j}} $ |  | | |
| $ lt_{j} $ |  | | |
| $ ec_{j} $ |  | | |
| $ ir $ |  | | |
| $ \alpha_{j} $ |  | | |
| $ load_{{cap}_{hs}} $ |  | load capacity of heat storage | |
| $ unload_{{cap}_{hs}} $ |  | unload capacity of heat storage | |
| $ n_{hs} $ |  | efficiency of heat storage | |
| $ loss_{hs} $ |  | losses of heat storage | |
| $ IK_{hs} $ |  | IK of heat storage | |
| $ cap_{hs} $ |  | capacity of heat storage                                     |  |
| $ c_{{ramp}_{chp}} $ |  | | |
| $ c_{{ramp}_{waste}} $ |  | | |
| $ c_{{coldstart}_{j}} $ |  | | |
| $ \alpha_{hs} $ |  | | |
| $ rf_{j} $ |  | | |
| $ rf_{tot} $ |  | | |
| $ OP_{{var}_{j}} $ |  | | |
| $ temperature_{t} $ |  | time-dependent temperature | |
| $ sale_{{electricityprice}_{jt}} $ |  | | |
| $ OP_{{fix}_{hs}} $ |  | | |
| $ mr_{j} $ |  | | |
| $ em_{j} $ |  | | |
| $ pco2 $ |  | $CO_2$ price | |
| $ cap_{{losse}_{hs}} $ |  | capacity losses of heat storages | |
| $ n_{{th}_{nom,jt}} $ |  | thermal, normative efficiency of heat generator *j*, time-dependent | |
| $ restricitionfactor_{th} $ |  | thermal restriction factor | |
| $ min_{{out}_{factor,j}} $ |  | minimum output factor of heat generator *j* | |


