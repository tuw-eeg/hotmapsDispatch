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
    val,message = preprocessing(data,demand_f,inv_flag,selection)
    
    if val == "Error1":
        return (val,message)
    elif val == "Error2":
        return (val,message)
    m.j_hp_new = pe.Set(initialize=val["j_hp_new"])
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
    m.j_air_heat_pump = pe.Set(initialize = val["j_air_heat_pump"])
    m.j_river_heat_pump = pe.Set(initialize = val["j_river_heat_pump"])
    m.j_wastewater_heat_pump = pe.Set(initialize = val["j_wastewater_heat_pump"])
    m.j_wasteheat_heat_pump = pe.Set(initialize = val["j_wasteheat_heat_pump"])
    m.all_heat_geneartors = pe.Set(initialize = val["all_heat_geneartors"])
    #%% Parameter - TODO: depends on how the input data looks finally
    m.demand_th_t = pe.Param(m.t,initialize = val["demand_th_t"])
    m.temp_river = pe.Param(m.t,initialize = val["temp_river"])
    m.temp_waste_water = pe.Param(m.t,initialize = val["temp_waste_water"])
    m.temp_flow = pe.Param(m.t,initialize = val["temp_flow"])
    m.temp_return = pe.Param(m.t,initialize = val["temp_return"])
    m.temp_ambient = pe.Param(m.t,initialize = val["temp_ambient"])
    m.radiation = pe.Param(m.t,initialize = val["radiation"])
    
    max_demad = val["max_demad"]
    m.potential_j = pe.Param(m.j,initialize=val["potential_j"])
    m.pow_cap_j = pe.Param(m.j,initialize=val["pow_cap_j"])
    m.radiation_t = pe.Param(m.t,initialize=val["radiation_t"])
    m.IK_j = pe.Param(m.j,initialize=val["IK_j"])
    m.OP_fix_j = pe.Param(m.j,initialize=val["OP_fix_j"])
    m.n_el_j = pe.Param(m.j ,initialize=val["n_el_j"])
    m.electricity_price_jt = pe.Param(m.j,m.t,initialize=val["electricity_price_jt"])
    m.P_min_el_chp = pe.Param(initialize=val["P_min_el_chp"])
    m.Q_min_th_chp = pe.Param(initialize=val["Q_min_th_chp"])
    m.ratioPMaxFW = pe.Param(initialize=val["ratioPMaxFW"])
    m.ratioPMax = pe.Param(initialize=val["ratioPMax"])
    m.mc_jt = pe.Param(m.j,m.t,initialize= val["mc_jt"])
    m.n_th_jt = pe.Param(m.j,m.t,initialize=val["n_th_jt"])
    m.hp_restriction_factor_jt = pe.Param(m.j,m.t,initialize=val["hp_restriction_factor_jt"])
    m.nom_p_th_j = pe.Param(m.j,initialize=val["nom_p_th_j"])
    m.min_p_th_j = pe.Param(m.j,initialize=val["min_p_th_j"])
    m.x_th_cap_j = pe.Param(m.j,initialize=val["x_th_cap_j"])
#    m.x_el_cap_j = pe.Param(m.j,initialize=val["x_el_cap_j"])
#    m.pot_j = pe.Param(m.j,initialize=val["pot_j"])
    m.lt_j = pe.Param(m.j,initialize=val["lt_j"])
    m.ec_j = pe.Param(m.j,initialize=val["ec_j"],within=pe.Any)
