# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import json
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))

path2solution = path+r"\AD\F16_input\Solution" 

def save_sol_to_json (instance,results,inv_flag,path2solution = path2solution):
      
    if os.path.isdir(path2solution) ==False:
        print("Create Solution Dictionary")
        os.mkdir(path2solution)
    print("Saving Solver Output ....")
       
    solution={"Thermal Power Energymix":{j:[instance.x_th_jt[(j,t)]() for t in instance.t] for j in instance.j},
              "Installed Capacities": {j:instance.Cap_j[j]() for j in instance.j},
              "Heat Price": [results.solution(0).constraint["genearation_covers_demand_t["+str(t)+"]"]["Dual"] for t in instance.t],
              "Electricity Production by CHP" : sum([instance.x_el_jt[(j,t)]() for j in instance.j_chp for t in instance.t]),
              "Thermal Production by CHP" : sum([instance.x_th_jt[(j,t)]() for j in instance.j_chp for t in instance.t]),
              "Electrical Consumption of Heatpumps and Power to Heat devices" : \
                                   sum([instance.x_th_jt[(j,t)]() / instance.n_th_j[j] for j in instance.j_hp for t in instance.t])+\
                                   sum([instance.x_th_jt[(j,t)]() / instance.n_th_j[j] for j in instance.j_pth for t in instance.t]),
              "Maximum Electrical Load of Heatpumps and Power to Heat devices" : \
                                   max([max(np.array([instance.x_th_jt[(j,t)]() / instance.n_th_j[j] for j in instance.j_hp for t in instance.t]),default=0),
                                      max(np.array([instance.x_th_jt[(j,t)]() / instance.n_th_j[j] for j in instance.j_pth for t in instance.t]),default=0)]),
              "Thermal Generation Mix":{j:sum([instance.x_th_jt[(j,t)]() for t in instance.t]) for j in instance.j},                          
              "Revenue From Electricity": sum([instance.x_el_jt[j,t]()*(instance.electricity_price_t[t]) for j in instance.j for t in instance.t]),
              "Ramping Costs": sum ([instance.ramp_j_waste_t[j,t]() * instance.c_ramp_waste for j in instance.j_waste for t in instance.t]) + sum ([instance.ramp_j_chp_t[j,t]() * instance.c_ramp_chp for j in instance.j_chp for t in instance.t])

#              "Total Heat Generation Costs":c_tot
#             "Specific Heat Generation Costs":c_tot
             
#              "Eletrical Power Energymix (CHP's)":{j:[instance.x_el_jt[(j,t)]() for t in instance.t] for j in instance.j_chp},
#               "Heat Storage Level": {k:[instance.store_level_hs_t[(k,t)]() for t in instance.t] for k in instance.j_hs},
#               "Load Heat Storage Level": {k:[instance.x_load_hs_t[(k,t)]() for t in instance.t] for k in instance.j_hs},
#               "Unload Heat Storage Level": {k:[instance.x_unload_hs_t[(k,t)]() for t in instance.t] for k in instance.j_hs},
#               "Cogeneration Ramping": {j:[instance.ramp_j_chp_t[(j,t)]() for t in instance.t] for j in instance.j_chp},
#              "Waste Incineration Ramping": {j:[instance.ramp_j_mv_t[(j,t)]() for t in instance.t] for j in instance.j_mv},
#              "Installed Capacities of Heat Storages": {k:instance.Cap_hs[k]() for k in instance.j_hs},
#              "Maximum Electrical Power": instance.P_el_max(),
#              "Investment Costs":sum([instance.Cap_j[j]() * instance.IK_j[j] for j in instance.j]),
#              "Variable Costs": sum([instance.mc_jt[j,t] * instance.x_th_jt[j,t]() for j in instance.j for t in instance.t  if j not in instance.j_chp]) + sum([(instance.x_el_jt[j,t]() + ((instance.ratioPMaxFW - instance.ratioPMax) \
#                                     / (instance.ratioPMax * instance.ratioPMaxFW)) * instance.x_th_jt[j,t]())/ instance.n_el_j[j] for j in instance.j_chp for t in instance.t]),
#              "Revenue from Waste incineration": sum([instance.x_th_jt[j,t]() * instance.electricity_price_t[t] for j in instance.j_mv for t in instance.t]),
#              "Revenue from CHPs": sum([instance.x_el_jt[j,t]() * instance.electricity_price_t[t] for j in instance.j_chp for t in instance.t]),  
            }
    solution["Heat Demand"] = [instance.demand_th_t[t] for t in instance.t]
    solution["Electricity Price"] = [instance.electricity_price_t[t] for t in instance.t]          
    solution["Mean Value Heat Price"] = np.mean(np.array(solution["Heat Price"]))        
    solution["Median Value Heat Price"] = np.median(np.array(solution["Heat Price"]))          
    
    solution["Operational Cost"]= sum([instance.Cap_j[j]() * instance.OP_fix_j[j] for j in instance.j]) 
    solution["Operational Cost"]= solution["Operational Cost"] + \
    sum([instance.x_th_jt[j,t]() * instance.OP_var_j[j] for j in instance.j for t in instance.t]) 
    sv_chp = (instance.ratioPMaxFW - instance.ratioPMax) / (instance.ratioPMax*instance.ratioPMaxFW)
    solution["Variable Cost CHP's"]= sum([instance.mc_jt[j,t] *(instance.x_el_jt[j,t]() + sv_chp * instance.x_th_jt[j,t]())/ instance.n_el_j[j] for j in instance.j_chp for t in instance.t])
    del sv_chp 
    solution["Total Variable Cost"] = sum([instance.mc_jt[j,t] * instance.x_th_jt[j,t]() for j in instance.j for t in instance.t  if j not in instance.j_chp])+solution["Variable Cost CHP's"]
    solution["Total Costs"] = instance.cost()
    if inv_flag:
        solution["Invesment Cost"] = sum([(instance.Cap_j[j]() - instance.x_th_cap_j[j])  * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j]) + sum([instance.Cap_hs[hs]()*instance.IK_hs[hs]* instance.alpha_hs[hs] for hs in instance.j_hs])
    else:
        solution["Invesment Cost"] = 0                                                                                             
    
    solution["Electrical Peak Load Costs"] = instance.P_el_max()*10000
    solution["Specific Capital Costs of installed Capacities"] = {j:instance.IK_j[j] * instance.alpha_j[j] for j in solution["Installed Capacities"].keys() if solution["Installed Capacities"][j] !=0 }
    solution["Technologies"] = [j for j in instance.j]
    solution["Marginal Costs"] = [np.mean([instance.mc_jt[j,t] for t in instance.t]) for j in instance.j] 
    
    with open(path2solution+r"\solution.json", "w") as f:
        json.dump(solution, f)
        
    print("Done ! ,\nsaved to: <"+path2solution+r"\solution.json> ...") 
    
    return solution

