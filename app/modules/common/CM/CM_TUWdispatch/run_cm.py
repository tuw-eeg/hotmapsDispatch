# -*- coding: utf-8 -*-

import os
import time
import sys
import numpy as np

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
	
import CM.CM_TUWdispatch.simpel_dispatch as simpel_dispatch
from CM.CM_TUWdispatch.save_sol_to_json import save_sol_to_json

        
def main(data,inv_flag,selection,demand_f,solver):
    
    instance,results = simpel_dispatch.run(data,inv_flag,selection,demand_f,solver)
    
    if instance == "Error1" or instance == "Error2":
        return instance,results,None 
    
    if instance == "Error3":
        return "Error3",None,None
    
    if instance == None and type(results) == str:
        return None,results,None    

    
    solutions = save_sol_to_json(instance,results,inv_flag)
    
    if solutions == "Error3#":
        return solutions,instance,results 
        
    return solutions,instance,results 

if __name__ == "__main__":
    print('calculation started')
