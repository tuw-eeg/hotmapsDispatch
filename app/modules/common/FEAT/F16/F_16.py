# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%%ppp
import os
import sys
import pandas as pd
import numpy as np
import json

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

from AD.F16_input.main import load_data 
from CM.CM_TUWdispatch.simpel_plot import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch
#%%
def execute(data,inv_flag):
    val = dispatch.main(data,inv_flag) 
    return val 
#%%
if __name__ == "__main__":
    print('calculation started')   
    data,inv_flag = load_data()    
    solutions,instance,results = execute(data,inv_flag)
    if solutions != None:
        plot_solutions()    
    print('calculation done')
