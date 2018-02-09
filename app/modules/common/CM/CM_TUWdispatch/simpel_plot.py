# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import matplotlib.pylab as plt
import numpy as np
import os
import json
import itertools
import pandas as pd
#%%
demand_f = 0.8
#%%
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def colormapping(tec):
    colors = get_cmap(len(tec))
    color_map = {val:colors(i) for i,val in enumerate(tec)}
    return color_map

def bar_chart(dic,path2output,decison_var,fig,ax,cmap):
    ax.set_title(decison_var)
    legend = list(dic)
    val = list(dic.values())
    k = [i for i,x in enumerate(val) if x!=0]
    legend= [legend[i] for i in k]
    val= [val[i] for i in k]
#    cmap = get_cmap(len(k))
#    colors = [cmap(i) for i in range(len(k))]
    colors = [cmap[i] for i in legend]
    rect = ax.bar(range(len(k)),val,color=colors)
    ax.set_xticks(range(len(k)))
    ax.set_xticklabels(legend)
    ax.legend(rect,legend,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax.grid(axis="y")
    fig.savefig(path2output+r"\\"+decison_var+"_absolut_bar_chart.png",
                dpi=300,bbox_inches='tight')
    
def pie_chart(dic,path2output,decison_var,fig,ax,cmap): 
    ax.set_title(decison_var)          
    labels = list(dic)
    sizes = np.array(list(dic.values()))/sum(dic.values())
    mask = sizes>0
    labels = list(itertools.compress(labels, mask))
    sizes = sizes[mask]
    explode = 0.1*np.ones((len(labels),))
    colors = [cmap[i] for i in labels]
    ax.pie(sizes, explode = explode,labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90,colors=colors,)
    ax.axis('equal')
    fig.savefig(path2output+r"\\"+decison_var+"_pie_chart.png",dpi=300,
                bbox_inches='tight')

def stack_chart(fig,ax,t,dic,y,legend,decison_var,path2output,cmap,flag=0):
    ax.plot(t,demand_f*np.array(dic["Heat Demand"])[t],"k",linewidth=0.5)
    null = [i for i,x in enumerate(range(y.shape[0])) if np.sum(y[x,:]) !=0]
    mc_mask=np.argsort(np.array(dic["Marginal Costs"])[null])
    
    legend = np.array(legend)[null][mc_mask].tolist()
    colors = [cmap[i] for i in legend]
    legend.insert(0,"Heat Demand")
    ax.stackplot(t,y[null][mc_mask],colors=colors)
    ax.grid()
    ax.set_xlim([t[0], t[-1]])     
 
    ax.set_xlabel("Time in Hours")
    ax.set_ylabel(r"$MWh_{th}$")
    ax.legend(legend,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax2 = ax.twinx()
    ax2.plot(t,demand_f*np.array(dic["Electricity Price"])[t],color=plt.cm.get_cmap("tab20b", 1)(1),linewidth=0.5)
    ax2.set_ylabel("Electricity Price in "+r"$\frac{€}{MWh}$",color=plt.cm.get_cmap("tab20b", 1)(1))
    ax2.tick_params(axis='y', colors=get_cmap(1)(1))
    
    name = "_over_year.png"
    if flag =="s":
        name= "_summer.png"
    if flag == "w":
        name= "_winter.png"
    
    ax.set_title(decison_var+name)
    fig.savefig(path2output+r"\\"+decison_var+name,dpi=300,bbox_inches='tight')
#%%
def load_duration_curve(fig,ax,t,dic,y,legend,decison_var,path2output,cmap):
    summe = np.sum(y,0)
    idx = np.argsort(-summe)
    dauerkurve = y[:,idx]
    ax.plot(t,summe[idx],"k",linewidth=0.5)
    null = [i for i,x in enumerate(range(y.shape[0])) if np.sum(y[x,:]) !=0]
    mc_mask=np.argsort(np.array(dic["Marginal Costs"])[null])
    legend = np.array(legend)[null][mc_mask].tolist()
    colors = [cmap[i] for i in legend]
    legend.insert(0,"Dauerkurve")
    ax.stackplot(t,dauerkurve[null][mc_mask],colors=colors)
    ax.grid()
    ax.set_xlim([t[0], t[-1]])     
    ax.set_title("Load Duration Curve")
    ax.set_xlabel("Time in Hours")
    ax.set_ylabel(r"$MWh_{th}$")
    ax.legend(legend,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        
    fig.savefig(path2output+r"\\load_duration_curve.png",dpi=300,bbox_inches='tight')
   
#%%
def matrix(dic,decison_var,legend,t):
    y = np.array(dic[decison_var][legend[0]])[t]
    for val_ind in legend[1:]:
        y=np.row_stack((y,np.array(dic[decison_var][val_ind])[t]))
    
    if len(y.shape) == 1:
        y=y.reshape((1,y.shape[0]))
    return y    
#%%   
def plot_tabel(dic,decision_vars,path2output):
    fig, ax = plt.subplots()
    text = [[str(round(dic[decison_var],2))] for decison_var in decision_vars]
    ax.table(cellText= text,
                  rowLabels= decision_vars,
                  loc='center')    
    ax.axis('off') 
    fig.subplots_adjust(top=0.88,bottom=0.085,left=0.51,right=0.75,hspace=0.18,
                         wspace=0.185)
    fig.savefig(path2output+r"\\solver_output.png",dpi=300,bbox_inches='tight')
#%%
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
path2json = path+r"\AD\F16_input\Solution\solution.json"
path2output = path+r"\AD\F16_input\Output_Graphics"
#%%
def plot_solutions(path2json=path2json):
    
    tw = range(0,350)  #JAN
    ts = range(730*5,730*5+336+1)   
    t = range(0,8760)
        
    try:
        with open(path2json) as f:
            dic = json.load(f)
        
        if os.path.isdir(path2output) == False:
            print("Create Dictionary...")
            os.mkdir(path2output)
            print("Created: "+ path2output)
            
            
    except FileNotFoundError:
        print("\n*********\nThere is no JSON File in this path: "+
              path2json+"\n*********\n")
        return True
    #%%
    cmap = colormapping(dic["Technologies"])
    
    
    decison_var="Thermal Power Energymix" 
    legend = list(dic["Thermal Power Energymix"].keys())
    
    y1 = matrix(dic,decison_var,legend,tw)
    y2 = matrix(dic,decison_var,legend,ts)  
    y3 = matrix(dic,decison_var,legend,t)
    

    fig1,ax1 = plt.subplots()
    stack_chart(fig1,ax1,tw,dic,y1,legend,decison_var,path2output,cmap,"w")
    
    fig2,ax2 = plt.subplots()
    stack_chart(fig2,ax2,ts,dic,y2,legend,decison_var,path2output,cmap,"s")
    
    fig8,ax8 = plt.subplots()
    stack_chart(fig8,ax8,t,dic,y3,legend,decison_var,path2output,cmap,"t")
    
    fig9,ax9 = plt.subplots()
    load_duration_curve(fig9,ax9,t,dic,y3,legend,decison_var,path2output,cmap)
    
    fig3, ax3 = plt.subplots()
    decison_var ="Heat Price"
    ax3.plot(dic[decison_var])
    ax3.grid()
    ax3.set_title(decison_var)
    ax3.set_xlabel("Time in Hours")
    ax3.set_ylabel("Heat Price in "+r"$\frac{€}{MWh}$")
    ax3.legend(["Heat Price"],bbox_to_anchor=(1.05, 1), loc=2, 
               borderaxespad=0.)
    fig3.savefig(path2output+r"\\"+decison_var+".png",dpi=300,
                 bbox_inches='tight')
    
    fig4, ax4 = plt.subplots()
    decison_var = "Thermal Generation Mix"
    pie_chart(dic[decison_var],path2output,decison_var,fig4,ax4,cmap)
    
    fig5, ax5 = plt.subplots()
    decison_var = "Installed Capacities"
    pie_chart(dic[decison_var],path2output,decison_var,fig5,ax5,cmap)
    
    fig6, ax6 = plt.subplots()
    bar_chart(dic[decison_var],path2output,decison_var,fig6,ax6,cmap)
    
    fig7, ax7 = plt.subplots()
    decison_var = "Specific Capital Costs of installed Capacities"
    bar_chart(dic[decison_var],path2output,decison_var,fig7,ax7,cmap)
            
    decision_vars = ["Electricity Production by CHP",
                 "Thermal Production by CHP",
                 "Mean Value Heat Price",
                 "Median Value Heat Price",
                 "Electrical Consumption of Heatpumps and Power to Heat devices",
                 "Maximum Electrical Load of Heatpumps and Power to Heat devices",
                 "Revenue From Electricity",
                 "Ramping Costs",
                 "Operational Cost",
                 "Invesment Cost",
                 "Electrical Peak Load Costs",
                 "Variable Cost CHP's",
                 "Total Variable Cost",
                 "Total Costs"]
    
    plot_tabel(dic,decision_vars,path2output)
#%%
#plot_solutions()