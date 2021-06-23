# -*- coding: utf-8 -*-
"""
# =============================================================================
# Copyright (c) <year> <copyright holders>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

Created on Wed Jan 15 15:15:19 2020

@author: hasani

Description: <insert here the description of your script>

"""
# %%
# =============================================================================
# IMPORT NEEDED MODULES
# =============================================================================
import numpy as np
import pandas as pd
from pathlib import Path
import pprint as pp
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import altair as alt

alt.renderers.enable('svg')
alt.themes.enable('default')

# =============================================================================
# GLOBAL PATHS AND VARIABLES
# =============================================================================
file_path = Path(__file__).parent.resolve()

systemp = {"Cluster 1":dict(code="VL(150/70)RL(70/58)",
                                   flow_temp=(150,70,-10,10),
                                   return_temp=(70,58,-10,10)
                                   ),
            "Cluster 2":dict(code="VL(100/70)RL(70/60)",
                                   flow_temp=(100,70,-10,10),
                                   return_temp=(70,60,-10,10)
                                   ),
            "Cluster 3":dict(code="VL(100/70)RL(70/60)",
                                   flow_temp=(100,70,-10,10),
                                   return_temp=(70,60,-10,10)
                                   ),
            "Cluster 4":dict(code="VL(100/70)RL(70/60)",
                                   flow_temp=(100,70,-10,10),
                                   return_temp=(70,60,-10,10)
                                   ),
            "Cluster 5":dict(code="VL(100/70)RL(70/60)",
                                   flow_temp=(100,70,-10,10),
                                   return_temp=(70,60,-10,10)
                                   ),
            "Cluster 6":dict(code="VL(90/70)RL(60/60)",
                                   flow_temp=(90,70,-10,10),
                                   return_temp=(60,60,-10,10)
                                   ),
            "Cluster 7":dict(code="VL(90/70)RL(60/60)",
                                   flow_temp=(90,70,-10,10),
                                   return_temp=(60,60,-10,10)
                                   ),
            "Cluster 8":dict(code="VL(90/70)RL(60/60)",
                                   flow_temp=(90,70,-10,10),
                                   return_temp=(60,60,-10,10)
                                   ),
            "Cluster 9":dict(code="VL(90/70)RL(60/60)",
                                   flow_temp=(90,70,-10,10),
                                   return_temp=(60,60,-10,10)
                                   ),
            "Cluster 10":dict(code="VL(90/70)RL(60/60)",
                                   flow_temp=(90,70,-10,10),
                                   return_temp=(60,60,-10,10)
                                   ),
                }
# =============================================================================
#         
# =============================================================================
# =============================================================================
# FUNCTIONS
# =============================================================================

# =============================================================================
# functions for reading and writing hotmaps dispatch model dat files
# =============================================================================
def opendat(string,path2dat):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"rb") as file:
        profile = pickle.load(file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"rb") as file:
        mapper = pickle.load(file)

    return profile, mapper

def savedat(profile, mapper, string, path2dat):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"wb") as file:
        pickle.dump(profile,file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"wb") as file:
        pickle.dump(mapper,file)
# =============================================================================
#         
# =============================================================================
def heizkurve(t_max,t_min,t_amb_min,t_amb_max):
    k = abs ( (t_max-t_min) / (t_amb_max-t_amb_min) ) 
    d =  t_max + k*t_amb_min
    return k,d

def flow_return_temp(t_max,t_min,t_amb_min,t_amb_max,t_amb):
    k,d = heizkurve(t_max,t_min,t_amb_min,t_amb_max)
    y = d - k * t_amb
    y[y >= t_max] = t_max
    y[y <= t_min] = t_min
    return y

def add_flow_return_temp(y_tamb,dat_path,output_path,
                         heizkurven=systemp,kuerzel="",save=False,
                         new = False,year=0):
    
    profile_return, mapper_return = opendat("return_temperature", dat_path) if not new else ({},{})
    profile_flow, mapper_flow = opendat("inlet_temperature", dat_path) if not new else ({},{})
    
    for name,dictionary in heizkurven.items():
        y_r = flow_return_temp(*dictionary["return_temp"],y_tamb)
        y_f = flow_return_temp(*dictionary["flow_temp"],y_tamb)
        profile_return[(name,year)] = y_r
        profile_flow[(name,year)] = y_f
        mapper_return[name] = dictionary["code"]+kuerzel
        mapper_flow[name] = dictionary["code"]+kuerzel
    
    if save:
        profile_return[("default",2016)] = np.zeros((8760))
        profile_flow[("default",2016)] = np.zeros((8760))
        mapper_return["default"] = "Wien"
        mapper_flow["default"] = "Wien"
        
        savedat(profile_return, mapper_return, "return_temperature", output_path)  
        savedat(profile_flow, mapper_flow, "inlet_temperature", output_path)  
    
    return [profile_return,profile_flow],[mapper_return,mapper_flow]



