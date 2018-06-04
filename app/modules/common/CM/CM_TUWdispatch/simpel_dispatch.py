# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% Import needed modules
import pyomo.environ as pe
from datetime import datetime

import os 
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUWdispatch.preprocessing import preprocessing

#import logging
#logging.getLogger('pyomo.core').setLevel(logging.ERROR)
    
def run(data,inv_flag,selection=[[],[]],demand_f=1):
    #%% Creation of a  Model
    m = pe.AbstractModel()
    #%% Sets - TODO: depends on how the input data looks finally
    val = preprocessing(data,demand_f,inv_flag,selection)
        
    if val == "Error1" or val == "Error2":
        return (val,None)
    
    m.t = pe.RangeSet(1,8760)
    m.j = pe.Set(initialize = val[0])
    m.j_hp = pe.Set(initialize = val[1])
    m.j_pth = pe.Set(initialize = val[2])
    m.j_st = pe.Set(initialize = val[3])
    m.j_waste = pe.Set(initialize = val[4])
    m.j_chp = pe.Set(initialize = val[5])
    m.j_bp = pe.Set(initialize = val[6])
    m.j_wh = pe.Set(initialize = val[7])
    m.j_gt = pe.Set(initialize = val[8])
    m.j_hs = pe.Set(initialize = val[9])
    
    #%% Parameter - TODO: depends on how the input data looks finally
    m.demand_th_t = pe.Param(m.t,initialize = val[10])
    max_demad = val[11]
            
    m.radiation_t = pe.Param(m.t,initialize=val[12])
    m.IK_j = pe.Param(m.j,initialize=val[13]) 
    m.OP_fix_j = pe.Param(m.j,initialize=val[14]) 
    m.n_el_j = pe.Param(m.j ,initialize=val[15])
    m.electricity_price_t = pe.Param(m.t,initialize=val[16])
    m.P_min_el_chp = pe.Param(initialize=val[17])
    m.Q_min_th_chp = pe.Param(initialize=val[18])
    m.ratioPMaxFW = pe.Param(initialize=val[19])
    m.ratioPMax = pe.Param(initialize=val[20])
    m.mc_jt = pe.Param(m.j,m.t,initialize= val[21])
    m.n_th_j = pe.Param(m.j,initialize=val[22]) 
    m.x_th_cap_j = pe.Param(m.j,initialize=val[23]) 
    m.x_el_cap_j = pe.Param(m.j,initialize=val[24]) 
    m.pot_j = pe.Param(m.j,initialize=val[25]) 
    m.lt_j = pe.Param(m.j,initialize=val[26])
#    m.el_surcharge = pe.Param(m.j,initialize=val[27])  # Taxes for electricity price
    m.ir = pe.Param(initialize=val[28])
    m.alpha_j = pe.Param(m.j,initialize=val[29])
       
    m.load_cap_hs  = pe.Param(m.j_hs,initialize=val[30])   
    m.unload_cap_hs  = pe.Param(m.j_hs,initialize=val[31])
    m.n_hs = pe.Param(m.j_hs,initialize=val[32])
    m.loss_hs = pe.Param(m.j_hs,initialize=val[33])
    m.IK_hs = pe.Param(m.j_hs,initialize=val[34])
    m.cap_hs = pe.Param(m.j_hs,initialize=val[35])
    m.c_ramp_chp = pe.Param(initialize=val[36])
    m.c_ramp_waste = pe.Param(initialize=val[37])
    m.alpha_hs = pe.Param(m.j_hs,initialize=val[38])
    
    m.rf_j = pe.Param(m.j,initialize=val[39])
    m.rf_tot = pe.Param(initialize=val[40])
    m.OP_var_j = pe.Param(m.j,initialize=val[41])
    m.temperature_t = pe.Param(m.t,initialize=val[42])
    thresh =  val[43]
    
    m.sale_electricity_price_t = pe.Param(m.t,initialize=val[44])
    m.OP_fix_hs = pe.Param(m.j_hs,initialize=val[45]) 
    m.all_heat_geneartors = pe.Set(initialize = val[46])
    #%% Variablen
    m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)       
    m.x_el_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.P_el_max = pe.Var(within=pe.NonNegativeReals) 
    
    m.x_load_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.x_unload_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.Cap_hs = pe.Var(m.j_hs,within=pe.NonNegativeReals)
    m.store_level_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.binary_load_hs_t = pe.Var(m.j_hs,m.t,within=pe.Binary)
    m.binary_unload_hs_t = pe.Var(m.j_hs,m.t,within=pe.Binary)
    
    m.ramp_j_chp_t = pe.Var(m.j_chp, m.t,within=pe.NonNegativeReals)
    m.ramp_j_waste_t = pe.Var(m.j_waste, m.t,within=pe.NonNegativeReals)
    
    #%% Nebenbedingungen 
    
    #% electircal power generation
    def gen_el_jt_rule(m,j,t):
        if j not in m.j_chp and m.n_th_j[j] != 0:
            return m.x_el_jt[j,t] == m.x_th_jt[j,t] / m.n_th_j[j] * m.n_el_j[j]
        else:
            return pe.Constraint.Skip
    m.gen_el_jt = pe.Constraint(m.j,m.t,rule=gen_el_jt_rule)

    #%  At any time, the heating generation must cover the heating demand
    def genearation_covers_demand_t_rule(m,t): 
