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

#%%

def get_cmap(n, name='tab10'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


def bar_chart(dic,path2output,decison_var,fig,ax):
    ax.set_title(decison_var)
    legend = list(dic)
    val = list(dic.values())
    k = [i for i,x in enumerate(val) if x!=0]
    legend= [legend[i] for i in k]
    val= [val[i] for i in k]
    cmap = get_cmap(len(k))
    colors = [cmap(i) for i in range(len(k))]
    rect = ax.bar(range(len(k)),val,color=colors)
    ax.set_xticks(range(len(k)))
    ax.set_xticklabels(legend)
    ax.legend(rect,legend,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    fig.savefig(path2output+r"\\"+decison_var+"_absolut_bar_chart.png",
                dpi=300,bbox_inches='tight')
    
def pie_chart(dic,path2output,decison_var,fig,ax): 
    ax.set_title(decison_var)          
    labels = list(dic)
    sizes = np.array(list(dic.values()))/sum(dic.values())
    mask = sizes>0
    labels = list(itertools.compress(labels, mask))
    sizes = sizes[mask]
    explode = 0.1*np.ones((len(labels),))
    ax.pie(sizes, explode = explode,labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax.axis('equal')
    fig.savefig(path2output+r"\\"+decison_var+"_pie_chart.png",dpi=300,
                bbox_inches='tight')

def stack_chart(fig,ax,t,dic,y,legend,decison_var,flag=0):
    ax.plot(t,np.array(dic["Heat Demand"])[t],"k")
    ax.stackplot(t,y)
    ax.grid()
    ax.set_xlim([t[0], t[-1]])     
    ax.set_title(decison_var)
    ax.set_xlabel("Time in Hours")
    ax.set_ylabel("")
    ax.legend(legend,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if flag:
        name= "_summer.png"
    else:
        name= "_winter.png"
    fig.savefig(path2output+r"\\"+decison_var+name,dpi=300,bbox_inches='tight')
    
#%%    
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
path2json = path+r"\AD\F16_input\Solution\solution.json"
path2output = path+r"\AD\F16_input\Output_Graphics"
#%%
def plot_solutions(path2json=path2json):
    
    tw = range(1,8000+1)  #JAN
    ts = range(730*5,730*5+336+1)   # Summer
        
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
    
    decison_var="Thermal Power Energymix" 
    legend = list(dic["Thermal Power Energymix"].keys())
    y1 = np.array(dic[decison_var][legend[0]])[tw]
    y2 =  np.array(dic[decison_var][legend[0]])[ts] 

    for val_ind in legend[1:]:
        y1=np.row_stack((y1,np.array(dic[decison_var][val_ind])[tw]))
        y2=np.row_stack((y2,np.array(dic[decison_var][val_ind])[ts]))
        
    legend.insert(0,"Heat Demand")


    fig1,ax1 = plt.subplots()
    stack_chart(fig1,ax1,tw,dic,y1,legend,decison_var)
    
    fig2,ax2 = plt.subplots()
    stack_chart(fig2,ax2,ts,dic,y2,legend,decison_var,1)
    
    fig3, ax3 = plt.subplots()
    decison_var ="Heat Price"
    ax3.plot(dic[decison_var])
    ax3.grid()
    ax3.set_title(decison_var)
    ax3.set_xlabel("Time in Hours")
    ax3.set_ylabel("Heat Price in EUR/MWh")
    ax3.legend(["Heat Price"],bbox_to_anchor=(1.05, 1), loc=2, 
               borderaxespad=0.)
    fig3.savefig(path2output+r"\\"+decison_var+".png",dpi=300,
                 bbox_inches='tight')
    
    fig4, ax4 = plt.subplots()
    decison_var = "Thermal Generation Mix"
    pie_chart(dic[decison_var],path2output,decison_var,fig4,ax4)
    
    fig5, ax5 = plt.subplots()
    decison_var = "Installed Capacities"
    pie_chart(dic[decison_var],path2output,decison_var,fig5,ax5)
    
    fig6, ax6 = plt.subplots()
    bar_chart(dic[decison_var],path2output,decison_var,fig6,ax6)
            
                          
#%%
plot_solutions()