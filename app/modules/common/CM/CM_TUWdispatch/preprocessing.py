# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:52:40 2018

@author: root
"""
import numpy as np
import pprint
class SliceMaker(object):
  def __getitem__(self, item):
    return item

#XXX: Catogorize
def preprocessing(data, demand_f = 1, inv_flag = 0,selection=[[],[]]):
    if inv_flag:
        tec = []
        for s in selection[0]:
            tec.append(data["tec"][s])
        tec_hs =      [ data["tec_hs"][s] for s in selection[1] ]

    else:
        selection_nonzero = np.nonzero(list(data["P_th_cap"].values()))[0].tolist()
        if not selection_nonzero:
            print("No Capacities installed !!!")
            return "Error1",None
        tec = []
        for s in selection_nonzero:
            tec.append(data["tec"][s])

        selection_nonzero = np.nonzero(list(data["cap_hs"].values()))[0].tolist()
        tec_hs = []
        for s in selection_nonzero:
            tec_hs.append(data["tec_hs"][s])


    j =         tec
    j_hp =      [key for key in tec if key in data["categorize"]["heat pump"] ]
    j_pth =     [key for key in tec if key in data["categorize"]["Power To Heat"] ]
    j_st =      [key for key in tec if key in data["categorize"]["Solar Thermal"] ]
    j_waste =   [key for key in tec if key in data["categorize"]["waste treatment"] ]
    j_chp_bp =  [key for key in tec if key in data["categorize"]["CHP-BP"] ]
    j_chp_se =  [key for key in tec if key in data["categorize"]["CHP-SE"] ]
    j_chp =     j_chp_bp + j_chp_se
    j_bp =      [key for key in tec if key in data["categorize"]["boiler"] ]
    j_wh =      [key for key in tec if key in data["categorize"]["Waste Heat"] ]
    j_gt =      [key for key in tec if key in data["categorize"]["Geo Thermal"] ]
    j_air_heat_pump =   [key for key in tec if key in data["categorize"]["Heat Pump Air"] ]
    j_river_heat_pump = [key for key in tec if key in data["categorize"]["Heat Pump River Water"] ]
    j_wastewater_heat_pump = [key for key in tec if key in data["categorize"]["Heat Pump Wastewater"] ]
    j_wasteheat_heat_pump = [key for key in tec if key in data["categorize"]["Heat Pump Ind. Wasteheat"] ]
    j_hs =      tec_hs
    j_hp_new =  j_air_heat_pump + j_river_heat_pump + j_wastewater_heat_pump + j_wasteheat_heat_pump

    #%% Parameter - #TODO: depends on how the input data looks finally

    demand_th_t =           data["demand_th"]
    
    temp_river = data["river_temp"]
    temp_waste_water = data["wastewater_temp"]
    temp_flow = data["inlet_temp"]
    temp_return = data["return_temp"]
    temp_ambient = data["temp"]
    radiation = data["radiation"]
  
    max_demad =             max(data["demand_th"].values())
    max_installed_caps =    sum([data["P_th_cap"][key] for key in tec])
    max_installed_caps +=    sum([data["unload_cap_hs"][key] for key in j_hs])
    print(max_installed_caps)
    print(max_demad)
    delta =                 max_demad*demand_f - max_installed_caps
    #XXX:
    if (max_installed_caps <= max_demad*demand_f) and not inv_flag:
        print("The installed capacities are not enough to cover the load")
        print(f"need extra {delta} MW to cover demand")
        return "Error2",f"need extra {round(delta,2)} MW to cover demand"

    
    #--------------Heat Pumps-------------------------------------------------- 
    #set minimum output power(for heat pumps this is overwritten with min comp power)
    min_p_th = {j: data["hp_compressor_power"][j] * data["output_power_min_factor"][j]  if j in j_hp_new else data["P_th_cap"][j]*data["output_power_min_factor"][j] for j in tec}
    min_out_factor_j = {j:data["output_power_min_factor"][j] for j in tec}
    # dict of numpy arrays
    source_temp_jt = {
        **{j:np.asarray(list(temp_ambient.values())) for j in j_air_heat_pump},
        **{j:np.asarray(list(temp_river.values())) for j in j_river_heat_pump},
        **{j:np.asarray(list(temp_waste_water.values())) for j in j_wastewater_heat_pump},
        **{j:np.full(8760, 0) for j in j_wasteheat_heat_pump},
        **{j:np.full(8760, 0) for j in tec if j not in j_hp_new}
        }
    nom_source_temp_j = {j:data["std_source_temp"].get(j,0) for j in tec}
    min_source_temp_j = {j:data["source_temp_min"].get(j,0) for j in tec}
    fade_out_source_temp_j = {j:data["source_temp_fadeout"].get(j,0) for j in tec}
    return_temp_jt = {j:np.asarray(list(temp_return.values())) for j in tec}
    nom_return_temp_j =  {j:data["std_return_temp"].get(j,0) for j in tec}
    flow_temp_jt = {j:np.asarray(list(temp_flow.values())) for j in tec}
    nom_flow_temp_j = {j:data["std_inlet_temp"].get(j,0) for j in tec}
    sens_source_j = {j:data["cop_source_sens"].get(j,0) for j in tec}
    sens_return_j = {j:data["cop_return_sens"].get(j,0) for j in tec}
    sens_flow_j = {j:data["cop_inlet_sens"].get(j,0) for j in tec}
    nominal_n_th_jt = {j:np.asarray([data["n_th"][j,t] for t in range(1,8760+1)])  for j in tec }
    
    n_th_nom_jt = {(j,t):nominal_n_th_jt[j][t-1] for t in range(1,8760+1)  for j in tec }
    restriction_factor =  {j: np.ones(8760) for j in tec }
 
    n_th_jt = {j:(source_temp_jt[j] - nom_source_temp_j[j]) * sens_source_j[j] + \
                 (return_temp_jt[j] - nom_return_temp_j[j]) * sens_return_j[j] + \
                 (flow_temp_jt[j] - nom_flow_temp_j[j]) * sens_flow_j[j] + \
                 nominal_n_th_jt[j] for j in tec}
  
    #division by zero protection
    for j in tec:
        time_of_low_efficiency = n_th_jt[j]<=0
        n_th_jt[j][time_of_low_efficiency] = 1e-3

    # restriciton factor for heat pumps
        shutdown_time = source_temp_jt[j]<min_source_temp_j[j]
        s = int(np.sum(shutdown_time))
        if s:
            restriction_factor[j][shutdown_time] = np.zeros(s)
        power_reduction_time = (min_source_temp_j[j]<=source_temp_jt[j]) & (source_temp_jt[j]<fade_out_source_temp_j[j])
        dx = fade_out_source_temp_j[j]-min_source_temp_j[j]
        dy = source_temp_jt[j][power_reduction_time]-min_source_temp_j[j]
        restriction_factor[j][power_reduction_time]  = dy/dx
        
    # when restriction factor smaller than power_min_factor set restriciton_factor to zero
        shutdown_time2 = restriction_factor[j] <= data["output_power_min_factor"][j]
        s2 = int(np.sum(shutdown_time2))
        if s2:
            restriction_factor[j][shutdown_time2] = np.zeros(s2)

    for j in tec:
        if data["MR"][j] * data["P_th_cap"][j] < min_p_th[j]:
            data["MR"][j] = 0


    #--------------------------------------------------------------------------

    potential_j =  {key:data["potential"][key] for key in tec}
    pow_cap_j = {key:data["pow_cap"][key] for key in tec}
    
    radiation_t =           data["radiation"]
    IK_j =                  {key:data["IK"][key] for key in tec}
    OP_fix_j =              {key:data["OP_fix"][key] for key in tec}
    OP_var_j =              {key:data["OP_var"][key] for key in tec}
    n_el_j =                {key:data["n_el"][key] for key in tec}
    electricity_price_jt =   {(key,t):data["energy_carrier_prices"]["electricity"][key,t] for t in range(1,8760+1) for key in tec}
    try:
        sale_electricity_price_jt =   {(key,t):data["sale_electricity"][key,t] for t in range(1,8760+1) for key in tec}
    except:
        sale_electricity_price_jt =   {(key,t):data["energy_carrier_prices"]["electricity"][key,t] for t in range(1,8760+1) for key in tec}


    P_min_el_chp =          0
    Q_min_th_chp =          0
    ratioPMaxFW =           450/700
    ratioPMax =             450/820

    mc = {}
    for j in tec:
        for t in range(1,8760+1):
            if n_th_jt[j][t-1]  == 0:
                    mc[j,t]= 1e100
            else:
                if type(data["energy_carrier_prices"][data["energy_carrier"][j]]) == dict:
                        mc[j,t]= data["energy_carrier_prices"][data["energy_carrier"][j]][j,t] /  \
                                      n_th_jt[j][t-1] + \
                                     data["em"][data["energy_carrier"][j]]*data["P_co2"] / \
                                      n_th_jt[j][t-1] + \
                                     data["excess_heat_source_price"][j] * (1 - 1/n_th_jt[j][t-1] )
                else:
                    mc[j,t]= data["energy_carrier_prices"][data["energy_carrier"][j]] /  \
                                    n_th_jt[j][t-1] + \
                                     data["em"][data["energy_carrier"][j]]*data["P_co2"] / \
                                      n_th_jt[j][t-1]+ \
                                          data["excess_heat_source_price"][j] * (1 - 1/n_th_jt[j][t-1] )
    pco2 =   data["P_co2"]                            
    mc_jt =                 {(key,t):mc[key,t] for t in range(1,8760+1) for key in tec}
    n_th_jt =                {(key,t):n_th_jt[key][t-1] for t in range(1,8760+1) for key in tec}
    hp_restriction_factor_jt = {(key,t):float(restriction_factor[key][t-1]) for t in range(1,8760+1) for key in j_hp_new} 
    restriction_factor_jt = {(key,t):float(restriction_factor[key][t-1]) for t in range(1,8760+1) for key in tec} 

    min_p_th_j =            {key:min_p_th[key] for key in tec}
    c_coldstart_j =         {key:data["c_coldstart"][key] for key in tec}
    x_th_cap_j =            {key:data["P_th_cap"][key]for key in tec}
    nom_p_th_j =            {key:data["P_th_cap"][key] for key in j_hp_new} #nominal thermal capacity is used in model to calculate OPEX fix
#    x_el_cap_j =            {key:data["P_el_cap"][key] for key in tec}
    x_el_cap_j = None #XXX: Not used
#    pot_j =                 {key:data["POT"][key] for key in tec}
    pot_j = None #XXX: Not used
    lt_j =                  {key:data["LT"][key] for key in tec}
    ec_j =                  {key:data["energy_carrier"][key] for key in tec}
    el_surcharge =          50  # Taxes for electricity price  #XXX: Not used


    ir = data["interest_rate"]  # interest Rate
    q = 1+ir
    alpha = {}
    for ix,val in data["LT"].items():
        if val == 0 or val != val:
            alpha[ix] = 1
        else:
            alpha[ix] =  ( q**val * ir) / ( q**val - 1)

    alpha_j =               {key:alpha[key] for key in tec}

    # Heat Storage
    load_cap_hs =           {hs: data["load_cap_hs"][hs] for hs in j_hs}
    unload_cap_hs =         {hs: data["unload_cap_hs"][hs] for hs in j_hs}
    n_hs =                  {hs: data["n_pump_hs"][hs] for hs in j_hs}
    loss_hs =               {hs: data["n_turb_hs"][hs] for hs in j_hs}
    IK_hs =                 {hs: data["IK_cap_hs"][hs] for hs in j_hs}
    cap_hs =                {hs: data["cap_hs"][hs] for hs in j_hs}
    OP_fix_hs =             {hs: data["OP_fix_hs"][hs] for hs in j_hs}
    cap_losse_hs =          {hs: data["cap_losse_hs"][hs]/100 for hs in j_hs}
    ir =    	              data["interest_rate"]
    q =                     1+ir
    alpha_hs =              {hs: ( q**data["LT_hs"][hs] * ir) / \
                             ( q**data["LT_hs"][hs] - 1)  for hs in j_hs}


    # Ramping Costs
    c_ramp_j =  {key:data["c_ramp"][key] for key in tec} 

    rf_j =                  {key:data["RF"][key] for key in tec}
    rf_tot =                data["toatl_RF"]

    temperature = data["temp"]

    thresh = data["threshold_heatpump"]
   

    all_heat_geneartors = tec+j_hs

    mr_j = {key:data["MR"][key] for key in tec}
    
    em_j = {j: data["em"][data["energy_carrier"][j]] for j in tec}
    
    args = [tec, j_hp, j_pth, j_st, j_waste, j_chp, j_bp, j_wh,
            j_gt, j_hs, demand_th_t, max_demad, radiation_t, IK_j,
            OP_fix_j, n_el_j, electricity_price_jt, P_min_el_chp,
            Q_min_th_chp, ratioPMaxFW, ratioPMax, mc_jt, n_th_jt,
            x_th_cap_j, x_el_cap_j, pot_j, lt_j, el_surcharge, ir,
            alpha_j, load_cap_hs, unload_cap_hs, n_hs, loss_hs,
            IK_hs, cap_hs, c_ramp_j, alpha_hs,
            rf_j, rf_tot, OP_var_j, temperature, thresh,
            sale_electricity_price_jt, OP_fix_hs, all_heat_geneartors,
            mr_j,j_chp_se,j_chp_bp,em_j,cap_losse_hs, j_air_heat_pump,
            j_river_heat_pump, j_wastewater_heat_pump, 
            j_wasteheat_heat_pump, hp_restriction_factor_jt, min_p_th_j, 
            nom_p_th_j, c_coldstart_j,potential_j,pco2,pow_cap_j,
            temp_river,temp_waste_water,temp_flow,temp_return,
            temp_ambient,radiation,j_hp_new,restriction_factor_jt,n_th_nom_jt,
            min_out_factor_j,ec_j]

    
    
    keys = ['j', 'j_hp', 'j_pth', 'j_st', 'j_waste', 'j_chp', 'j_bp', 'j_wh',
            'j_gt', 'j_hs', 'demand_th_t', 'max_demad', 'radiation_t', 'IK_j',
            'OP_fix_j', 'n_el_j', 'electricity_price_jt', 'P_min_el_chp',
            'Q_min_th_chp', 'ratioPMaxFW', 'ratioPMax', 'mc_jt', 'n_th_jt',
            'x_th_cap_j', 'x_el_cap_j', 'pot_j', 'lt_j', 'el_surcharge', 'ir',
            'alpha_j', 'load_cap_hs', 'unload_cap_hs', 'n_hs', 'loss_hs',
            'IK_hs', 'cap_hs', 'c_ramp_j', 'alpha_hs',
            'rf_j', 'rf_tot', 'OP_var_j', 'temperature_t', 'thresh',
            'sale_electricity_price_jt', 'OP_fix_hs', 'all_heat_geneartors',
            'mr_j' , 'j_chp_se' , 'j_chp_bp','em_j','cap_losse_hs' ,
            'j_air_heat_pump','j_river_heat_pump', 'j_wastewater_heat_pump',
             'j_wasteheat_heat_pump','hp_restriction_factor_jt','min_p_th_j',
             'nom_p_th_j','c_coldstart_j',"potential_j","pco2","pow_cap_j",
             'temp_river', 'temp_waste_water', 'temp_flow', 'temp_return', 
             'temp_ambient', 'radiation',"j_hp_new","restriction_factor_jt","n_th_nom_jt",
             "min_out_factor_j","ec_j"]
    
    data= dict(zip(keys,args))
    
#% reshape data to fit the pyomo data structure for abstract models
    pyomo_data = {}
    for key,value in data.items():
        if type(value) != dict:
            pyomo_data[key]={None:value}
        else:
            pyomo_data[key]=value
        
    pyomo_data = {None:pyomo_data}    

    # with open(r"C:\Users\hasani\Desktop\data.txt","a") as fp: 
    #     pprint.pprint("="*100,stream=fp)
    #     pprint.pprint(pyomo_data,stream=fp)
        
    return data,None