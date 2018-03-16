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


path_parameter2 = path + r"\FEAT\F16\input.xlsx"
path2data = os.path.split(os.path.abspath(__file__))[0]
path_parameter = path2data + r"\DH_technology_cost.xlsx"

def load_data(path2data = path2data):
#    print(path2data)   
    val = pickle.load(open(path2data+r"\data.dat", "rb"))
    data1 = pd.read_excel(path_parameter,skiprows=[1])
    tec = list(data1.tec.values)
    data1 = data1.set_index("tec").to_dict()
    data2 = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[1]).fillna(0)
    data2 = data2.set_index("energy_carrier").to_dict()
    data3 = pd.read_excel(path_parameter,"financal and other parameteres").fillna(0)
    data3 = data3.to_dict("records")[0]
    data = {**data1, **data2,**data3}
    
    data4 = pd.read_excel(path_parameter2,"Data",skiprows=range(2,4)).fillna(0)
    data5 = pd.read_excel(path_parameter2,"Parameter for Powerplants",skiprows=range(21,26)).fillna(0)
    data6 = pd.read_excel(path_parameter2,"prices and emmision factors").fillna(0)
    
    dic5 = data5.set_index("name").to_dict()
    data1 = pd.read_excel(path_parameter)[0:1]
    input_list_mapper = dict(zip(data1.values[0].tolist(),list(data1)))
    for key in list(dic5):
        data[input_list_mapper[key]]=dic5[key]
        
    dic6=data6.set_index("energy_carrier").to_dict()
    for key in list(dic6):
        data[key]=dic6[key]
    
    for key in list(data4):
        data[key]= data4[key].values[0]
        
    demand = np.array(list(val["demand_th"].values()))
    sum_demand = sum(demand)
    demand_neu = demand / sum_demand * float(data4.total_demand.values[0])
    
    
    data["demand_th"] = dict(zip(range(1,len(demand_neu)+1),demand_neu.tolist()))
    data["radiation"] = val["radiation"]
    data["temp"] = val["temp"]
    data["energy_carrier_prices"]["electricity"] = val["energy_carrier_prices"]["electricity"]
    data["tec"] = tec
    inv_flag = 0
    
    
    
    return data, inv_flag 


if __name__ == "__main__":
    print('Loading Data...')
    val,flag = load_data()
#    print(result)
    print('Loading done')
    
    