#    m.el_surcharge = pe.Param(m.j,initialize=val[27])  # Taxes for electricity price
    m.ir = pe.Param(initialize=val["ir"])
    m.alpha_j = pe.Param(m.j,initialize=val["alpha_j"])

    m.load_cap_hs  = pe.Param(m.j_hs,initialize=val["load_cap_hs"])
    m.unload_cap_hs  = pe.Param(m.j_hs,initialize=val["unload_cap_hs"])
    m.n_hs = pe.Param(m.j_hs,initialize=val["n_hs"])
    m.loss_hs = pe.Param(m.j_hs,initialize=val["loss_hs"])
    m.IK_hs = pe.Param(m.j_hs,initialize=val["IK_hs"])
    m.cap_hs = pe.Param(m.j_hs,initialize=val["cap_hs"])
    m.c_ramp_j = pe.Param(m.j,initialize =val["c_ramp_j"] ) 
    m.c_coldstart_j = pe.Param(m.j,initialize=val["c_coldstart_j"])
    m.alpha_hs = pe.Param(m.j_hs,initialize=val["alpha_hs"])

    m.rf_j = pe.Param(m.j,initialize=val["rf_j"])
    m.rf_tot = pe.Param(initialize=val["rf_tot"])
    m.OP_var_j = pe.Param(m.j,initialize=val["OP_var_j"])
    m.temperature_t = pe.Param(m.t,initialize=val["temperature_t"])
    m.sale_electricity_price_jt = pe.Param(m.j,m.t,initialize=val["sale_electricity_price_jt"])
    m.OP_fix_hs = pe.Param(m.j_hs,initialize=val["OP_fix_hs"])

    m.mr_j = pe.Param(m.j, initialize = val["mr_j"])
    m.em_j = pe.Param(m.j, initialize = val["em_j"])
    m.pco2 = pe.Param(initialize = val["pco2"])
    
    m.cap_losse_hs = pe.Param(m.j_hs,initialize=val["cap_losse_hs"])
    m.n_th_nom_jt = pe.Param(m.j,m.t,initialize=val["n_th_nom_jt"])
    m.restriction_factor_jt = pe.Param(m.j,m.t,initialize=val["restriction_factor_jt"])
    m.min_out_factor_j = pe.Param(m.j,initialize=val["min_out_factor_j"])
    #%% Variablen
    m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
    m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)
#     m.Cap_nom_j = pe.Var(m.j,within=pe.NonNegativeReals)
    m.x_el_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
#     m.P_el_max = pe.Var(within=pe.NonNegativeReals)

    m.x_load_hs_t = pe.Var(m.j_hs,m.t,within=pe.Reals)
#    m.x_unload_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)
    m.Cap_hs = pe.Var(m.j_hs,within=pe.NonNegativeReals)
    m.store_level_hs_t = pe.Var(m.j_hs,m.t,within=pe.NonNegativeReals)

    m.ramp_jt = pe.Var(m.j, m.t,within=pe.NonNegativeReals) 

    m.coldstart_jt = pe.Var(m.j, m.t, within = pe.Boolean)
    
    m.Active_jt = pe.Var(m.j,m.t, within = pe.Boolean)
    m.Active2_jt = pe.Var(m.j,m.t, within = pe.Binary)
    m.Active3_jt = pe.Var(m.j,m.t, within = pe.Binary)
