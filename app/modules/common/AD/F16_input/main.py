# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import pickle

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)


def load_data(path2data = os.path.split(os.path.abspath(__file__))[0]):
#    print(path2data)
    val = pickle.load(open(path2data+r"\data.dat", "rb"))
    inv_flag = 0
    return val, inv_flag 


if __name__ == "__main__":
    print('Loading Data...')
    val,flag = load_data()
#    print(result)
    print('Loading done')
    
    

