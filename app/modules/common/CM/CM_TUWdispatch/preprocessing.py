# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:52:40 2018

@author: root
"""
import numpy as np

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
            return "Error1"
        tec = []
        for s in selection_nonzero: 
            tec.append(data["tec"][s])
            
        selection_nonzero = np.nonzero(list(data["cap_hs"].values()))[0].tolist() 
        tec_hs = []
        for s in selection_nonzero: 
            tec_hs.append(data["tec_hs"][s])
        
        
    j =         tec
    j_hp =      [key for key in tec if "heat pump" in key ]
    j_pth =     [key for key in tec if "Power To Heat" in key]
    j_st =      [key for key in tec if "Solar Thermal" in key]
    j_waste =   [key for key in tec if "waste" in key]
    j_chp =     [key for key in tec if "CHP" in key]
    j_bp =      [key for key in tec if "boiler" in key]
    j_wh =      [key for key in tec if "Waste Heat" in key]
    j_gt =      [key for key in tec if "Geo Thermal" in key]
    j_hs =      tec_hs

    #%% Parameter - #TODO: depends on how the input data looks finally
    demand_th_t =           data["demand_th"]
    
    max_demad =             max(data["demand_th"].values())
    max_installed_caps =    sum([data["P_th_cap"][key] for key in tec])
    delta =                 max_demad*demand_f - max_installed_caps
    #XXX: 
    delta = 5*delta
    if (max_installed_caps <= max_demad*demand_f) and not inv_flag:
        print("The installed capacities are not enough to cover the load")
        return "Error2"

    radiation_t =           data["radiation"]
    IK_j =                  {key:data["IK"][key] for key in tec}
    OP_fix_j =              {key:data["OP_fix"][key] for key in tec}
    OP_var_j =              {key:data["OP_var"][key] for key in tec}
    n_el_j =                {key:data["n_el"][key] for key in tec}
    electricity_price_t =   data["energy_carrier_prices"]["electricity"]
    try:
        sale_electricity_price_t =   data["sale_electricity"]
    except:
        sale_electricity_price_t =   data["energy_carrier_prices"]["electricity"]
        
    P_min_el_chp =          0
    Q_min_th_chp =          0
    ratioPMaxFW =           450/700
    ratioPMax =             450/820
           
    mc = {}
    for j in data["tec"]:
        if data["n_th"][j]  == 0:
            for t in range(1,8760+1):
                mc[j,t]= 1e100   
        else:
            if type(data["energy_carrier_prices"][data["energy_carrier"][j]]) == dict:  # Boiler Peak Load
                for t in range(1,8760+1):
                    mc[j,t]= data["energy_carrier_prices"][data["energy_carrier"][j]][t] /  \
                                  data["n_th"][j] + \
                                 data["em"][data["energy_carrier"][j]]*data["P_co2"] / \
                                  data["n_th"][j] 
            else:
                for t in range(1,8760+1):
                    mc[j,t]= data["energy_carrier_prices"][data["energy_carrier"][j]] /  \
                                data["n_th"][j] + \
                                 data["em"][data["energy_carrier"][j]]*data["P_co2"] / \
                                  data["n_th"][j]   
   
    print("Here") 
       
    mc_jt =                 {(key,t):mc[key,t] for t in range(1,8760+1) for key in tec}
    print("Here2") 
    n_th_j =                {key:data["n_th"][key] for key in tec}
    x_th_cap_j =            {key:data["P_th_cap"][key] for key in tec}
#    x_el_cap_j =            {key:data["P_el_cap"][key] for key in tec}
    x_el_cap_j = None
#    pot_j =                 {key:data["POT"][key] for key in tec}
    pot_j = None
    lt_j =                  {key:data["LT"][key] for key in tec}
    el_surcharge =          50  # Taxes for electricity price
    print("Here3") 
       
    ir = data["interest_rate"]  # interest Rate
    q = 1+ir
    alpha = {}
    for ix,val in data["LT"].items():
        if val == 0 or val != val:
            alpha[ix] = 1
        else:
            alpha[ix] =  ( q**val * ir) / ( q**val - 1)
    print("Here4")              
    alpha_j =               {key:alpha[key] for key in tec}
    
    # Heat Storage
    load_cap_hs =           {hs: data["load_cap_hs"][hs] for hs in j_hs}
    unload_cap_hs =         {hs: data["unload_cap_hs"][hs] for hs in j_hs}
    n_hs =                  {hs: data["n_pump_hs"][hs] for hs in j_hs}
    loss_hs =               {hs: data["n_turb_hs"][hs] for hs in j_hs}
    IK_hs =                 {hs: data["IK_cap_hs"][hs] for hs in j_hs}
    cap_hs =                {hs: data["cap_hs"][hs] for hs in j_hs}
    OP_fix_hs =             {hs: data["OP_fix_hs"][hs] for hs in j_hs}
        
    ir =    	              data["interest_rate"]  
    q =                     1+ir
    alpha_hs =              {hs: ( q**data["LT_hs"][hs] * ir) / \
                             ( q**data["LT_hs"][hs] - 1)  for hs in j_hs}
    
    
    # Ramping Costs
    c_ramp_chp =            100
    c_ramp_waste =          100
    print("Here5") 
    rf_j =                  {key:data["RF"][key] for key in tec}
    rf_tot =                data["toatl_RF"]

    temperature = data["temp"]

    thresh = data["threshold_heatpump"]
    all_heat_geneartors = data["all_heat_geneartors"] 
 
    mr_j = {key:data["MR"][key] for key in tec}

    args = (tec, j_hp, j_pth, j_st, j_waste, j_chp, j_bp, j_wh, j_gt, j_hs, 
            demand_th_t, max_demad, radiation_t,IK_j, OP_fix_j, n_el_j, 
            electricity_price_t, P_min_el_chp, Q_min_th_chp,
            ratioPMaxFW, ratioPMax, mc_jt, n_th_j, x_th_cap_j, x_el_cap_j, 
            pot_j, lt_j, el_surcharge, ir, alpha_j, load_cap_hs, unload_cap_hs,
            n_hs, loss_hs, IK_hs, cap_hs, c_ramp_chp, c_ramp_waste, alpha_hs,
            rf_j,rf_tot,OP_var_j,temperature,thresh,sale_electricity_price_t,
            OP_fix_hs,all_heat_geneartors, mr_j)
    
    return args