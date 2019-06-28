# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% Import needed modules
import pyomo.environ as pe
from datetime import datetime
from pyomo.opt import SolverStatus, TerminationCondition
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
    m.j = pe.Set(initialize = val["j"])
    m.j_hp = pe.Set(initialize = val["j_hp"])
    m.j_pth = pe.Set(initialize = val["j_pth"])
    m.j_st = pe.Set(initialize = val["j_st"])
    m.j_waste = pe.Set(initialize = val["j_waste"])
    m.j_chp = pe.Set(initialize = val["j_chp"])
    m.j_bp = pe.Set(initialize = val["j_bp"])
    m.j_wh = pe.Set(initialize = val["j_wh"])
    m.j_gt = pe.Set(initialize = val["j_gt"])
    m.j_hs = pe.Set(initialize = val["j_hs"])
    m.all_heat_geneartors = pe.Set(initialize = val["all_heat_geneartors"])
    #%% Parameter - TODO: depends on how the input data looks finally
    m.demand_th_t = pe.Param(m.t,initialize = val["demand_th_t"])
    max_demad = val["max_demad"]
    
    m.radiation_t = pe.Param(m.t,initialize=val["radiation_t"])
    m.IK_j = pe.Param(m.j,initialize=val["IK_j"])
    m.OP_fix_j = pe.Param(m.j,initialize=val["OP_fix_j"])
    m.n_el_j = pe.Param(m.j ,initialize=val["n_el_j"])
    m.electricity_price_jt = pe.Param(m.j,m.t,initialize=val["electricity_price_jt"])
    m.P_min_el_j = pe.Param(m.j,initialize=val["P_min_el_j"])
    m.P_max_el_j = pe.Param(m.j,initialize=val["P_max_el_j"])
    m.Q_min_th_j = pe.Param(m.j_chp,initialize=val["Q_min_th_j"])

    m.mc_jt = pe.Param(m.j,m.t,initialize= val["mc_jt"])
    m.n_th_jt = pe.Param(m.j,m.t,initialize=val["n_th_jt"])
    m.x_th_cap_j = pe.Param(m.j,initialize=val["x_th_cap_j"])

    m.lt_j = pe.Param(m.j,initialize=val["lt_j"])

    m.ir = pe.Param(initialize=val["ir"])
    m.alpha_j = pe.Param(m.j,initialize=val["alpha_j"])
    m.c_ramp_j = pe.Param(m.j,initialize =val["c_ramp_j"] )
    
    m.load_cap_hs  = pe.Param(m.j_hs,initialize=val["load_cap_hs"])
    m.unload_cap_hs  = pe.Param(m.j_hs,initialize=val["unload_cap_hs"])
    m.n_hs = pe.Param(m.j_hs,initialize=val["n_hs"])
    m.IK_hs = pe.Param(m.j_hs,initialize=val["IK_hs"])
    m.cap_hs = pe.Param(m.j_hs,initialize=val["cap_hs"])
    

    m.alpha_hs = pe.Param(m.j_hs,initialize=val["alpha_hs"])

    m.rf_j = pe.Param(m.j,initialize=val["rf_j"])
    m.rf_tot = pe.Param(initialize=val["rf_tot"])
    m.OP_var_j = pe.Param(m.j,initialize=val["OP_var_j"])
    m.temperature_t = pe.Param(m.t,initialize=val["temperature_t"])
    thresh =  val["thresh"]

    m.sale_electricity_price_jt = pe.Param(m.j,m.t,initialize=val["sale_electricity_price_jt"])
    m.OP_fix_hs = pe.Param(m.j_hs,initialize=val["OP_fix_hs"])

    m.mr_j = pe.Param(m.j, initialize = val["mr_j"])
    m.em_j = pe.Param(m.j, initialize = val["em_j"])
    
    m.cap_losse_hs = pe.Param(m.j_hs,initialize=val["cap_losse_hs"])
    #%% Variablen
    m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)
    m.x_el_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.P_el_max = pe.Var(within=pe.NonNegativeReals)

    m.x_load_hs_t = pe.Var(m.j_hs,m.t,within=pe.Reals)
    m.Cap_hs = pe.Var(m.j_hs,within=pe.NonNegativeReals)
    m.store_level_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)

    m.ramp_jt = pe.Var(m.j, m.t,within=pe.NonNegativeReals)


    #%% Nebenbedingungen

    #% electircal power generation
    def gen_el_jt_rule(m,j,t):
        if j not in m.j_chp or m.n_th_jt[j,t] != 0:
            return m.x_el_jt[j,t] == m.x_th_jt[j,t] / m.n_th_jt[j,t] * m.n_el_j[j]
        else:
            return pe.Constraint.Skip
    m.gen_el_jt = pe.Constraint(m.j,m.t,rule=gen_el_jt_rule)

    #%  At any time, the heating generation must cover the heating demand
    def genearation_covers_demand_t_rule(m,t):
