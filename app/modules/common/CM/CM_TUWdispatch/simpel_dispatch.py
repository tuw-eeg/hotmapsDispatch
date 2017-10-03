# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% Import needed modules
import pyomo.environ as pe
from datetime import datetime

def run(data,inv_flag):
    #%% Creation of a  Model
    m = pe.AbstractModel()
    #%% Sets - TODO: depends on how the input data looks finally
    m.t = pe.RangeSet(1,8760)
    m.j = pe.Set(initialize=data["tec"])
    m.j_hp = pe.Set(initialize={data["tec"][0]})
    m.j_pth = pe.Set(initialize={data["tec"][1]})
    m.j_st = pe.Set(initialize={data["tec"][2]})
    m.j_mv = pe.Set(initialize={data["tec"][3]})
    m.j_chp = pe.Set(initialize={data["tec"][4]})
    m.j_bp = pe.Set(initialize={data["tec"][5]})
    m.j_wh = pe.Set(initialize = data["tec"][6:9])
    m.j_gt = pe.Set(initialize = data["tec"][9:12])
    m.year = pe.Set(initialize=data["years"])
    m.sz = pe.Set(initialize=data["scenarios"])
    m.j_hs = pe.Set(initialize={"Heat Storage"})

    
    
    #%% Parameter - TODO: depends on how the input data looks finally
    m.demand_th_t = pe.Param(m.t,initialize=data["demand_th"])
    m.radiation_t = pe.Param(m.t,initialize=data["radiation"])
    m.IK_j = pe.Param(m.j,initialize=data["IK"]) 
    m.OP_j = pe.Param(m.j,initialize=data["OP"]) 
    m.n_el_j = pe.Param(m.j ,initialize=data["n_el"])
    m.electricity_price_t = pe.Param(m.t,initialize=data["electricity price"])
    m.P_min_el_chp = pe.Param(initialize=0)
    m.Q_min_th_chp = pe.Param(initialize=0)
    m.ratioPMaxFW = pe.Param(initialize=450/700)
    m.ratioPMax = pe.Param(initialize=450/820)
    m.mc_jt = pe.Param(m.j,m.t,initialize= data["mc"])
    m.n_th_j = pe.Param(m.j,initialize=data["n_th"]) 
    m.x_th_cap_j = pe.Param(m.j,initialize=data["P_th_cap"]) 
    
    m.load_cap_hs  = pe.Param(m.j_hs,initialize=50)   
    m.unload_cap_hs  = pe.Param(m.j_hs,initialize=140)
    m.n_hs = pe.Param(m.j_hs,initialize=0.95)
    m.loss_hs = pe.Param(m.j_hs,initialize=0.02)
    m.IK_hs = pe.Param(m.j_hs,initialize=30)
    m.cap_hs = pe.Param(m.j_hs,initialize=10)
    m.c_ramp_chp = pe.Param(initialize=10)
    m.c_ramp_waste = pe.Param(initialize=100)

           
    #%% Variablen
    m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)       
    m.x_el_jt = pe.Var(m.j_chp,m.t,within=pe.NonNegativeReals)
    m.P_el_max = pe.Var(within=pe.NonNegativeReals) 
    
    m.x_load_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.x_unload_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.Cap_hs = pe.Var(m.j_hs,within=pe.NonNegativeReals)
    m.store_level_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    
    m.ramp_j_chp_t = pe.Var(m.j_chp, m.t,within=pe.NonNegativeReals)
    m.ramp_j_mv_t = pe.Var(m.j_mv, m.t,within=pe.NonNegativeReals)
    
    #%% Nebenbedingungen 
    #%  At any time, the heating generation must cover the heating demand
    def genearation_covers_demand_t_rule(m,t): 
        rule = sum([m.x_th_jt[j,t] for j in m.j]) >= m.demand_th_t[t] 
        return rule 
    m.genearation_covers_demand_t = pe.Constraint(m.t,rule=genearation_covers_demand_t_rule)  
    
    #% ToDo: Define upper bound;
    def capacity_restriction_j_rule (m,j):
        rule = m.Cap_j[j] <= max(m.demand_th_t) * 1.5
        return rule 
    
    def capacity_restriction_j_rule2 (m,j):
        rule = m.Cap_j[j] == m.x_th_cap_j[j]
        return rule 
    
    if inv_flag:
        m.capacity_restriction_j_rule = pe.Constraint(m.j,rule=capacity_restriction_j_rule)
    else:
        m.capacity_restriction_j_rule = pe.Constraint(m.j,rule=capacity_restriction_j_rule2)
        
    #% The amount of heat eneragy generated must not exceed the installed capacities
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
    m.waste_incineration_restriction_jt = pe.Constraint(m.j_mv,m.t,rule=waste_incineration_restriction_jt_rule)
    
    #% Restriction for the Heat Pumps in the cold Seasion 
    def heat_pump_restriction_jt_rule(m,j,t):
        
        if t in range(1,24*60+1) or t in range(8760-24*30, 8760+1):
            return m.x_th_jt[j,t] == 0
        else: 
            return pe.Constraint.Skip
    m.heat_pump_restriction_jt = pe.Constraint(m.j_hp,m.t,rule=heat_pump_restriction_jt_rule)  
    
    #% The electrical peak load at the winter time (from December to February) results from
    #% the sum of the power consumption of the power to heat systems and the heat pumps.
    def max_p_el_t_rule(m,t):
        if t in range(1,24*60+1) or t in range(8760-24*30, 8760+1):
            return m.P_el_max >= sum([m.x_th_jt[j,t] / m.n_th_j[j]  for j in m.j_hp]) + sum([m.x_th_jt[j,t] / m.n_th_j[j]  for j in m.j_pth]) 
        else: 
            return pe.Constraint.Skip
    m.max_p_el_t = pe.Constraint(m.t,rule=max_p_el_t_rule)  
    
    #% The maximum installed capacity for CHP plants is limited by the maximum heat demand.
    def chp_capacity_restriction_j_rule (m,j):
        rule = m.Cap_j[j] <= max(m.demand_th_t) 
        return rule 
    
    if inv_flag:
        m.chp_capacity_restriction_j = pe.Constraint(m.j_chp,rule=chp_capacity_restriction_j_rule)
    
    #% With full heat extraction, a loss of power can occur which, only reduces the maximum power.
    def chp_geneartion_restriction1_jt_rule(m,j,t):
        sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
        rule = m.x_el_jt[j,t] <= m.Cap_j[j]/m.ratioPMax - sv_chp * m.x_th_jt[j,t]
        return rule 
    m.chp_geneartion_restriction1_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction1_jt_rule)
    
    def chp_geneartion_restriction2_jt_rule(m,j,t):
        rule = m.P_min_el_chp <=  m.x_el_jt[j,t]
        return rule 
    m.chp_geneartion_restriction2_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction2_jt_rule) 
    
    #% The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling 
    #with the produced electrical net power.
    def chp_geneartion_restriction3_jt_rule(m,j,t):
        rule = m.x_el_jt[j,t] >= m.x_th_jt[j,t] / m.ratioPMaxFW
        return rule 
    m.chp_geneartion_restriction3_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction3_jt_rule) 
    
    # The heat storage level results from the previous state from the loading and unloading, minus the losses of the memory.
    def storage_state_hs_t_rule(m,hs,t):
        if t == 1:
            return m.store_level_hs_t[hs,t] == 0
        elif t == 8760:
            return m.store_level_hs_t[hs,t] == 0
        else:
            return m.store_level_hs_t[hs,t] == m.store_level_hs_t[hs,t-1] - m.x_unload_hs_t[hs,t-1] + m.x_load_hs_t[hs,t-1]*m.n_hs[hs] - m.store_level_hs_t[hs,t-1] * m.loss_hs[hs]
    m.storage_state_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_hs_t_rule) 
    
    # The storage_level is restricted by the installed capcities 
    def storage_state_capacity_restriction_hs_t_rule2(m,hs,t):
        return m.Cap_hs[hs] == m.cap_hs[hs]
    if not inv_flag:
        m.storage_state_capacity_restriction2_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_capacity_restriction_hs_t_rule2)

    def storage_state_capacity_restriction_hs_t_rule(m,hs,t):
        return m.store_level_hs_t[hs,t] <= m.Cap_hs[hs]
    m.storage_state_capacity_restriction_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_capacity_restriction_hs_t_rule)
    
    # The discharge and charge amounts are limited by the installed capacity of the storage.
    def load_hs_t_restriction_rule (m,hs,t):
        return m.x_load_hs_t[hs,t] <= m.load_cap_hs[hs]
    m.load_hs_t_restriction = pe.Constraint(m.j_hs,m.t,rule=load_hs_t_restriction_rule)
    
    def unload_hs_t_restriction_rule (m,hs,t):
        return m.x_unload_hs_t[hs,t] <= m.unload_cap_hs[hs]
    m.unload_hs_t_restriction = pe.Constraint(m.j_hs,m.t,rule=unload_hs_t_restriction_rule)
    #%
    def ramp_j_chp_t_rule (m,j,t):
        if t==1:
            return m.ramp_j_chp_t[j,t] == 0 
        else:
            return m.ramp_j_chp_t[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1]
    m.ramping_j_chp_t = pe.Constraint(m.j_chp,m.t,rule=ramp_j_chp_t_rule)
    
    def ramp_j_mv_t_rule (m,j,t):
        if t==1:
            return m.ramp_j_mv_t[j,t] == 0 
        else:
            return m.ramp_j_mv_t[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1]
    m.ramping_j_mv_t = pe.Constraint(m.j_mv,m.t,rule=ramp_j_mv_t_rule)
    
    #%% Zielfunktion
    def cost_rule(m):
        if inv_flag:
            c_inv = sum([m.Cap_j[j] * m.IK_j[j] for j in m.j]) + sum([m.Cap_hs[hs]*m.IK_hs[hs] for hs in m.j_hs])
        else:
            c_inv = 0
        c_op = sum([m.Cap_j[j] * m.OP_j[j] for j in m.j])
        c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t  if j not in m.j_chp])  # 
        sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
        c_var = c_var + sum([(m.x_el_jt[j,t] + sv_chp * m.x_th_jt[j,t])/ m.n_el_j[j] for j in m.j_chp for t in m.t])
        c_peak_el = m.P_el_max*1000  
        c_ramp = sum ([m.ramp_j_mv_t[j,t] * m.c_ramp_waste for j in m.j_mv for t in m.t]) + sum ([m.ramp_j_chp_t[j,t] * m.c_ramp_chp for j in m.j_chp for t in m.t])
        c_tot = c_inv + c_var + c_op + c_peak_el + c_ramp
 
        rev_chp = sum([m.x_el_jt[j,t]*m.electricity_price_t[t] for j in m.j_chp for t in m.t])
        rev_waste = sum([m.x_th_jt[j,t] * m.electricity_price_t[t] for j in m.j_mv for t in m.t])
        rev_tot = rev_chp + rev_waste
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
    results = opt.solve(instance, load_solutions=False,tee=True,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
    instance.solutions.load_from(results)
    instance.solutions.store_to(results)
    print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")

    return(instance)



if __name__ == "__main__":
    print('Main: Simpel Dispatch Module')

    
