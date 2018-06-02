# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import json
import numpy as np
import pandas as pd
import copy
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))

path2solution = path+r"\AD\F16_input\Solution" 

def save_sol_to_json (instance,results,inv_flag,path2solution = path2solution):
    try:
        if os.path.isdir(path2solution) ==False:
            print("Create Solution Dictionary")
            os.mkdir(path2solution)
        print("Saving Solver Output ....")
        
        
        c_inv={}
        c_op_fix={}
        c_op_var={}
        c_var={}
        c_peak_el={}
        c_ramp={}
        c_tot={}
        rev_tot={}
        c_final={}
        
        c_inv_stock = {j:instance.x_th_cap_j[j] * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j}
        c_inv = {j:(instance.Cap_j[j]() - instance.x_th_cap_j[j])  * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j}
        c_op_fix = {j:instance.Cap_j[j]() * instance.OP_fix_j[j] for j in instance.j}
        if inv_flag:
            c_op_fix = {j:(instance.Cap_j[j]()+instance.x_th_cap_j[j]) * instance.OP_fix_j[j] for j in instance.j}
        c_op_var = {j:sum(instance.x_th_jt[j,t]()* instance.OP_var_j[j]  for t in instance.t) for j in instance.j}
        c_var= {j:sum(instance.mc_jt[j,t] * instance.x_th_jt[j,t]() for t in instance.t) for j in instance.j if j not in instance.j_chp}  # 
        sv_chp = (instance.ratioPMaxFW - instance.ratioPMax) / (instance.ratioPMax*instance.ratioPMaxFW)
        for j in instance.j_chp:
            c_var[j] = sum(instance.mc_jt[j,t] *(instance.x_el_jt[j,t]() + sv_chp * instance.x_th_jt[j,t]())/ instance.n_el_j[j] for t in instance.t)
        c_peak_el = instance.P_el_max()*10000  
        c_ramp = {j:sum(instance.ramp_j_waste_t[j,t]() * instance.c_ramp_waste for t in instance.t) for j in instance.j_waste}
        for j in instance.j_chp:
            c_ramp[j] = sum(instance.ramp_j_chp_t[j,t]() * instance.c_ramp_chp for t in instance.t)
        rev_tot = {j:sum(instance.x_el_jt[j,t]()*instance.sale_electricity_price_t[t] for t in instance.t) for j in instance.j}
        
        c_tot_inv = instance.cost() + sum ([c_inv_stock[j]  for j in instance.j])
        c_tot = sum(c_var.values())
        c_tot = sum(c_inv.values()) + sum(c_var.values()) + sum(c_op_fix.values()) + sum(c_op_var.values()) + c_peak_el + sum(c_ramp.values())

        
        solution={ "Thermal Power Energymix":{j:[instance.x_th_jt[(j,t)]() for t in instance.t] for j in instance.j},
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
                  "Thermal Generation Mix":{j:sum([instance.x_th_jt[(j,t)]() for t in instance.t]) for j in instance.j}
                  } 
    
        solution["Ramping Costs"] = c_ramp
        solution["Revenue From Electricity"] = rev_tot
        solution["Heat Demand"] = [instance.demand_th_t[t] for t in instance.t]
        solution["Electricity Price"] = [instance.electricity_price_t[t] for t in instance.t]          
        solution["Mean Value Heat Price"] = np.mean(np.array(solution["Heat Price"])) 
        solution["Mean Value Heat Price (with costs of existing power plants)"] =  c_tot_inv/sum([instance.demand_th_t[t] for t in instance.t])
        solution["Median Value Heat Price"] = np.median(np.array(solution["Heat Price"]))          
        solution["Operational Cost"]= {j:(instance.Cap_j[j]() * instance.OP_fix_j[j] + sum(instance.x_th_jt[j,t]() * instance.OP_var_j[j]for t in instance.t))for j in instance.j}
        sv_chp = (instance.ratioPMaxFW - instance.ratioPMax) / (instance.ratioPMax*instance.ratioPMaxFW)
        solution["Variable Cost CHP's"]= sum([instance.mc_jt[j,t] *(instance.x_el_jt[j,t]() + sv_chp * instance.x_th_jt[j,t]())/ instance.n_el_j[j] for j in instance.j_chp for t in instance.t])
        solution["Fuel Costs"] = {j:sum([instance.mc_jt[j,t] * instance.x_th_jt[j,t]() for t in instance.t]) for j in instance.j}
        for j in instance.j_chp:
            solution["Fuel Costs"][j] = sum(instance.mc_jt[j,t] *(instance.x_el_jt[j,t]() + sv_chp * instance.x_th_jt[j,t]())/ instance.n_el_j[j]  for t in instance.t)
        
        del sv_chp 
        solution["Anual Total Costs"] = instance.cost()
        solution["Anual Total Costs (with costs of existing power plants)"] = c_tot_inv
         
        solution["Anual Investment Cost"] =  {j:0 for j in instance.j} 
        solution["Anual Investment Cost Heat Storage"] = {hs:0 for hs in instance.j_hs} 
        if inv_flag:
            solution["Anual Investment Cost"] = {j:(instance.Cap_j[j]() - instance.x_th_cap_j[j])  * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j}
            solution["Anual Investment Cost Heat Storage"] = {hs:instance.Cap_hs[hs]()  * instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in instance.j_hs}

        solution["Anual Investment Cost (of existing power plants)"] = c_inv_stock
        solution["Anual Investment Cost (of existing heat storages)"] = {hs:instance.cap_hs[hs] * instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in instance.j_hs}
        solution["Anual Investment Cost (of existing power plants and heat storages)"]={**solution["Anual Investment Cost (of existing power plants)"],
                 **solution["Anual Investment Cost (of existing heat storages)"],
                 }
        solution["Anual Total Costs (with costs of existing power plants and heat storages)"] = \
            solution["Anual Total Costs (with costs of existing power plants)"] + \
            sum(solution["Anual Investment Cost (of existing heat storages)"].values())
        
        solution["Mean Value Heat Price (with costs of existing power plants and heat storages)"] = solution["Anual Total Costs (with costs of existing power plants and heat storages)"] / sum([instance.demand_th_t[t] for t in instance.t])
        
        solution["Electrical Peak Load Costs"] = instance.P_el_max()*10000
        solution["Specific Capital Costs of installed Capacities"] = {j:instance.IK_j[j] * instance.alpha_j[j] for j in solution["Installed Capacities"].keys() if solution["Installed Capacities"][j] !=0 }
        solution["Technologies"] = [j for j in instance.j]
        solution["Marginal Costs"] = [np.mean([instance.mc_jt[j,t] for t in instance.t]) for j in instance.j] 
        
        solution["State of Charge"] = {hs:[instance.store_level_hs_t[hs,t]() for t in instance.t] for hs in instance.j_hs}
        
        solution["HS-Capacities"] = {hs:instance.Cap_hs[hs]()+instance.cap_hs[hs] if instance.Cap_hs[hs]() != None else instance.cap_hs[hs] for hs in instance.j_hs }

        solution["Unloading Heat Storage"] =  {hs:[instance.x_unload_hs_t[hs,t]() for t in instance.t] for hs in instance.j_hs}  
        solution["Loading Heat Storage"] =  {hs:[instance.x_load_hs_t[hs,t]() for t in instance.t] for hs in instance.j_hs}  
        solution["Heat Storage Technologies"] = list(instance.j_hs.value)
        solution["Unloading Heat Storage over year"] =  {hs:sum([instance.x_unload_hs_t[hs,t]() for t in instance.t]) for hs in instance.j_hs}  
        solution["Revenue from Heat Storages"]  = {hs:0 for hs in instance.j_hs} 
        solution["Operational Cost of Heat Storages"]= {hs:solution["HS-Capacities"][hs] * instance.OP_fix_hs[hs] + sum(instance.x_load_hs_t[hs,t]() * instance.electricity_price_t[t] for t in instance.t) for hs in instance.j_hs }
        solution["Specific Capital Costs of installed Heat Storages"] = {hs:instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in solution["HS-Capacities"].keys() if solution["HS-Capacities"][hs] !=0 }
        solution["Fuel Costs Heat Storages"] = {hs:0 for hs in instance.j_hs}  