#        rule = sum([m.x_th_jt[j,t] for j in m.j]) >= demand_f * m.demand_th_t[t]
        rule = sum([m.x_th_jt[j,t] for j in m.j]) + \
                sum([- m.x_load_hs_t[hs,t]  for hs in m.j_hs]) >= demand_f * m.demand_th_t[t]
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

     #% mr specifies the amaount of capacity that has to run all the time. (0-1)
    def must_run_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] >= m.mr_j[j]*m.Cap_j[j]
        return rule
    m.must_run_jt = pe.Constraint(m.j,m.t,rule=must_run_jt_rule)

    #% The solar gains depend on the installed capacity and the solar radiation
    #% 1000 represent the radiation at wich the solar plant has maximal power 
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
            return m.P_el_max >= sum([m.x_th_jt[j,t] / m.n_th_jt[j,t]  for j in m.j_hp]) + sum([m.x_th_jt[j,t] / m.n_th_jt[j,t]  for j in m.j_pth])
        else:
            return pe.Constraint.Skip
    m.max_p_el_t = pe.Constraint(m.t,rule=max_p_el_t_rule)

    #% Restriction for the Powert to Heat - #TODO: Define upper Limit
    def power_to_heat_restriction_jt_rule(m,j,t):
        return m.x_th_jt[j,t] <=  max_demad
    m.power_to_heat_restriction_jt = pe.Constraint(m.j_pth,m.t,rule=power_to_heat_restriction_jt_rule)

    #% The maximum installed capacity for CHP plants is limited by the maximum heat demand. 
    def chp_electricity_driven_jt_rule (m,j,t,flag):
        if j in val["j_chp_se"]:
            #TODO: invest mode not possible nonlinear x_th_cap  is Cap_j
            k = ( m.P_max_el_j[j]/m.x_th_cap_j[j] - m.n_el_j[j] / m.n_th_jt[j,t] ) 
            if flag:
                rule = m.x_el_jt[j,t] <= m.P_max_el_j[j] - m.x_th_jt[j,t] * k  
            else:
                rule = m.x_el_jt[j,t] >= m.P_min_el_j[j] - m.x_th_jt[j,t] * k     
        else:
            rule = pe.Constraint.Skip
        return rule

    m.chp_electricity_driven_jt = pe.Constraint(m.j_chp,m.t,[True,False],rule=chp_electricity_driven_jt_rule)

   
    def chp_geneartion_restriction2_jt_rule(m,j,t):
        rule = m.P_min_el_j[j] <=  m.x_el_jt[j,t]
        return rule
    m.chp_geneartion_restriction2_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction2_jt_rule)

    def chp_geneartion_restriction5_jt_rule(m,j,t):
        rule = m.Q_min_th_j[j] <=  m.x_th_jt[j,t]
        return rule
    m.chp_geneartion_restriction5_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction5_jt_rule)

    #% The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling
    #with the produced electrical net power.
    def chp_geneartion_restriction3_jt_rule(m,j,t):
        if j in val["j_chp_se"]:
            rule = m.x_el_jt[j,t] >= m.x_th_jt[j,t] / m.n_th_jt[j,t] * m.n_el_j[j]
        else:
            rule = m.x_el_jt[j,t] == m.x_th_jt[j,t] / m.n_th_jt[j,t] * m.n_el_j[j]
        return rule
    m.chp_geneartion_restriction3_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction3_jt_rule)