#        rule = sum([m.x_th_jt[j,t] for j in m.j]) >= demand_f * m.demand_th_t[t] 
        rule = sum([m.x_th_jt[j,t] for j in m.j]) + \
                sum([m.x_unload_hs_t[hs,t] for hs in m.j_hs])>= demand_f * m.demand_th_t[t] 
        return rule 
    m.genearation_covers_demand_t = pe.Constraint(m.t,rule=genearation_covers_demand_t_rule)  
    
    
    def capacity_restriction_max_j_rule (m,j):
        #% ToDo: Define upper bound
        if inv_flag:
            rule = m.Cap_j[j]  <= demand_f*max_demad
        else:
            rule = m.Cap_j[j] == m.x_th_cap_j[j]
        return rule 
    m.capacity_restriction_max_j = pe.Constraint(m.j,rule=capacity_restriction_max_j_rule)

    def capacity_restriction_min_j_rule (m,j):
        return m.Cap_j[j] >= m.x_th_cap_j[j] 
    m.capacity_restriction_min_j = pe.Constraint(m.j,rule=capacity_restriction_min_j_rule)
      
    #% The amount of heat energy generated must not exceed the installed capacities
    def generation_restriction_jt_rule(m,j,t): 
        rule = m.x_th_jt[j,t] <= m.Cap_j[j] 
        return rule 
    m.generation_restriction_jt = pe.Constraint(m.j,m.t,rule=generation_restriction_jt_rule)
    
    #% The solar gains depend on the installed capacity and the solar radiation
    def solar_restriction_jt_rule(m,j,t): 
        rule = m.x_th_jt[j,t] <=  m.Cap_j[j]*m.radiation_t[t]/1000 
        return rule
    m.solar_restriction_jt = pe.Constraint(m.j_st,m.t,rule=solar_restriction_jt_rule)
    
    #% No investment in waste incineration plants possible,thus geneartion cant exeed already installed capacities
    def waste_incineration_restriction_jt_rule(m,j,t): 
        rule = m.x_th_jt[j,t] <=  m.x_th_cap_j[j]
        return rule
    m.waste_incineration_restriction_jt = pe.Constraint(m.j_waste,m.t,rule=waste_incineration_restriction_jt_rule)
    
    #% Restriction for the Heat Pumps in the cold Seasion , temp_vec[t] < -grenz °C
    def heat_pump_restriction_jt_rule(m,j,t):
        if m.temperature_t[t] <= thresh:
            return m.x_th_jt[j,t] == 0
        else: 
#            return m.x_th_jt[j,t] ==  m.x_el_jt[j,t]*0.41*50/(50-m.temperature_t[t])
            return m.x_th_jt[j,t] <=  max_demad
    m.heat_pump_restriction_jt = pe.Constraint(m.j_hp,m.t,rule=heat_pump_restriction_jt_rule)  
    
    #% The electrical peak load at the winter time (from December to February) results from
    #% the sum of the power consumption of the power to heat systems and the heat pumps.
    def max_p_el_t_rule(m,t):
        if t in range(1,24*60+1) or t in range(8760-24*30, 8760+1):
            return m.P_el_max >= sum([m.x_th_jt[j,t] / m.n_th_j[j]  for j in m.j_hp]) + sum([m.x_th_jt[j,t] / m.n_th_j[j]  for j in m.j_pth]) 
        else: 
            return pe.Constraint.Skip
    m.max_p_el_t = pe.Constraint(m.t,rule=max_p_el_t_rule)  
    
    #% Restriction for the Powert to Heat - Define upper Limit
    def power_to_heat_restriction_jt_rule(m,j,t):
        return m.x_th_jt[j,t] <=  max_demad
    m.power_to_heat_restriction_jt = pe.Constraint(m.j_pth,m.t,rule=power_to_heat_restriction_jt_rule)  
    
    #% The maximum installed capacity for CHP plants is limited by the maximum heat demand.
    def chp_capacity_restriction_j_rule (m,j):
        rule = m.Cap_j[j] <= max_demad
        return rule 
    
    m.chp_capacity_restriction_j = pe.Constraint(m.j_chp,rule=chp_capacity_restriction_j_rule)
    
    #% With full heat extraction, a loss of power can occur which, only reduces the maximum power.
    def chp_geneartion_restriction1_jt_rule(m,j,t):
        sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
        rule = m.x_el_jt[j,t] <= m.Cap_j[j]/m.ratioPMax - sv_chp * m.x_th_jt[j,t]
        return rule 