#XXX: needed?        
        solution["Technologies:"] =  solution["Technologies"] + solution["Heat Storage Technologies"]
        
        solution["Thermal Power Energymix:"] = {**solution["Thermal Power Energymix"], 
                                        **solution["Unloading Heat Storage"]}

        solution["Installed Capacities:"] ={**solution["Installed Capacities"], 
                                        **solution["HS-Capacities"]} 
        
        solution["Thermal Generation Mix:"] = {**solution["Thermal Generation Mix"], 
                                        **solution["Unloading Heat Storage over year"]}  
        
        solution["Marginal Costs:"] = solution["Marginal Costs"]+[1e100]*len(solution["Heat Storage Technologies"])
        
        solution["Anual Investment Cost:"] =  {**solution["Anual Investment Cost"],
        **solution["Anual Investment Cost Heat Storage"]} 
        
        solution["Revenue From Electricity:"] = {**solution["Revenue From Electricity"],
                **solution["Revenue from Heat Storages"]}
 
                
        
        solution["Operational Cost:"] = {**solution["Operational Cost"],
                **solution["Operational Cost of Heat Storages"]}
        
        solution["Specific Capital Costs of Installed Capacities:"] = {**solution["Specific Capital Costs of installed Capacities"],
                **solution["Specific Capital Costs of installed Heat Storages"]}
        solution["Fuel Costs:"] = {**solution["Fuel Costs"], 
                **solution["Fuel Costs Heat Storages"]} 
        solution["all_heat_geneartors"] = list(instance.all_heat_geneartors.value)
        
        # only sum effective energy -> producton of solar thermal over  heat 
        # demand is not shown in the Thermal Generation mix
        
        matrix = pd.DataFrame(solution["Thermal Power Energymix:"]).values
        sum_matrix = matrix.sum(1)
        demand = solution["Heat Demand"]
        
        dif = sum_matrix - demand
        mask = sum_matrix > demand
        reduce = mask*dif
        
        _dic = copy.deepcopy(solution)
        try:
            for j in instance.j_st:
                _dic["Thermal Power Energymix:"][j] = list(np.array(solution["Thermal Power Energymix:"][j]) - reduce)
                solution["Thermal Generation Mix:"]  = pd.DataFrame(_dic["Thermal Power Energymix:"]).sum().to_dict()
        except:
            pass

        
        with open(path2solution+r"\solution.json", "w") as f:
            json.dump(solution, f)
            
        print("Done ! ,\nsaved to: <"+path2solution+r"\solution.json> ...") 
        return solution
    except:
        return "Error3"


    