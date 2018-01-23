# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 11:52:40 2018

@author: root
"""


from time import sleep

class SliceMaker(object):
  def __getitem__(self, item):
    return item


#TODO: Adapt to real data
    

    
def preprocessing(data, demand_f = 1, inv_flag = 0):  
    
    select = SliceMaker()     # [start1:stop1:step1, start2:stop2:step2, ...]
    select = select[:]   
    if type(select) == tuple:
        tec = []
        for s in select: 
            tec=tec+data["tec"][s]
    else:
        tec=data["tec"][select]
        
    j =         tec
    j_hp =      [key for key in tec if key in data["tec"][0:1]]
    j_pth =     [key for key in tec if key in data["tec"][1:2]]
    j_st =      [key for key in tec if key in data["tec"][2:3]]
    j_waste =   [key for key in tec if key in data["tec"][3:4]]
    j_chp =     [key for key in tec if key in data["tec"][4:5]]
    j_bp =      [key for key in tec if key in data["tec"][5:6]]
    j_wh =      [key for key in tec if key in data["tec"][6:9]]
    j_gt =      [key for key in tec if key in data["tec"][9:12]]
    j_hs =      ["Heat Storage"]
    
    #%% Parameter - TODO: depends on how the input data looks finally
    demand_th_t =           data["demand_th"]
    max_demad =             max(data["demand_th"].values())
    max_installed_caps =    sum([data["P_th_cap"][key] for key in tec])
    delta =                 max_demad*demand_f - max_installed_caps
    
    if (max_installed_caps <= max_demad*demand_f) and not inv_flag:
        print("The installed capacities are not enough to cover the load")
        if [key for key in tec if key in data["tec"][5:6]] == []:
            print("There ist no Peak Boiler that could be updated with additional capacity")
            return None
        print("Additional "+str(round(delta,2))+" MW will be installed to the Peak Boilers")
        print("PLease be aware, It can happen that the model can not be solved,")
        print("due to the limitations of the other technologies at certain times or certain conditions")
        sleep(5)
        
        for key in data["tec"][5:6]:   
            if key in tec:
                data["P_th_cap"][key] = data["P_th_cap"][key]  + delta
            
    radiation_t =           data["radiation"]
    IK_j =                  {key:data["IK"][key] for key in tec}
    OP_j =                  {key:data["OP"][key] for key in tec}
    n_el_j =                {key:data["n_el"][key] for key in tec}
    electricity_price_t =   data["electricity price"]
    P_min_el_chp =          0
    Q_min_th_chp =          0
    ratioPMaxFW =           450/700
    ratioPMax =             450/820
    mc_jt =                 {(key,t):data["mc"][key,t] for t in range(1,8760+1) for key in tec}
    n_th_j =                {key:data["n_th"][key] for key in tec}
    x_th_cap_j =            {key:data["P_th_cap"][key] for key in tec}
    x_el_cap_j =            {key:data["P_el_cap"][key] for key in tec}
    pot_j =                 {key:data["POT"][key] for key in tec}
    lt_j =                  {key:data["LT"][key] for key in tec}
    el_surcharge =          50  # Taxes for electricity price
    ir =                    data["IR"]  # interest Rate
    alpha_j =               {key:data["alpha"][key] for key in tec}
    
    
    load_cap_hs =           50 
    unload_cap_hs =         140
    n_hs =                  0.95
    loss_hs =               0.02
    IK_hs =                 30
    cap_hs =                10
    c_ramp_chp =            10
    c_ramp_waste =          100
    alpha_hs =              {"Heat Storage":data["heat_storage"]["alpha"]}


    args = (j, j_hp, j_pth, j_st, j_waste, j_chp, j_bp, j_wh, j_gt, j_hs, 
            demand_th_t, max_demad, radiation_t,IK_j, OP_j, n_el_j, 
            electricity_price_t, P_min_el_chp, Q_min_th_chp,
            ratioPMaxFW, ratioPMax, mc_jt, n_th_j, x_th_cap_j, x_el_cap_j, 
            pot_j, lt_j, el_surcharge, ir, alpha_j, load_cap_hs, unload_cap_hs,
            n_hs, loss_hs, IK_hs, cap_hs, c_ramp_chp, c_ramp_waste, alpha_hs)
    
    return args