def plot_1heizkurve(ax,name,dictionary,flow=True):
    t_amb = np.linspace(-20,35,100)
    y = flow_return_temp(*dictionary["flow_temp" if flow else "return_temp"],t_amb)
    ax.plot(t_amb,y,label=name)
#    ax.legend()
    ax.grid(b=True, which='major')
    ax.set_xlabel('ambient temperature [°C]')
    ax.set_ylabel("Flow Temperature [°C]"if flow else 'Return Temperature [°C]')
#    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax.set_title(name)
    data = pd.DataFrame(dict(name=[name]*len(t_amb),
                               topic=["Flow System Temperature"if flow else"Return System Temperature" ]*len(t_amb),ambient_temperatur=t_amb,value=y))
    return ax,data

def plot_heizkurven(ax,flow,heizkurven):
    data  = []
    for name,dictionary in heizkurven.items():
        ax,df=plot_1heizkurve(ax,name,dictionary,flow)
        data += [df]
    data=pd.concat(data)
    return ax,data

def show_system_temperatures(system_temperatures=systemp):    
    fig1, ax = plt.subplots()
    ax,data1=plot_heizkurven(ax,False,heizkurven=system_temperatures)
    ax.set_title("System Return Temperature Curve")
    
    fig2, ax = plt.subplots()
    ax,data2=plot_heizkurven(ax,True,heizkurven=system_temperatures)
    ax.set_title("System Flow Temperature Curve")
    data = pd.concat([data1,data2])
    return data,fig1,fig2


def show_mean_values(data):
    chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("name",sort=alt.EncodingSortField(field="value", op="mean",order='ascending')),
            y=alt.Y("mean(value)"),
            color=alt.Color("code",sort=alt.EncodingSortField('value', op='mean', order='ascending'))
            ).properties(width=400,height=400).resolve_scale(x='independent',y='shared').interactive()
    chart.serve()
        
def tidyData(profiles,mappers,interest,name):
    list0 = interest if interest!=[] else "".join(list(mappers[0].values())).split(f" {name}")
    list1 = interest if interest!=[] else "".join(list(mappers[1].values())).split(f" {name}")
    print(list0,list1)
    x=[pd.DataFrame(dict(code=[key[0]]*len(array),
            name=[mappers[0][key[0]]]*len(array),
            topic=["Mean Return Temperature"]*len(array),
            time=range(len(array)),
            value=array)) for key,array in profiles[0].items() if mappers[0][key[0]].split(f" {name}")[0].strip() in list0 ]
    y=[pd.DataFrame(dict(code=[key[0]]*len(array),
            name=[mappers[1][key[0]]]*len(array),
            topic=["Mean Flow Temperature"]*len(array),
            time=range(len(array)),
            value=array,)) for key,array in profiles[1].items() if mappers[1][key[0]].split(f" {name}")[0].strip()  in list1]
    data = pd.concat([pd.concat(x),pd.concat(y)]) 
    data["name"]= data.name.str.split(f" {name}",expand=True)[0]
    return data

def show_all(data1,data2):
    chart1=alt.Chart(data2).mark_line().encode(x="time",y="value",color="name",column="topic",row="name").resolve_scale(x='independent',y='independent').interactive()
    chart2=alt.Chart(data1).mark_line().encode(x="ambient_temperatur",y="value",color="name",column="topic",row="name").resolve_scale(x='independent',y='independent').interactive()
    
    chart = chart1 | chart2
    chart.serve()
def show_systemps(data):
    return alt.Chart(data).mark_line().encode(x="ambient_temperatur",y="value",color="name",column="topic").interactive().serve()
# =============================================================================
# MAIN
# =============================================================================
def open_profiles(dat_path):
    profile_return, mapper_return = opendat("return_temperature", dat_path) 
    profile_flow, mapper_flow = opendat("inlet_temperature", dat_path)    
    df_return = pd.DataFrame(profile_return)
    df_flow = pd.DataFrame(profile_flow)
    return df_return,df_flow

if __name__ == "__main__":
    dat_path = file_path
    temp_profile, temp_mapper = opendat("temperature",dat_path)
    for i,((name,_year),y_tamb) in enumerate(temp_profile.items()):
        if name == "default":
            continue
        profiles,mappers = add_flow_return_temp(y_tamb, dat_path, output_path=dat_path,
                                                kuerzel=f" {name}",save=True,
                                                new=False if i else True,
                                                heizkurven={name:systemp[name]})
    df_return,df_flow = open_profiles(dat_path)
    