# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%%
import os
import sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

from AD.F16_input.main import load_data 
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch
#%%
def execute(data,inv_flag,selection=[[],[]],demand_f=1):
    val = dispatch.main(data,inv_flag,selection,demand_f) 
    return val 
#%%
if __name__ == "__main__":
    print('calculation started')   
    data,inv_flag = load_data()   
    solutions,instance,results = execute(data,inv_flag,selection=[[],[]])
    if solutions == "Error1":
        print( 'No Capacities installed !!!')
    elif solutions == "Error2":
        print("The installed capacities are not enough to cover the load !!!" )
    elif solutions == "Error3":
        print("Error: Infeasible or Unbounded model !!!")
    elif solutions == None:
        print("Error: Something get Wrong")
    else:
        print('calculation done')
        tabs = plot_solutions(show_plot=True,solution=solutions)   
        if tabs == "Error4":
            print("Error @ Ploting  !!!")
        