#    m.chp_geneartion_restriction1_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction1_jt_rule)   # should be adopted using binary variables
    
    def chp_geneartion_restriction2_jt_rule(m,j,t):
        rule = m.P_min_el_chp <=  m.x_el_jt[j,t]
        return rule 
    m.chp_geneartion_restriction2_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction2_jt_rule) 
    
    #% The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling 
    #with the produced electrical net power.
    def chp_geneartion_restriction3_jt_rule(m,j,t):
#        rule = m.x_el_jt[j,t] >= m.x_th_jt[j,t] / m.ratioPMaxFW    # should be adopted using binary variables
        rule = m.x_el_jt[j,t] == m.x_th_jt[j,t] / m.ratioPMaxFW

        return rule 
    m.chp_geneartion_restriction3_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction3_jt_rule) 
    
    def load_or_unload_rule(m,hs,t):
        return m.binary_load_hs_t[hs,t] + m.binary_unload_hs_t[hs,t] == 1
    m.load_or_unload = pe.Constraint(m.j_hs,m.t,rule=load_or_unload_rule)
    
    # The heat storage level = old_level + pumping  - turbining
    def storage_state_hs_t_rule(m,hs,t):
        if t == 1:
            return m.store_level_hs_t[hs,t] == 0
        elif t == 8760:
            return m.store_level_hs_t[hs,t] == 0
        else:
            return m.store_level_hs_t[hs,t] == m.store_level_hs_t[hs,t-1] - m.x_unload_hs_t[hs,t]/m.loss_hs[hs] + m.x_load_hs_t[hs,t-1]*m.n_hs[hs] 
    m.storage_state_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_hs_t_rule) 
    
    # The storage_level is restricted by the installed capcities 
    def storage_state_capacity_restriction_hs_t_rule(m,hs,t):
        if inv_flag:
            return m.store_level_hs_t[hs,t] <= (m.Cap_hs[hs] - m.cap_hs[hs])
        else:
            return m.store_level_hs_t[hs,t] <= m.cap_hs[hs]
    m.storage_state_capacity_restriction_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_capacity_restriction_hs_t_rule)
    
    def storage_cap_restriction_hs_rule(m,hs,t,flag):
        if flag :
            if inv_flag:
                return m.x_load_hs_t[hs,t] <=  m.Cap_hs[hs] + m.cap_hs[hs] - m.store_level_hs_t[hs,t]
            else:
                return m.x_load_hs_t[hs,t] <=  m.cap_hs[hs] - m.store_level_hs_t[hs,t]
        else:
            return m.x_unload_hs_t[hs,t] <=  m.store_level_hs_t[hs,t] - m.unload_cap_hs[hs]
        
