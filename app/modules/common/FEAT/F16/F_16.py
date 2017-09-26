# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%%
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

import CM.CM_TUWdispatch.run_cm as dispatch
#%%
def execute(data):
    val = dispatch.main(data) 
    return val 
#%%
if __name__ == "__main__":
    print('calculation started')
    
    
    data = load_data()
    
    result = execute(data)
    print(str(sum([result.x_th_jt[j,5]() for j in result.j])))
    
    print('calculation done')
