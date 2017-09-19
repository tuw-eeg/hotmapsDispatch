# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:54:44 2017

@author: root
"""
import matplotlib.pylab as plt
import numpy as np
import os
import json
path2solution = os.path.split(os.path.abspath("__file__"))[0]+"\Solution\solution.json"


def plot_solutions(path2json=path2solution):
    try:
        with open(path2json) as f:
            dic = json.load(f)
        path2output = os.path.split(os.path.abspath("__file__"))[0]+"\Output_Graphics"

        if os.path.isdir(path2solution) ==False:
            print(os.path.isdir(path2solution))
            print(path2solution)
            
            if os.path.isdir(path2output) ==False:
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
        
        for val_ind in list(dic[decison_var]):
            if type(dic[decison_var][val_ind]) != str and type(dic[decison_var][val_ind]) != float:
                leg.append(val_ind)
                y = prev_val+np.array(dic[decison_var][val_ind])
                ax.fill_between(range(1,len(y)+1),prev_val,y)
                prev_val = y
            
                ax.grid()
                ax.set_xlim([1, len(y)])     
                ax.set_title("Decision Variable: "+decison_var)
                ax.set_xlabel("Time in Hours")
                ax.set_ylabel("")
                ax.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                fig.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
            else:
                ax.set_title("Decision Variable: "+decison_var)
    #            clsprint(decison_var + ": " + str(dic[decison_var]))
                ax.text(0.5, 0.5, val_ind + ": " + str(round(dic[decison_var][val_ind],2))+" MW",
                verticalalignment='center', horizontalalignment='center',
                transform=ax.transAxes,
                color='red', fontsize=22)
                ax.set_xlim([0,1])
                ax.set_ylim([0,1])
                ax.axis('off')
                fig.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
                
#%%
plot_solutions()