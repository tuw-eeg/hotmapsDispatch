# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 12:29:48 2017

@author: root
"""
#%% Import of the pyomo module
import pyomo.environ as pe

#%% Creation of a Concrete Model
model = pe.AbstractModel()
#model.create_instance()
#%% Sets
model.t = pe.Set(doc="Zeit in h")
model.j = pe.Set(doc='Erzeugung von Kraftwerktyp')
model.f = pe.Set(doc='Brennstoffe')
model.brennstoffe_jf = pe.Set(dimen=2,within=model.j*model.f,doc='Kombinationen von Erzeugung und Brennstoffe')  #!! 
#model.brennstoffe_jf = pe.Set(initialize=model.j*model.f)

#only comment

#%% Parameter
model.C_CO2 =  pe.Param(doc = "CO2-Kosten")

model.Pmax_j = pe.Param(model.j, doc='Maximale Leistung des j-Kraftwerks in MW')

model.eta_KW_j = pe.Param(model.j,doc='Wirkungsgrad der j-Kraftwerks')

model.BP_f = pe.Param(model.f,doc="Brennstoffpreis (€\MWh_prim)")

model.EF_f = pe.Param(model.f,doc="Emissionsfaktoren (t\MWh_prim)")

model.L_t = pe.Param(model.t,doc='Last Sommer')


def MC_jf_init(model,j,f):
    return (model.BP_f[f]+model.EF_f[f]*model.C_CO2())/model.eta_KW_j[j]

model.MC_jf = pe.Param(model.brennstoffe_jf,rule=MC_jf_init,default=0,doc="Grenzkosten der Erzeugung")


#%% Variablen
model.C_tot = pe.Var(doc='Gesamt Kosten')
model.P_jt = pe.Var(model.j, model.t, within=pe.NonNegativeReals, doc='Einspeise Leistung Kraftwerke')

#%% Zielfunktion 
def cost_rule(model):
    return sum([model.P_jt[j,t]*model.MC_jf[(j,f)] for t in model.t for j in model.j for f in model.f if (j,f) in model.brennstoffe_jf ])

model.cost = pe.Objective(rule=cost_rule)
#%% Zielfunktion Emmsionsminimiert
#def cem_t_rule(model):
#    x = sum([model.P_jt[j,t]*model.EF_f[f] for t in model.t for j in model.j for f in model.f if (j,f) in model.brennstoffe_jf ])
#    return x
#model.cem_t = pe.Objective(rule=cem_t_rule)

#%% Nebenbedingungen
    
def last_t_rule(model,t):
    return sum([model.P_jt[j,t] for j in model.j]) == model.L_t[t] 
               
model.last_t = pe.Constraint(model.t,rule=last_t_rule)


def leistung_jt_rule(model,t,j):
    return model.P_jt[j,t]  <= model.Pmax_j[j] 
               
model.leistung_jt = pe.Constraint(model.t,model.j,rule=leistung_jt_rule)
            

instance = model.create_instance("kep_abstraktes_model_fossil.dat")
#instance.pprint()
opt = pe.SolverFactory("glpk")
results = opt.solve(instance, load_solutions=False,suffixes=['.*'])   # Suffix um z.B Duale Variablen anzuzeigen -> '.*' für alle   
instance.solutions.load_from(results)
#instance.solutions.store_to(results)

#instance.display()
#results.write()
#instance.solutions.load_from(results)
#print(instance.C_tot())

#%%Visualisierung der Ergebnisse 
import numpy as np
import matplotlib.pylab as plt

f = {"b" :(0.12156862745098039, 0.4666666666666667, 0.7058823529411765),  
         "g":(0.17254901960784313, 0.6274509803921569, 0.17254901960784313), 
         "r":(0.8392156862745098, 0.15294117647058825, 0.1568627450980392), 
         "c":(0.09019607843137255, 0.7450980392156863, 0.8117647058823529), 
         "o":(1.0, 0.4980392156862745, 0.054901960784313725),
         "l":(0.5803921568627451, 0.403921568627451, 0.7411764705882353)
         }

x = list(instance.t.value)
key,val=zip(*sorted(instance.P_jt.get_values().items())) 
y=np.array([val() for val in instance.last_t.values()])

#Finde Kraftwerkstyen
seen= []
for j,t in key:
    if j not in seen:
        seen.append(j)

dic = {}
for j in seen:    
    dic[j]=np.array([instance.P_jt[(j,t)]() for t in x])

    
#%% ---
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(x,y,c=f['r'],ls='--', linewidth=2.5)

prev = 0
for i,y in enumerate(reversed(sorted(dic))):
#    ax.plot(x,dic[y],c=f[list(f)[i-1]])
    ax.fill_between(x,prev,prev+dic[y],facecolor=f[list(f)[i]])
    prev = prev+dic[y]

ax.legend(["Last"]+list(dic),bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.grid()
ax.set_xlim([min(x), max(x)])    
ax.set_title("Kraftwerks Mix mit Fossilen ")
ax.set_xlabel("Zeit in Stunden")
ax.set_ylabel("Leistung in MW")    

#%% ---
dual = np.array([results.solution(0).constraint["last_t["+str(t)+"]"]["Dual"] for t in x])
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x,dual,c=f["b"],marker="x")
ax.grid()
ax.set_xlim([min(x), max(x)])
ax.set_ylim([min(dual)-1, max(dual)+1])      
ax.set_title("Spotpreise Last_t")
ax.set_xlabel("Zeit in Stunden")
ax.set_ylabel("Strommarktpreis €/MWh")