#    m.Storage_load_hs_jt = pe.Var(m.j_hs,m.t, within = pe.Boolean)
#    m.Storage_unload_hs_jt = pe.Var(m.j_hs,m.t, within = pe.Boolean)
#    m.cop_HP_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)

    #%% Nebenbedingungen
    def potential_restriction_rule_j(m,j):
        if m.potential_j[j] > 0: 
            rule = sum (m.x_th_jt[j,t] for t in m.t) <= m.potential_j[j]
        else:
            rule = pe.Constraint.Skip
        return rule
    m.potential_restriction_rule = pe.Constraint(m.j,rule=potential_restriction_rule_j) 
    
    def power_restriction_jt_rule(m,j,t):
        if m.pow_cap_j[j]>0:
            rule = m.x_th_jt[j,t] <=  m.pow_cap_j[j]
        else:
            rule = pe.Constraint.Skip            
        return rule
    m.power_restriction_jt = pe.Constraint(m.j,m.t,rule=power_restriction_jt_rule)
    
  

    #% electircal power generation
    def gen_el_jt_rule(m,j,t):
        if j not in m.j_chp or m.n_th_jt[j,t] != 0:
            return m.x_el_jt[j,t] == m.x_th_jt[j,t] / m.n_th_jt[j,t] * m.n_el_j[j]
        else:
            return pe.Constraint.Skip
    m.gen_el_jt = pe.Constraint(m.j,m.t,rule=gen_el_jt_rule)

    #%  At any time, the heating generation must cover the heating demand
    def genearation_covers_demand_t_rule(m,t):
        rule = sum([m.x_th_jt[j,t] for j in m.j]) - \
                    sum([m.x_load_hs_t[hs,t]  for hs in m.j_hs]) == demand_f * m.demand_th_t[t]
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
        rule = m.x_th_jt[j,t] <= m.Cap_j[j] / m.n_th_nom_jt[j,t] * m.n_th_jt[j,t]  * m.Active_jt[j,t] * m.restriction_factor_jt[j,t]
        return rule
    m.generation_restriction_jt = pe.Constraint(m.j,m.t,rule=generation_restriction_jt_rule)
    
    #% All Generators have a minimum Operating Power
    def generation_minimum_hp_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] >= m.Cap_j[j] / m.n_th_nom_jt[j,t] * m.n_th_jt[j,t]  * m.Active_jt[j,t] * m.min_out_factor_j[j]
        return rule
    m.generation_minimum_hp_jt = pe.Constraint(m.j,m.t,rule=generation_minimum_hp_jt_rule)


    def must_run_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] >= m.mr_j[j] * m.Cap_j[j] / m.n_th_nom_jt[j,t] * m.n_th_jt[j,t] * m.restriction_factor_jt[j,t]   * m.Active3_jt[j,t]
        return rule
    m.mr_jt = pe.Constraint(m.j,m.t,rule=must_run_jt_rule)

    def must_run_jt_rule2(m,j,t):
        rule = m.x_th_jt[j,t] >= m.demand_th_t[t]  * m.Active2_jt[j,t]
        return rule
    m.mr_jt2 = pe.Constraint(m.j,m.t,rule=must_run_jt_rule2)
    
    def must_run_jt_rule3(m,j,t):
        return m.Active2_jt[j,t] + m.Active3_jt[j,t] == 1
    m.mr_jt3 = pe.Constraint(m.j,m.t,rule=must_run_jt_rule3) 
     #% mr specifies the amaount of capacity that has to run all the time. (0-1)

    #% The solar gains depend on the installed capacity and the solar radiation
    #% 1000 represent the radiation at wich the solar plant has maximal power 
    def solar_restriction_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] <=  m.Cap_j[j]*m.radiation_t[t] / max(val["radiation_t"].values())
        return rule
    m.solar_restriction_jt = pe.Constraint(m.j_st,m.t,rule=solar_restriction_jt_rule)

    #% No investment in waste incineration plants possible,thus geneartion cant exeed already installed capacities
    def waste_incineration_restriction_jt_rule(m,j,t):
        rule = m.x_th_jt[j,t] <=  m.x_th_cap_j[j]
        return rule
    m.waste_incineration_restriction_jt = pe.Constraint(m.j_waste,m.t,rule=waste_incineration_restriction_jt_rule)

    #% With full heat extraction, a loss of power can occur which, only reduces the maximum power.
    def chp_geneartion_restriction1_jt_rule(m,j,t):
        if j in val["j_chp_se"]:
            sv_chp = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
            rule = m.x_el_jt[j,t] <= m.Cap_j[j]/m.ratioPMax - sv_chp * m.x_th_jt[j,t]
        else:
            rule = pe.Constraint.Skip
        return rule
    m.chp_geneartion_restriction1_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction1_jt_rule)   # should be adopted using binary variables

    def chp_geneartion_restriction2_jt_rule(m,j,t):
        rule = m.P_min_el_chp <=  m.x_el_jt[j,t]
        return rule
    m.chp_geneartion_restriction2_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction2_jt_rule)

    def chp_geneartion_restriction5_jt_rule(m,j,t):
        rule = m.Q_min_th_chp <=  m.x_th_jt[j,t]
        return rule