#    m.storage_cap_restriction_hs = pe.Constraint(m.j_hs,m.t,[True,False],rule=storage_cap_restriction_hs_rule)
    
    # The discharge and charge amounts are limited 
    def load_hs_t_restriction_rule (m,hs,t):
        return m.x_load_hs_t[hs,t] <=  m.binary_load_hs_t[hs,t]*m.load_cap_hs[hs]
    m.load_hs_t_restriction = pe.Constraint(m.j_hs,m.t,rule=load_hs_t_restriction_rule)
    
    def unload_hs_t_restriction_rule (m,hs,t,flag):
        
        if flag:
            return m.x_unload_hs_t[hs,t] <=  m.binary_unload_hs_t[hs,t]*m.unload_cap_hs[hs]
        else:
            return m.x_unload_hs_t[hs,t] <=  m.binary_unload_hs_t[hs,t]*m.store_level_hs_t[hs,t] 

    m.unload_hs_t_restriction = pe.Constraint(m.j_hs,m.t,[True,False],rule=unload_hs_t_restriction_rule)
    #%
    def ramp_j_chp_t_rule (m,j,t):
        if t==1:
            return m.ramp_j_chp_t[j,t] == 0 
        else:
            return m.ramp_j_chp_t[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1]
    m.ramping_j_chp_t = pe.Constraint(m.j_chp,m.t,rule=ramp_j_chp_t_rule)
    
    def ramp_j_waste_t_rule (m,j,t):
        if t==1:
            return m.ramp_j_waste_t[j,t] == 0 
        else:
            return m.ramp_j_waste_t[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1]
    m.ramping_j_waste_t = pe.Constraint(m.j_waste,m.t,rule=ramp_j_waste_t_rule)
    
    def renewable_factor_j_rule (m):
        if (sum(m.rf_j[j] for j in m.j) == 0):
            return pe.Constraint.Skip
        rule = sum([sum([(m.x_th_jt[j,t]+m.x_el_jt[j,t]) for t in m.t])*m.rf_j[j] for j in m.j]) >=  m.rf_tot * sum([sum([(m.x_th_jt[j,t]+m.x_el_jt[j,t]) for t in m.t])for j in m.j])        
        return rule 
    
    m.renewable_factor = pe.Constraint(rule=renewable_factor_j_rule)

        
    #%% Zielfunktion
    def cost_rule(m): 
        if inv_flag:
            c_inv = sum([(m.Cap_j[j] - m.x_th_cap_j[j])  * m.IK_j[j] * m.alpha_j[j] for j in m.j]) + sum([(m.Cap_hs[hs] - m.cap_hs[hs])*m.IK_hs[hs]* m.alpha_hs[hs] for hs in m.j_hs])
            c_op_fix = sum([(m.Cap_j[j]+m.x_th_cap_j[j]) * m.OP_fix_j[j] for j in m.j]) + \
                        sum([(m.Cap_hs[hs]+m.cap_hs[hs]) * m.OP_fix_hs[hs] for hs in m.j_hs])
        else:
            c_inv = 0
            c_op_fix = sum([m.Cap_j[j] * m.OP_fix_j[j] for j in m.j]) + \
                       sum([m.cap_hs[hs] * m.OP_fix_hs[hs] for hs in m.j_hs])
			
        c_op_var = sum([m.x_th_jt[j,t]* m.OP_var_j[j] for j in m.j for t in m.t])
        c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t  if j not in m.j_chp])  # 
        sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
#        c_var = c_var + sum([m.mc_jt[j,t] *(m.x_el_jt[j,t] + sv_chp * m.x_th_jt[j,t])/ m.n_el_j[j] for j in m.j_chp for t in m.t])
        c_var = c_var + sum([m.mc_jt[j,t] * m.x_th_jt[j,t] - m.sale_electricity_price_t[t] * m.x_el_jt[j,t] for j in m.j_chp for t in m.t])
        c_peak_el = m.P_el_max*10000  
        c_ramp = sum ([m.ramp_j_waste_t[j,t] * m.c_ramp_waste for j in m.j_waste for t in m.t]) + sum ([m.ramp_j_chp_t[j,t] * m.c_ramp_chp for j in m.j_chp for t in m.t])
        c_storage = sum([m.x_load_hs_t[hs,t]*m.electricity_price_t[t]  for hs in m.j_hs for t in m.t])
        c_hs_penalty = sum([m.x_unload_hs_t[hs,t]*1e-6  for hs in m.j_hs for t in m.t]) # for modeling reasons       
        c_tot = c_inv + c_var + c_op_fix + c_op_var + c_peak_el + c_ramp +c_storage + c_hs_penalty
 
        rev_gen_electricity = sum([m.x_el_jt[j,t]*(m.sale_electricity_price_t[t]) for j in m.j for t in m.t])
 
        rev_tot = rev_gen_electricity
        
        rule = c_tot - rev_tot
        return rule
    m.cost = pe.Objective(rule=cost_rule)
    
    
    #%% Compile Model 
    #print("*****************\ntime to load data: " + str(datetime.now()-solv_start)+"\n*****************")
    print("*****************\nCreating Model...\n*****************")
    solv_start = datetime.now()
    instance = m.create_instance(report_timing= True)
    print("*****************\ntime to create model: " + str(datetime.now()-solv_start)+"\n*****************")
    solv_start = datetime.now()
    print("*****************\nStart Solving...\n*****************")
    opt = pe.SolverFactory("gurobi")
    opt.options['MIPGap'] = 0.5
    opt.options['Threads'] = 4
    results = opt.solve(instance, load_solutions=False,tee=True,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
    instance.solutions.load_from(results)
    instance.solutions.store_to(results)
    print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")
    solv_start = datetime.now()
    try:
        if len(list(instance.j_hs.value)) != 0:
            print("*****************\nFixing Binary and resolving...\n*****************")
            # to get Dual Variables the binary variables had to be fixed and then resolved again 
            instance.binary_load_hs_t.fix()
            instance.binary_unload_hs_t.fix()
            instance.preprocess() 
            results = opt.solve(instance, load_solutions=False,tee=True,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
            instance.solutions.load_from(results)
            instance.solutions.store_to(results)
            print("*****************\ntime for resolving: " + str(datetime.now()-solv_start)+"\n*****************")
    except:
        pass

    return(instance,results)



if __name__ == "__main__":
    print('Main: Simpel Dispatch Module')

    
