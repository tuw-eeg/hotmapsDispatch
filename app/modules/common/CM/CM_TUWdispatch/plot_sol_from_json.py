# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import matplotlib.pylab as plt
import numpy as np
import os
import json

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))

path2json = path+r"\AD\F16_input\Solution\solution.json"
path2output = path+r"\AD\F16_input\Output_Graphics"

def plot_solutions(path2json=path2json,time="w"):
    if time == "w":
        t = range(1,730*3+1)  #JAN,FEB,MAR
    elif time == "s":
        t = range(730*6-730,730*8-730+1)   # JUN,JUL,AUG
    
    else:
        t = range(0,730*12+1)
        
    try:
        with open(path2json) as f:
            dic = json.load(f)
        
        if os.path.isdir(path2output) == False:
            print("Create Dictionary...")
            os.mkdir(path2output)
            print("Created: "+ path2output)
            
            
    except FileNotFoundError:
        print("\n*********\nThere is no JSON File in this path: "+path2json+"\n*********\n")
        dic={}
        
    
    prev_val = 0        
    for decison_var in list(dic):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        leg=[]
        if type(dic[decison_var]) != str and type(dic[decison_var]) != float:
            for i,val_ind in enumerate(list(dic[decison_var])):
                if type(dic[decison_var][val_ind]) != str and type(dic[decison_var][val_ind]) != float:
                    leg.append(val_ind)
                    y = prev_val+np.array(dic[decison_var][val_ind])
                    ax.fill_between(range(1,len(y)+1),prev_val,y)
                    prev_val = y
                
                    ax.grid()
                    ax.set_xlim([1, len(y)])     
#                    ax.set_title("Decision Variable: "+decison_var)
                    ax.set_title(decison_var)

                    ax.set_xlabel("Time in Hours")
                    ax.set_ylabel("")
                    ax.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    fig.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
            
                else:
#                    ax.set_title("Decision Variable: "+decison_var)
                    ax.set_title(decison_var)
#                    print(decison_var + ": " + str(dic[decison_var]))
                    ax.text(0.5,i/15, val_ind + ": " + str(round(dic[decison_var][val_ind],2))+" MW",
                    verticalalignment='center', horizontalalignment='left',
                    transform=ax.transAxes,
                    color='red', fontsize=10)
                    ax.set_xlim([0,1])
                    ax.set_ylim([0,1])
                    ax.axis('off')
                    fig.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
        else:
            
#            ax.set_title("Decision Variable: "+decison_var)
            ax.set_title(decison_var)
            ax.text(0.5, 0.5, decison_var + ": " + str(dic[decison_var]),
            verticalalignment='center', horizontalalignment='center',
            transform=ax.transAxes,
            color='red', fontsize=22)
            ax.set_xlim([0,1])
            ax.set_ylim([0,1])
            ax.axis('off')
            fig.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
            
        
#%%
#plot_solutions()