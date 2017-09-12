# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:08:48 2017

@author: root
"""

#%% Import needed modules
import pyomo.environ as pe
import numpy as np
#import matplotlib.pylab as plt
#from datetime import datetime,timedelta
#import locale
#locale.setlocale(locale.LC_ALL, 'de')
#%% Import needed Model-Data  --Load data per drag drop in spyder
import data_load 
Pl,Pl_dict,WS,Jahr,S,S_dict,em,demand_th,demand_th_dict,tec,szenario,t_v,radiation,radiation_dict = data_load.import_data()

#%%AUSWAHL 

year = 2020
scenario = "M2M"

#%%

WS["IK_WS_KAP"] = WS["IK_WS_KAP"]*0.5
WS["IK_WS_P"] = WS["IK_WS_P"]*0.5

#%% Add paramters
z=0.05 #% Kalkulationszinssatz

#%% Optinale Förderung von Solarthermie
Foerderung_Solar=0; #% €/kW Investitionsförderung Solarthermie 

#%% Geforderter Mindestanteil von Erneuerbaren
min_anteil_erneuerbar=0;

#%% Jährliche Kapitalkosten über Annuität in €/MWh

Pl["Kj"]=list(np.array(Pl["IK"])*((1+z)**np.array(Pl["LD"])*z/((1+z)**np.array(Pl["LD"])-1))*1000)


#% Kapitalkosten der Solarthermie nach Förderung
Pl["Kj"][2]=(Pl["IK"][2]-Foerderung_Solar)*((1+z)**Pl["LD"][2]*z/((1+z)**Pl["LD"][2]-1))*1000;

#%Kapitalkosten Wärmespeicher
WS["Kj_kap"] = WS["IK_WS_KAP"]*((1+z)**WS["LD"]*z/((1+z)**WS["LD"]-1))*1000;
WS["Kj_P"]=WS["IK_WS_P"]*((1+z)**WS["LD"]*z/((1+z)**WS["LD"]-1))*1000;

WS["Entladeleistung_bestand"]=140;

#%% Creation of a  Model
#m = pe.ConcreteModel()
m = pe.AbstractModel()
#% Annahmen Rampingcosts
m.c_ramp_KWK=pe.Param(initialize=10)
m.c_ramp_muell=pe.Param(initialize=100)
#% Annahme Zusatzkosten für maximale elektrische Leistung        
m.cost_P_el_max = pe.Param(initialize=10000) #%€/MW
#%% Sets
m.t = pe.RangeSet(1,8760,doc="Zeit in h")
m.j = pe.Set(initialize=tec)
m.j_kwk = pe.Set(initialize={"KWK"})
m.j_aw = pe.Set(initialize={"Abwärme 1","Abwärme 2","Abwärme 3"})
m.j_st = pe.Set(initialize={"Solarthermie"})
m.j_gt = pe.Set(initialize={"Geothermie 1","Geothermie 2"})
m.j_pt = pe.Set(initialize={"E-Heizer"})
m.j_mv = pe.Set(initialize={"Müllverbrennung"})
m.j_peak = pe.Set(initialize={"Spitzenlastkessel"})
m.j_wp = pe.Set(initialize={"Wärmepumpe"})
m.k = pe.Set(initialize= {"Wärmespeicher"})


m.jahr = pe.Set(initialize=Jahr)
m.sz = pe.Set(initialize=szenario)
m.f = pe.Set(initialize=list(em))

#%% Parameter
m.demand_th_t = pe.Param(m.t,initialize=demand_th_dict)
m.radiation_t = pe.Param(m.t,initialize=radiation_dict)

#%%
m.IK_j = pe.Param(m.j,initialize=Pl_dict["IK"]) 
m.n_th_j = pe.Param(m.j,initialize=Pl_dict["n_th"]) 
m.OP_j = pe.Param(m.j,initialize=Pl_dict["OP"]) 
m.POT_j = pe.Param(m.j ,initialize=Pl_dict["POT"])
m.P_th_bestand_j = pe.Param(m.j ,initialize=Pl_dict["P_th_bestand"])
m.LD_j = pe.Param(m.j ,initialize=Pl_dict["LD"])
m.EN_j = pe.Param(m.j ,initialize=Pl_dict["EN"])
m.n_el_j = pe.Param(m.j ,initialize=Pl_dict["n_el"])
m.P_el_bestand_j = pe.Param(m.j,initialize=Pl_dict["P_el_bestand"])
m.K_j = pe.Param(m.j,initialize=dict(zip(tec,Pl["Kj"])))

#%%
m.P_oil_sc_year = pe.Param(m.sz,m.jahr,initialize=S_dict["P_oil"])
m.P_gas_sc_year = pe.Param(m.sz,m.jahr,initialize=S_dict["P_gas"])
m.P_coal_sc_year = pe.Param(m.sz,m.jahr,initialize=S_dict["P_coal"])
m.P_co2_sc_year = pe.Param(m.sz,m.jahr,initialize=S_dict["P_co2"])
#%%
m.strompreis_year_sc_t = pe.Param(m.jahr,m.sz,m.t,initialize=S_dict["strompreis"])

m.em_f = pe.Param(m.f,initialize=em)

#%%
m.P_min_el_KWK = pe.Param(initialize=0)
m.Q_min_th_KWK = pe.Param(initialize=0)

m.ratioPMaxFW = pe.Param(initialize=450/700)
m.ratioPMax = pe.Param(initialize=450/820)
#%% Definition der Grenzkosten
'''
grenzkosten werden für alle Abwärmequellen und Geothermie jeweils nur einmal berechnet
da für alle Potenzialstufen die gleichen Wirkungsgrade
angenommen wurden - die Wirkungsgrade sind hier als Aufwand für 
Pumpen usw zu verstehen und sind so wir der COP einer Wärmepumpe
zu interpretieren
'''

#mc =  {(j,t): m.strompreis_year_sc_t[year,scenario,t] / m.n_th_j[j] for t in m.t for j in m.j if j not in m.j_kwk and  j not in m.j_mv and j not in m.j_peak and j not in m.j_st}
mc =  {(j,t): S_dict["strompreis"][year,scenario,t] / Pl_dict["n_th"][j] for t in range(1,8760+1) for j in tec if j not in ["KWK","Müllverbrennung","Spitzenlastkessel","Solarthermie"] }

#for j in m.j:
#    if j in m.j_peak:
#        for t in m.t:
#            mc[j,t]= m.P_gas_sc_year[scenario,year] /  \
#                          m.n_th_j[j] + \
#                          m.em_f["gas"]*m.P_co2_sc_year[scenario,year] / \
#                          m.n_th_j[j]   
#    if j in m.j_mv:
#        for t in m.t:
#            mc[j,t] =5
#    if j not in m.j_kwk:
#        for t in m.t:   
#            mc[j,t] = m.strompreis_year_sc_t[year,scenario,t] / m.n_th_j[j]

for j in tec:
    if j in ["Spitzenlastkessel"]:
        for t in range(1,8760+1):
            mc[j,t]= S_dict["P_gas"][scenario,year] /  \
                          Pl_dict["n_th"][j] + \
                          em["gas"]*S_dict["P_co2"][scenario,year] / \
                          Pl_dict["n_th"][j]   
    if j in ["Müllverbrennung"]:
        for t in range(1,8760+1):
            mc[j,t] =5
    if j not in ["KWK"]:
        for t in range(1,8760+1):   
            mc[j,t] = S_dict["strompreis"][year,scenario,t] /Pl_dict["n_th"][j]

m.mc_jt = pe.Param(m.j,m.t,initialize= mc)
        
#%% Variablen
m.x_th_jt = pe.Var(m.j,m.t,within=pe.NonNegativeReals)

m.unload_kt = pe.Var(m.k,m.t,within=pe.NonNegativeReals)
m.load_kt = pe.Var(m.k,m.t,within=pe.NonNegativeReals)

m.Cap_j = pe.Var(m.j,within=pe.NonNegativeReals)

m.x_th_bestand_jt = pe.Var(m.j_kwk,m.t,within=pe.NonNegativeReals)

m.x_el_jt = pe.Var(m.j_kwk,m.t,within=pe.NonNegativeReals)
m.x_el_bestand_jt = pe.Var(m.j_kwk,m.t,within=pe.NonNegativeReals)

m.stor_level_kt = pe.Var(m.k,m.t,within=pe.NonNegativeReals)

m.Cap_store_max_k = pe.Var(m.k,within=pe.NonNegativeReals) 
m.Cap_store_LadeLeistung_k = pe.Var(m.k,within=pe.NonNegativeReals) 
m.Cap_store_Ent_LadeLeistung_k = pe.Var(m.k,within=pe.NonNegativeReals) 
 
m.ramp_KWK_jt=pe.Var(m.j_kwk,m.t, within=pe.NonNegativeReals) 
m.ramp_muell_jt=pe.Var(m.j_mv,m.t, within=pe.NonNegativeReals) 

m.P_el_max=pe.Var(within=pe.NonNegativeReals) 

#%%  Nachfragegleichung - Der Schattenpreis dieser Gleichung ergibt den stündlichen Wärmepreis
def demand_t_rule(m,t): 
    rule = sum([m.x_th_jt[j,t] for j in m.j])+ sum([m.unload_kt[k,t]-m.load_kt[k,t] for k in m.k]) >= m.demand_th_t[t]
    return rule 
               
m.demand_t = pe.Constraint(m.t,rule=demand_t_rule)

#%% Beschränkung des Outputs 

def power_generation_t_rule1(m,t,j):
    
    if j in m.j_st:
        return ( m.Cap_j[j]+m.P_th_bestand_j[j] ) * m.radiation_t[t]/1000 >= m.x_th_jt[j,t]
    elif j in m.j_mv:
        return m.P_th_bestand_j[j] >= m.x_th_jt[j,t]
    elif j in m.j_kwk:
        return m.x_th_bestand_jt[j,t] <= m.P_th_bestand_j[j] 
    else:
        return m.Cap_j[j]+m.P_th_bestand_j[j] >= m.x_th_jt[j,t]    
              
m.power_generation1_t_j = pe.Constraint(m.t,m.j,rule=power_generation_t_rule1)


#%%
 
def stock_rule(m,j):
    if m.POT_j[j] != None:
        return m.Cap_j[j] <= m.POT_j[j]
    elif j in m.j_st:
        return m.Cap_j[j]>=1000
    elif j in m.j_kwk:
        return m.Cap_j[j] <= max(m.demand_th_t) - m.P_th_bestand_j[j]
    else:
        return pe.Constraint.Skip
    
m.stock_j = pe.Constraint(m.j,rule=stock_rule)  
     
#%%

def renewable_erz_t_rule(m,t):
    
    summe = sum([m.x_th_jt[j,t]*(1-m.EN_j[j]) for j in m.j]) + sum([m.x_th_bestand_jt[j,t] for j in m.j_kwk]) 
    rule = summe / sum(m.demand_th_t) <= 1 - min_anteil_erneuerbar
    
    return rule
m.renewable_erz_t = pe.Constraint(m.t,rule=renewable_erz_t_rule)

#%%
'''
Definition des Zeitraums in dem Wärmepumpen nicht verfügbar sind
und Spitzenlasten im Stromsystem auftreten (in dieser Zeit ist
eine zusätzliche elektrische Last für die Deckung der
Wärmenachfrage problematisch - deshalb werden hier auch Kosten
für P_el_max angesetzt
'''
t_knappheit = list(range(1,60*24+1))+list(range(8760-24*30,8760+1))

'''
Wärmepumpe ist hier nicht verfügbar
Constraints = [Constraints, x_WP(t_knappheit) <= 0];
'''

#%% Ermittlung der maximalen elektrischen Leistung in diesem Zeitraum
def pe_el_max_t_rule(m,t):
    if t in t_knappheit:
        return m.P_el_max >= sum([ m.x_th_jt[j,t]/m.n_th_j[j] for x in [m.j_wp,m.j_pt] for j in x ])
    else:
        return  pe.Constraint.Skip 
m.pe_el_max_t = pe.Constraint(m.t,rule=pe_el_max_t_rule)

#%% Restriktionen Wärmespeicher
def storage_restric_t_rule(m,k,t):
    
    if t==1:
        return m.stor_level_kt[k,t] == m.stor_level_kt[k,t+1]
    elif t>=2:
        return m.stor_level_kt[k,t] == m.stor_level_kt[k,t-1] * (1-WS["loss_ws"]) + m.load_kt[k,t-1]*WS["n_ws"]-m.unload_kt[k,t-1] 
m.storage_restric_kt = pe.Constraint(m.k,m.t,rule=storage_restric_t_rule)

def storage_restric2_t_rule(m,k,t):
    return m.stor_level_kt[k,t] <= m.Cap_store_max_k[k]  
m.storage_restric2_kt = pe.Constraint(m.k,m.t,rule=storage_restric2_t_rule)

def storage_restric3_t_rule(m,k,t):
    return m.load_kt[k,t] <= m.Cap_store_LadeLeistung_k[k]  
m.storage_restric3_kt = pe.Constraint(m.k,m.t,rule=storage_restric3_t_rule)


def storage_restric4_t_rule(m,k,t):
    return m.unload_kt[k,t] <= m.Cap_store_Ent_LadeLeistung_k[k]
m.storage_restric4_kt = pe.Constraint(m.k,m.t,rule=storage_restric4_t_rule)

def storage_restric5_t_rule(m,k,t):
    return m.Cap_store_LadeLeistung_k[k] == m.Cap_store_Ent_LadeLeistung_k[k]
m.storage_restric5_kt = pe.Constraint(m.k,m.t,rule=storage_restric5_t_rule)

        
#%% Ramping constraints Müll und KWK
def kwk_ramp_t_rule(m,j,t):
    if t>=2:
        return m.ramp_KWK_jt[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1] 
    else:
        return pe.Constraint.Skip 
    
m.kwk_ramp_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_ramp_t_rule)

def muell_ramp_t_rule(m,j,t):
    if t>=2:
        return m.ramp_muell_jt[j,t] >= m.x_th_jt[j,t] - m.x_th_jt[j,t-1] 
    else:
        return pe.Constraint.Skip 
    
m.muell_ramp_jt = pe.Constraint(m.j_mv,m.t,rule=muell_ramp_t_rule)


##%% Modellierung KWK 1:
#P_maxFW_el_KWK_j = {j: (m.Cap_j[j])/ m.ratioPMaxFW for j in m.j_kwk}
#P_max_el_KWK_j = {j:(m.Cap_j[j])/ m.ratioPMax for j in m.j_kwk}
#sv_kwk_j = {j:(P_max_el_KWK_j[j] - P_maxFW_el_KWK_j[j]) / (m.Cap_j[j]) for j in m.j_kwk}
#
#P_maxFW_el_KWK_bestand_j = {j:(m.P_th_bestand_j[j])/ m.ratioPMaxFW for j in m.j_kwk} 
#P_max_el_KWK_bestand_j =  {j:(m.P_th_bestand_j[j])/ m.ratioPMax for j in m.j_kwk} 
#sv_kwk_bestand_j =  {j: (P_max_el_KWK_bestand_j[j] - P_maxFW_el_KWK_bestand_j[j]) / m.P_th_bestand_j[j] for j in m.j_kwk }
# 
       
#Produktionsregion elektrisch inkl. Berücksichtigung Leistungseinbußung aufgrund Stromverlust
def kwk_model_t_rule (m,j,t):
    return m.P_min_el_KWK <= m.x_el_jt[j,t] 
m.kwk_model_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_model_t_rule)

#def kwk_model2_t_rule (m,j,t):
#    return m.x_el_jt[j,t] <= P_max_el_KWK_j[j] - sv_kwk_j[j] + m.x_th_jt[j,t]
#m.kwk_model2_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_model2_t_rule)    

#%Verhältnis maximale Wärmeauskopplung zur maximalen elektrischen Energie
def kwk_model3_t_rule (m,j,t):
    return m.x_el_jt[j,t] >= m.x_th_jt[j,t] /m.ratioPMaxFW
m.kwk_model3_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk_model3_t_rule)


#%% Modellierung KWK 2:
#Produktionsregion elektrisch inkl. Berücksichtigung Leistungseinbußung aufgrund Stromverlust
def kwk2_model_t_rule (m,j,t):
    return m.P_min_el_KWK <= m.x_el_bestand_jt[j,t] 
m.kwk2_model_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk2_model_t_rule)

#def kwk2_model2_t_rule (m,j,t):
#    return m.x_el_bestand_jt[j,t] <= P_max_el_KWK_bestand_j[j] - sv_kwk_bestand_j[j] *m.x_th_bestand_jt[j,t]
#m.kwk2_model2_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk2_model2_t_rule)    
#  
#%Verhältnis maximale Wärmeauskopplung zur maximalen elektrischen Energie
def kwk2_model3_jt_rule (m,j,t):
    return m.x_el_bestand_jt[j,t] >= m.x_th_bestand_jt[j,t] / m.ratioPMaxFW
m.kwk2_model3_jt = pe.Constraint(m.j_kwk,m.t,rule=kwk2_model3_jt_rule)


#%%        
'''        
% Zusätzliche Nebenbedingung: Von jeder Technologie wird zumindest 1 MW installiert - Diese
% Beschränkung hat nur sehr geringe Auswirkungen auf die Kosten und
% wurde aufgrund der leichteren Ergebnisausertung hinzugefügt
'''            

def cap_restric_j_rule(m,j):
    return m.Cap_j[j] >=0.1
cap_restric_j = pe.Constraint(m.j,rule=cap_restric_j_rule)

def cap_storage_max_restric_k_rule(m,k):
    return m.Cap_store_max_k[k] >=0.1
cap_storage_max_restric_k = pe.Constraint(m.k,rule=cap_storage_max_restric_k_rule)

def cap_storage_LadeLeistung_restric_k_rule(m,k):
    return m.Cap_store_LadeLeistung_k[k] >=0.1
cap_storage_LadeLeistung_restric_k = pe.Constraint(m.k,rule=cap_storage_LadeLeistung_restric_k_rule)

#%% Zielfunktion

def cost_rule(m):
    obj = []
    for t in m.t:

        BWL_KWK = sum([(m.x_el_jt[j,t] +m.x_th_jt[j,t])/m.n_el_j[j] for j in m.j_kwk ])

        BWL_KWK_bestand = sum([(m.x_el_bestand_jt[j,t]+m.x_th_bestand_jt[j,t])/m.n_el_j[j] for j in m.j_kwk ])
        
        
        #%% Gesamte variable Kosten je Technologie
        cost = sum([m.mc_jt[j,t]*m.x_th_jt[j,t] for j in m.j if j not in m.j_kwk])
        cost_KWK = m.P_gas_sc_year[scenario,year]*(BWL_KWK+BWL_KWK_bestand)+ m.em_f["gas"]*m.P_co2_sc_year[scenario,year]*(BWL_KWK+BWL_KWK_bestand)
        #%% Einnahmen auf Strommarkt
                
        #% Stromoutput Müllverbrennung - hier fixes Strom/Wärme Verhältnis
#        x_el_muell=sum([m.x_th_jt[j,t] * (m.n_el_j[j]/m.n_th_j[j]) for j in m.j_mv])
        
        income_KWK = sum([(m.x_el_jt[j,t]+m.x_el_bestand_jt[j,t])*m.strompreis_year_sc_t[year,scenario,t] for j in m.j_kwk])
        income_muell = sum([(m.x_th_jt[j,t] * (m.n_el_j[j]/m.n_th_j[j])) * m.strompreis_year_sc_t[year,scenario,t] for j in m.j_mv])
        
        #%% Definition der Gesamtkosten
                
        # variable Kosten
        obj_variable = cost + cost_KWK
        
        #Investitionskosten
        obj_invest = sum([m.Cap_j[j]+m.K_j[j] for j in m.j if j not in m.j_mv])
        
        #Investitionskosten Speicher
        obj_invest_speicher= sum([m.Cap_store_max_k[k]*WS["Kj_kap"]+m.Cap_store_LadeLeistung_k[k]*WS["Kj_P"] for k in m.k ] )
        
        # Instandhaltungskosten
        obj_operation = sum([(m.Cap_j[j]+m.P_th_bestand_j[j])*m.OP_j[j] for j in m.j if j not in m.j_mv])
        
        
        #Kosten für maximale elektrische Leistung während t_knappheit
        obj_peak_el=m.P_el_max*m.cost_P_el_max;
        
        # Kosten für Ramping
        obj_ramp=sum([m.ramp_KWK_jt[j,t]*m.c_ramp_KWK for j in m.j_kwk])+ sum([m.ramp_muell_jt[j,t]*m.c_ramp_muell for j in m.j_mv])
        #Das Modell minimiert die Zielfunktion unter Berücksichtigung aller Nebenbedingungen
        obj.append(obj_variable+obj_invest+obj_invest_speicher+obj_operation-income_KWK-income_muell+obj_peak_el+obj_ramp)    
                
        
    return sum(obj)

m.cost = pe.Objective(rule=cost_rule)


#%% Compile Model 
instance = m.create_instance()
#instance.pprint()
opt = pe.SolverFactory("glpk")
results = opt.solve(instance, load_solutions=False,suffixes=['.*'])   # Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
instance.solutions.load_from(results)
instance.solutions.store_to(results)

#%% Visualisierung der Ergebnisse
#f = {"b" :(0.12156862745098039, 0.4666666666666667, 0.7058823529411765),  
#         "g":(0.17254901960784313, 0.6274509803921569, 0.17254901960784313), 
#         "r":(0.8392156862745098, 0.15294117647058825, 0.1568627450980392), 
#         "c":(0.09019607843137255, 0.7450980392156863, 0.8117647058823529), 
#         "o":(1.0, 0.4980392156862745, 0.054901960784313725),
#         "l":(0.5803921568627451, 0.403921568627451, 0.7411764705882353)
#         }
#
#fig = plt.figure()
#ax = fig.add_subplot(111)
#
#ax.plot()