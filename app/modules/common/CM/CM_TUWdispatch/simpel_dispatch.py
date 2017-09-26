# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% Import needed modules
import pyomo.environ as pe
from datetime import datetime

def run(data):
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
    m.year = pe.Set(initialize=data["years"])
    m.sz = pe.Set(initialize=data["scenarios"])
    
    #%% Parameter - TODO: depends on how the input data looks finally
    m.demand_th_t = pe.Param(m.t,initialize=data["demand_th"])
    m.radiation_t = pe.Param(m.t,initialize=data["radiation"])
    m.IK_j = pe.Param(m.j,initialize=data["IK"]) 
    m.OP_j = pe.Param(m.j,initialize=data["OP"]) 
    m.n_el_j = pe.Param(m.j ,initialize=data["n_el"])
    m.electricity_price_year_sc_t = pe.Param(m.year,m.sz,m.t,initialize=data["electricity price"])
    m.P_min_el_chp = pe.Param(initialize=0)
    m.Q_min_th_chp = pe.Param(initialize=0)
    m.ratioPMaxFW = pe.Param(initialize=450/700)
    m.ratioPMax = pe.Param(initialize=450/820)
    m.mc_jt = pe.Param(m.j,m.t,initialize= data["mc"])
    m.n_th_j = pe.Param(m.j,initialize=data["n_el"]) 
           
    #%% Variablen
    m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)
    m.x_el_jt = pe.Var(m.j_chp,m.t,within=pe.NonNegativeReals)
    m.P_el_max=pe.Var(within=pe.NonNegativeReals) 
    #%% Nebenbedingungen 
    #%  At any time, the heating generation must cover the heating demand
    def genearation_covers_demand_t_rule(m,t): 
        rule = sum([m.x_th_jt[j,t] for j in m.j]) >= m.demand_th_t[t] 
        return rule 
    m.genearation_covers_demand_t = pe.Constraint(m.t,rule=genearation_covers_demand_t_rule)  
    
    #% ToDo: Define upper bound;
    def capacity_restriction_jt_rule (m,j,t):
        rule = m.Cap_j[j] <= max(m.demand_th_t) * 1.5
        return rule 
    m.capacity_restriction_jt_rule = pe.Constraint(m.j,m.t,rule=capacity_restriction_jt_rule)
        
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
    
    #% The maximum installed capacity for CHP plants is limited by the maximum heat demand.
    def chp_capacity_restriction_jt_rule (m,j,t):
        rule = m.Cap_j[j] <= max(m.demand_th_t) 
        return rule 
    m.chp_capacity_restriction_jt = pe.Constraint(m.j_chp,m.t,rule=chp_capacity_restriction_jt_rule)
    
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
    #%% Zielfunktion
    def cost_rule(m):
        c_inv = sum([m.Cap_j[j] * m.IK_j[j] for j in m.j])
        c_op = sum([m.Cap_j[j] * m.OP_j[j] for j in m.j])
        c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t  if j not in m.j_chp])  # 
        sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
        c_var = c_var + sum([(m.x_el_jt[j,t] + sv_chp * m.x_th_jt[j,t])/ m.n_el_j[j] for j in m.j_chp for t in m.t])
        c_peak_el = 0
        c_ramp = 0
        c_tot = c_inv + c_var + c_op + c_peak_el + c_ramp
 
        #Auswahl: auch die Grenzkosten sind aus diesen Strommarktszenarien berechnet worden
        year = 2020
        scenario = "M2M"
        rev_chp = sum([m.x_el_jt[j,t]*m.electricity_price_year_sc_t[year,scenario,t] for j in m.j_chp for t in m.t])
#        rev_chp=0
        rev_waste = sum([m.x_th_jt[j,t] * m.electricity_price_year_sc_t[year,scenario,t] for j in m.j_mv for t in m.t])
        rev_tot = rev_chp + rev_waste
        rule = c_tot - rev_tot
        return rule
    m.cost = pe.Objective(rule=cost_rule)
    
    
    #%% Compile Model 
    #print("*****************\ntime to load data: " + str(datetime.now()-solv_start)+"\n*****************")
    print("*****************\nCreating Model...\n*****************")
    solv_start = datetime.now()
    instance = m.create_instance()
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

    
