# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:52:40 2018

@author: root
"""
from time import sleep
import numpy as np

class SliceMaker(object):
  def __getitem__(self, item):
    return item

#TODO: Adapt to real data
def preprocessing(data, demand_f = 1, inv_flag = 0):  
    
    if inv_flag:
        select = SliceMaker()     
        select = select[:]          # [start1:stop1:step1, start2:stop2:step2, ...]
        if type(select) == tuple:
            tec = []
            for s in select: 
                tec=tec+data["tec"][s]
        else:
            tec=data["tec"][select]
    else:
        selection = np.array(list(data["P_th_cap"].values())).nonzero()[0].tolist()
        if not selection:
            print("No Capacities installed !!!")
            return "Error1"
        tec = []
        for s in selection: 
            tec.append(data["tec"][s])
#TODO: assign to catagories

    
    
    j =         tec
    j_hp =      [key for key in tec if "heat pump" in key ]
    j_pth =     [key for key in tec if "Power To Heat" in key]
    j_st =      [key for key in tec if "Solar Thermal" in key]
    j_waste =   [key for key in tec if "waste" in key]
    j_chp =     [key for key in tec if "CHP" in key]
    j_bp =      [key for key in tec if "boiler" in key]
    j_wh =      [key for key in tec if "Waste Heat" in key]
    j_gt =      [key for key in tec if "Geothermal" in key]
    j_hs =      ["Heat Storage"]
    

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
#        if [key for key in tec if key in data["tec"][5:6]] == []:
#            print("There ist no Peak Boiler that could be updated with additional capacity")
#            return None
#        print("Additional "+str(round(delta,2))+" MW will be installed to the Peak Boilers")
#        print("PLease be aware, It can happen that the model can not be solved,")
#        print("due to the limitations of  other technologies at certain hours or due to certain technology conditions")
#        sleep(5)
#        
#        for key in data["tec"][5:6]:   
#            if key in tec:
#                data["P_th_cap"][key] = data["P_th_cap"][key]  + delta
      
    radiation_t =           data["radiation"]
    IK_j =                  {key:data["IK"][key] for key in tec}
    OP_fix_j =                  {key:data["OP_fix"][key] for key in tec}
    OP_var_j =                  {key:data["OP_var"][key] for key in tec}
    n_el_j =                {key:data["n_el"][key] for key in tec}
    electricity_price_t =   data["energy_carrier_prices"]["electricity"]
    P_min_el_chp =          0
    Q_min_th_chp =          0
    ratioPMaxFW =           450/700
    ratioPMax =             450/820

#XXX: Calculate MC with electricity price from user               
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

   
    mc_jt =                 {(key,t):mc[key,t] for t in range(1,8760+1) for key in tec}
    n_th_j =                {key:data["n_th"][key] for key in tec}
    x_th_cap_j =            {key:data["P_th_cap"][key] for key in tec}
    x_el_cap_j =            {key:data["P_el_cap"][key] for key in tec}
    pot_j =                 {key:data["POT"][key] for key in tec}
    lt_j =                  {key:data["LT"][key] for key in tec}
    el_surcharge =          50  # Taxes for electricity price

#TODO: Calculate alpha with interest rate from user , 
#      LT complete Data...     
    ir = data["interest_rate"]  # interest Rate
    q = 1+ir
    alpha = {}
    for ix,val in data["LT"].items():
        if val == 0 or val != val:
            alpha[ix] = 1
        else:
            alpha[ix] =  ( q**val * ir) / ( q**val - 1)
                  
    alpha_j =               {key:alpha[key] for key in tec}
    

    load_cap_hs =           50 
    unload_cap_hs =         140
    n_hs =                  0.95
    loss_hs =               0.02
    IK_hs =                 30
    cap_hs =                10
    c_ramp_chp =            100
    c_ramp_waste =          100
    alpha_hs =              {"Heat Storage":0}

    rf_j = {key:data["RF"][key] for key in tec}
    rf_tot = data["toatl_RF"]

    temperature = []
    for idx,val in data["temp"].items():
        temperature.append([val]*24)

    temperature = dict(zip(range(1,8760+1),sum(temperature,[])))   

    thresh = data["threshold_heatpump"]

    args = (tec, j_hp, j_pth, j_st, j_waste, j_chp, j_bp, j_wh, j_gt, j_hs, 
            demand_th_t, max_demad, radiation_t,IK_j, OP_fix_j, n_el_j, 
            electricity_price_t, P_min_el_chp, Q_min_th_chp,
            ratioPMaxFW, ratioPMax, mc_jt, n_th_j, x_th_cap_j, x_el_cap_j, 
            pot_j, lt_j, el_surcharge, ir, alpha_j, load_cap_hs, unload_cap_hs,
            n_hs, loss_hs, IK_hs, cap_hs, c_ramp_chp, c_ramp_waste, alpha_hs,
            rf_j,rf_tot,OP_var_j,temperature,thresh)
    
    return args