#   Seting cap for chp generation
    def chp_geneartion_restriction4_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] <= m.demand_th_t[t] + sum(m.x_load_hs_t[hs,t] for hs in m.j_hs)
        return rule
    m.chp_geneartion_restriction4_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction4_jt_rule)

    # The heat storage level = old_level + pumping  - turbining
    def storage_state_hs_t_rule(m,hs,t):
        if t == 1:
            return m.store_level_hs_t[hs,t] == 0
        elif t == 8760:
            return m.store_level_hs_t[hs,t] == 0
        else:
            return m.store_level_hs_t[hs,t] == m.store_level_hs_t[hs,t-1]*(1-m.cap_losse_hs[hs]) + m.x_load_hs_t[hs,t-1]*m.n_hs[hs]
    m.storage_state_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_hs_t_rule)

    # The storage_level is restricted by the installed capcities
    def storage_state_capacity_restriction_hs_t_rule(m,hs,t):
        if inv_flag:
            return m.store_level_hs_t[hs,t] <= (m.Cap_hs[hs] - m.cap_hs[hs])
        else:
            return m.store_level_hs_t[hs,t] <= m.cap_hs[hs]
    m.storage_state_capacity_restriction_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_capacity_restriction_hs_t_rule)
    

    # The discharge and charge amounts are limited
    def load_hs_t_restriction_rule (m,hs,t):
        return m.x_load_hs_t[hs,t] <=  m.load_cap_hs[hs]
    m.load_hs_t_restriction = pe.Constraint(m.j_hs,m.t,rule=load_hs_t_restriction_rule)

    def unload_hs_t_restriction_rule (m,hs,t,flag):

        if flag:
            return m.x_load_hs_t[hs,t] >=  - m.unload_cap_hs[hs]
        else:
            return m.x_load_hs_t[hs,t] >=  - m.store_level_hs_t[hs,t]

    m.unload_hs_t_restriction = pe.Constraint(m.j_hs,m.t,[True,False],rule=unload_hs_t_restriction_rule)
    #%
    def ramp_cost_jt_rule (m,j,t):
        if t==1:
            return m.ramp_jt[j,t] == 0
        else:
            return m.ramp_jt[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1]
    m.ramp_cost_jt = pe.Constraint(m.j,m.t,rule=ramp_cost_jt_rule)


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
        c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t])  #
#        c_var_chp = sum([m.mc_jt[j,t] * m.x_th_jt[j,t] - m.sale_electricity_price_jt[j,t] * m.x_el_jt[j,t] for j in m.j_chp for t in m.t])
        c_var = c_var
        c_peak_el = m.P_el_max*10000
        c_ramp = sum ([m.ramp_jt[j,t] * m.c_ramp_j[j] for j in m.j for t in m.t])
        c_tot = c_inv + c_var + c_op_fix + c_op_var + c_peak_el + c_ramp

        rev_gen_electricity = sum([m.x_el_jt[j,t]*(m.sale_electricity_price_jt[j,t]) for j in m.j for t in m.t])

        rule = c_tot - rev_gen_electricity
        return rule
    m.cost = pe.Objective(rule=cost_rule)


    #%% Compile Model
    #print("*****************\ntime to load data: " + str(datetime.now()-solv_start)+"\n*****************")
    print("*****************\nCreating Model...\n*****************")
    solv_start = datetime.now()
    instance = m.create_instance(report_timing= False)  #TODO
    print("*****************\ntime to create model: " + str(datetime.now()-solv_start)+"\n*****************")
    solv_start = datetime.now()
    print("*****************\nSolving...\n*****************")
    opt = pe.SolverFactory("gurobi")
#    opt.options['MIPGap'] = 0.5
#    opt.options['Threads'] = 4
    #TODO
    results = opt.solve(instance, load_solutions=False,tee=False,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle
    instance.solutions.load_from(results)
    instance.solutions.store_to(results)
    print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")
    
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print ("this is feasible and optimal")
        return(instance,results)
    elif results.solver.termination_condition == TerminationCondition.infeasible:
         print ("infeasible")
         return("Error3","Error3")
    else:
        print ("something else is wrong")
        return (None,results.solver.message)
     
     
    



if __name__ == "__main__":
    print('Main: Simpel Dispatch Module')