#    m.chp_geneartion_restriction5_jt = pe.Constraint(m.j_chp,m.t,rule=chp_geneartion_restriction5_jt_rule)

#    % The ratio of the maximum heat decoupling to the maximum electrical power determines the decrease in the maximum heat decoupling
#    with the produced electrical net power.
    def chp_geneartion_restriction3_jt_rule(m,j,t):
        if j in val["j_chp_se"]:
            rule = m.x_el_jt[j,t] >= m.x_th_jt[j,t] / m.ratioPMaxFW    # should be adopted using binary variables
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
            return m.store_level_hs_t[hs,t] == m.store_level_hs_t[hs,8760]
        else: 
            return m.store_level_hs_t[hs,t] == m.store_level_hs_t[hs,t-1]*(1-m.cap_losse_hs[hs]) + m.x_load_hs_t[hs,t-1]*m.n_hs[hs] 
    m.storage_state_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_hs_t_rule) 

    
    # installed capcities must be greater or equeal pre installed capacities
    def storage_capacity_restriction_hs_rule(m,hs):
        if inv_flag:
            return m.Cap_hs[hs]  >= m.cap_hs[hs]
        else:
            return m.Cap_hs[hs]  == m.cap_hs[hs]
    m.storage_capacity_restriction_hs = pe.Constraint(m.j_hs,rule=storage_capacity_restriction_hs_rule)


    # The storage_level is restricted by the installed capcities
    def storage_state_capacity_restriction_hs_t_rule(m,hs,t):
        return m.store_level_hs_t[hs,t] <= m.Cap_hs[hs]
    m.storage_state_capacity_restriction_hs_t = pe.Constraint(m.j_hs,m.t,rule=storage_state_capacity_restriction_hs_t_rule)




    # The discharge and charge amounts are limited
    def load_hs_t_restriction_rule (m,hs,t):
        return m.x_load_hs_t[hs,t] <=   m.load_cap_hs[hs]
    m.load_hs_t_restriction = pe.Constraint(m.j_hs,m.t,rule=load_hs_t_restriction_rule)

    def unload_hs_t_restriction_rule (m,hs,t,flag):

        if flag:
            return m.x_load_hs_t[hs,t] >=  -  m.unload_cap_hs[hs]
        else:
            return m.x_load_hs_t[hs,t] >=  -  m.store_level_hs_t[hs,t]

    m.unload_hs_t_restriction = pe.Constraint(m.j_hs,m.t,[True,False],rule=unload_hs_t_restriction_rule)
    #%
    def ramp_cost_jt_rule (m,j,t): 
        if t==1: 
            return m.ramp_jt[j,t] == 0 
        else: 
            return m.ramp_jt[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1] 
    m.ramp_cost_jt = pe.Constraint(m.j,m.t,rule=ramp_cost_jt_rule) 
    
    def coldstart_j_t_rule (m,j,t):
        if t==1:
            return  m.coldstart_jt[j,t] == 1
        else:
            return m.coldstart_jt[j,t] >= m.Active_jt[j,t] - m.Active_jt[j,t-1] # puts out True only for Coldstart
    m.coldstart_rule_jt = pe.Constraint(m.j,m.t,rule=coldstart_j_t_rule)
    
    
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
            c_op_fix = sum([m.Cap_j[j] * m.OP_fix_j[j] for j in m.j]) + \
                        sum([m.Cap_hs[hs] * m.OP_fix_hs[hs] for hs in m.j_hs])
        else:
            c_inv = 0
            c_op_fix = sum([m.Cap_j[j] * m.OP_fix_j[j] for j in m.j]) + \
                       sum([m.Cap_hs[hs] * m.OP_fix_hs[hs] for hs in m.j_hs])

        c_op_var = sum([m.x_th_jt[j,t]* m.OP_var_j[j] for j in m.j for t in m.t])
        c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t])  #
