# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 11:42:54 2017

@author: root
"""

#%% Import needed modules
import pyomo.environ as pe
from datetime import datetime
print("*****************\nLoading Data...\n*****************")
import data_load 
Pl,Pl_dict,WS,Jahr,S,S_dict,em,demand_th,demand_th_dict,tec,szenario,t_v,radiation,radiation_dict,mc,year,scenario,min_anteil_erneuerbar,t_knappheit = data_load.import_data()
print("*****************\nCreating Model...\n*****************")

#%% Creation of a  Model
m = pe.AbstractModel()
#%% Sets
m.t = pe.RangeSet(1,8760)
m.j = pe.Set(initialize=[tec[0]])
#m.j_kwk = pe.Set(initialize={"KWK"})
#m.j_st = pe.Set(initialize={"Solarthermie"})
#m.j_pt = pe.Set(initialize={"E-Heizer"})
#m.j_mv = pe.Set(initialize={"Müllverbrennung"})
m.j_hp = pe.Set(initialize={tec[0]})
m.jahr = pe.Set(initialize=Jahr)
m.sz = pe.Set(initialize=szenario)

#%% Parameter
m.demand_th_t = pe.Param(m.t,initialize=demand_th_dict)
m.radiation_t = pe.Param(m.t,initialize=radiation_dict)
m.IK_j = pe.Param(m.j,initialize={x:Pl_dict["IK"][x] for x in [tec[0]]}) 
m.OP_j = pe.Param(m.j,initialize={x:Pl_dict["OP"][x] for x in [tec[0]]}) 
m.n_el_j = pe.Param(m.j ,initialize={x:Pl_dict["n_el"][x] for x in [tec[0]]})
m.strompreis_year_sc_t = pe.Param(m.jahr,m.sz,m.t,initialize=S_dict["strompreis"])
#m.P_min_el_KWK = pe.Param(initialize=0)
#m.Q_min_th_KWK = pe.Param(initialize=0)
#m.ratioPMaxFW = pe.Param(initialize=450/700)
#m.ratioPMax = pe.Param(initialize=450/820)
m.mc_jt = pe.Param(m.j,m.t,initialize= mc)
        
#%% Variablen
m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)
m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)
#m.x_el_jt = pe.Var(m.j_kwk,m.t,within=pe.NonNegativeReals)

#%% Nebenbedingungen 
#%  Zu jedem Zeitpunkt muss das Wärmenagebot die Wärmenachfrage decken
def genearation_covers_demand_t_rule(m,t): 
    rule = sum([m.x_th_jt[j,t] for j in m.j]) >= m.demand_th_t[t] 
    return rule 
m.genearation_covers_demand_t = pe.Constraint(m.t,rule=genearation_covers_demand_t_rule)
#% Die erzeugte Wämemenge darf die installierten Kapazitäten nicht ¨uberschreiten.
def generation_restriction_jt_rule(m,j,t): 
    rule = m.x_th_jt[j,t] <= m.Cap_j[j]
    return rule 
m.generation_restriction_jt = pe.Constraint(m.j,m.t,rule=generation_restriction_jt_rule)

#% Die solaren Gewinne sind abhängig von der installierten Kapazität und der solaren Strahlung
#def solar_restriction_jt_rule(m,j,t): 
#    rule = m.x_th_jt[j,t] <=  m.Cap_j[j]*m.radiation_t[t]/1000 
#    return rule 
#m.solar_restriction_jt = pe.Constraint(m.j_st,m.t,rule=solar_restriction_jt_rule)

#% Es wird angenommen, dass Wärmepumpen zu gewissen Zeitpunkten nicht in Betrieb genommen werden können (Problem mit der Wärmequellen (Frost) in der Winterzeit)).
#def heat_pump_restriction_jt_rule(m,j,t):
#    if t in t_knappheit:
#        rule = m.x_th_jt[j,t] ==  0 
#        return rule
#    else:
#        return pe.Constraint.Skip 
#m.heat_pump_restriction_jt = pe.Constraint(m.j_hp,m.t,rule=heat_pump_restriction_jt_rule)

##% Die maximal installierbare Kapazität für KWK-Anlagen wird durch den maximalen Wärmebedarf beschränkt.
#def kwk_capacity_restriction_jt_rule (m,j,t):
#    rule = m.Cap_j[j] <= max(demand_th) 
#    return rule 
#m.kwk_capacity_restriction_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_capacity_restriction_jt_rule)
#
##% Bei voller Fernwärmeauskopplung kann eine Leistungseinbußung auftreten, die jedoch nur die Maxmimalleistung verringert.
#def kwk_geneartion_restriction1_jt_rule(m,j,t):
#    sv_kwk = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
#    rule = m.x_el_jt[j,t] <= m.Cap_j[j]/m.ratioPMax - sv_kwk * m.x_th_jt[j,t]
#    return rule 
#m.kwk_geneartion_restriction1_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_geneartion_restriction1_jt_rule)
#
#def kwk_geneartion_restriction2_jt_rule(m,j,t):
#    rule = m.P_min_el_KWK <=  m.x_el_jt[j,t]
#    return rule 
#m.kwk_geneartion_restriction2_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_geneartion_restriction2_jt_rule) 
##% Das Verhältnis der maximalen Wärmeauskopplung zur maximalen elektrischen Leistungbestimmt den Rückgang der maximalen Wärmeauskopplung mit der produzierten elek-trischen Nettoleistung.
#def kwk_geneartion_restriction3_jt_rule(m,j,t):
#    rule = m.x_el_jt[j,t] >= m.x_th_jt[j,t] / m.ratioPMaxFW
#    return rule 
#m.kwk_geneartion_restriction3_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_geneartion_restriction3_jt_rule) 
#%% Zielfunktion
def cost_rule(m):
    c_inv = sum([m.Cap_j[j] * m.IK_j[j] for j in m.j])
    c_op = sum([m.Cap_j[j] * m.OP_j[j] for j in m.j])
    c_var= sum([m.mc_jt[j,t] * m.x_th_jt[j,t] for j in m.j for t in m.t ])  # if j not in m.j_kwk
#    sv_kwk = (m.ratioPMaxFW - m.ratioPMax) / (m.ratioPMax*m.ratioPMaxFW)
#    c_var = c_var + sum([(m.x_el_jt[j,t] + sv_kwk * m.x_th_jt[j,t])/ m.n_el_j[j] for j in m.j_kwk for t in m.t])
    c_peak_el = 0
    c_ramp = 0
    c_tot = c_inv + c_var + c_op + c_peak_el + c_ramp
    
#    rev_kwk = sum([m.x_el_jt[j,t]*m.strompreis_year_sc_t[year,scenario,t] for j in m.j_kwk for t in m.t])
    rev_kwk = 0
#    rev_waste = sum([m.x_th_jt[j,t] * m.strompreis_year_sc_t[year,scenario,t] for j in m.j_mv for t in m.t])
    rev_waste = 0
    rev_tot = rev_kwk + rev_waste
    
    rule = c_tot - rev_tot
    return rule
m.cost = pe.Objective(rule=cost_rule)


#%% Compile Model 
solv_start = datetime.now()
instance = m.create_instance()
print("*****************\nStart Solving...\n*****************")
opt = pe.SolverFactory("glpk")
results = opt.solve(instance, load_solutions=False,tee=True,suffixes=['.*'])   # tee= Solver Progress, Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
instance.solutions.load_from(results)
instance.solutions.store_to(results)

print("*****************\nTime for solving: " + str(datetime.now()-solv_start)+"\n*****************")

#%%
import os
start_time0 = datetime.now()
start_time = start_time0

path2solution = os.path.split(os.path.abspath("__file__"))[0]+"\Solution"

if os.path.isdir(path2solution) ==False:
    print("Create Solution Dictionary")
    os.mkdir(path2solution)

print("----------------------")
print("Writing Soluton to "+path2solution+"...")
print("----------------------")

solution={"Heat Geneartion":{j:[instance.x_th_jt[(j,t)]() for t in instance.t] for j in instance.j},
          "installed Capacity": {j:instance.Cap_j[j]() for j in instance.j}
                                                 }

# save the solution                                                                                                       
import json
with open(path2solution+r"\solution.json", "w") as f:
    json.dump(solution, f)
#del solution
print("----------------------")
print("Done in "+str(datetime.now()-start_time0) + "s !\nSaved to "+path2solution+r"\solution.json ")
print("----------------------")