#        c_var_chp = sum([m.mc_jt[j,t] * m.x_th_jt[j,t] - m.sale_electricity_price_jt[j,t] * m.x_el_jt[j,t] for j in m.j_chp for t in m.t])
        c_var = c_var
        c_peak_el = 0.0#m.P_el_max*10000
        c_ramp = sum ([m.ramp_jt[j,t] * m.c_ramp_j[j] for j in m.j for t in m.t]) 
        c_cold = sum([(m.coldstart_jt[j,t]*m.c_coldstart_j[j]) for j in m.j for t in m.t]) #Counts up coldstarts and multiplies with Coldstart cost

#        c_hs_penalty_load = sum([m.x_load_hs_t[hs,t]*5e-2  for hs in m.j_hs for t in m.t])      # for modeling reasons
#        c_hs_penalty_unload = sum([m.x_unload_hs_t[hs,t]*5e-2  for hs in m.j_hs for t in m.t])  # for modeling reasons
        c_tot = c_inv + c_var + c_op_fix + c_op_var + c_cold + c_ramp #+c_hs_penalty_load + c_hs_penalty_unload

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
    opt.options['MIPGap'] = 1e-3
    opt.options["MIPFocus"] = 0
    opt.options["TimeLimit"] = 1200
    opt.options['NodefileStart']=0.5
    # opt.options['Threads'] = 0
    #TODO 4
    tee = True
    results = opt.solve(instance, load_solutions=False,tee=tee,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle
    print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")
    solv_start = datetime.now()
    if results.solver.termination_condition == TerminationCondition.maxTimeLimit:
        return (None,results.solver.message)
        print("Time Limit reached, set MIPGap=0.05 and try solving...")
        opt.options['MIPGap'] = 0.05
        results = opt.solve(instance, load_solutions=False,tee=tee,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle
        print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")
        if results.solver.termination_condition == TerminationCondition.maxTimeLimit:
            solv_start = datetime.now()
            print("Time Limit reached, set MIPFocus=1 to find any feasible solution....")
            opt.options['MIPFocus'] = 1
            opt.options["TimeLimit"] = 260
            results = opt.solve(instance, load_solutions=False,tee=tee,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle
            print("*****************\ntime for solving: " + str(datetime.now()-solv_start)+"\n*****************")
            if results.solver.termination_condition == TerminationCondition.maxTimeLimit:
                solv_start = datetime.now()
                print("Time Limit reached, set MIPFocus=0 one more time solving....")
                opt.options['MIPFocus'] = 0
                results = opt.solve(instance, load_solutions=False,tee=tee,suffixes=['.*']) 
                print("*****************\ntime for resolving: " + str(datetime.now()-solv_start)+"\n*****************")
                
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        instance.solutions.load_from(results)
        instance.solutions.store_to(results)
        print("*****************\nFixing Binary and resolving...\n*****************") 
        # to get Dual Variables the binary variables had to be fixed and then resolved again  
        instance.Active_jt.fix() 
        instance.Active2_jt.fix() 
        instance.Active3_jt.fix() 
#        instance.Storage_load_hs_jt.fix() 
#        instance.Storage_unload_hs_jt.fix()
        instance.coldstart_jt.fix()
        instance.preprocess()  
        results = opt.solve(instance, load_solutions=False,tee=tee,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle    
        instance.solutions.load_from(results) 
        instance.solutions.store_to(results) 
        print("*****************\ntime for resolving fixed variables: " + str(datetime.now()-solv_start)+"\n*****************") 
        
    else: 
        print("Here")
        print(results.solver.status)
        print(results.solver.termination_condition)
        print ("something else is wrong")
        return (None,results.solver.message)
    
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


