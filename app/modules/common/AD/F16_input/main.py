# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle

#%% Get current absolute file path 
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
#%% Setting Global default paramters and default paths
path2data = os.path.split(os.path.abspath(__file__))[0]
# path to user input data
path_parameter2 = path + r"\FEAT\F16\input.xlsx"
# path to default values
path_parameter = path2data + r"\DH_technology_cost.xlsx"
# default key for the extern paramters (load,price,radiation,temperature)
init_data=("Wien",2016)
#%% Function definition for loading,writing and mapping the default values
def return_dict(name_dat,init_data=init_data):
    """
    This function loads "pickle" data and converts the data into dictionary 
    with one-based indexing for "pyomo" 
    
    Parameters:
        name:           string 
                        name of the "dat" file : 
                            i.e: "pirces" for the <prices.dat>-file 
                        
        init_data:      tuple
                        default: init_data (global variable)
                        key for the data to load: i.e: ("Wien",2016) 
    Returns:
        one-based-dictionary:   dict
                                This will be converted data to a 
                                one-based indexed dictionary 
    
    """
    val = pickle.load(open(path2data+r"\\"+name_dat+".dat", "rb"))[init_data]
    return dict(zip(range(1,len(val)+1),val.tolist()))

def return_mapper(sheet_name="",path2file=path_parameter):
    """
    This function creates a mapping dictionary that is specifiedy in 
    "DH_technology_cost.xlsx" by the first two rows
    This mapping table is used to map the user input data to the model data 
    
    Parameters:
        sheet_name:     string
                        sheet name of "DH_technology_cost.xlsx"
    Returns:
        mapping_table:  dict:
                        THis is the mapping dictionary
    """
    data1 = pd.read_excel(path2file)[0:1]
    if sheet_name !="":  
        data1 = pd.read_excel(path2file,sheet_name)[0:1]

    return dict(zip(data1.values[0].tolist(),list(data1)))

def overwrite(old,new,value,mapper):
    """
    This function overwrite the inital data values of the model with the user 
    input data, that are specified in the "\FEAT\F16\input.xlsx"
    
    Parameters:
        old:        dict
                    The initial data dictionary for the model
                
        new:        padas_DataFrame 
                    DataFrame that contains the user input data
                
        value:      string
                    name of the first column in that is specified in 
                    "\FEAT\F16\input.xlsx"
                    
        mapper:     dict
                    This dictionary is used to map the user input data to the 
                    model data 
     Returns:
        This function doesnt have return values            
    """
    dic = new.to_dict()
    if value !="" :
        dic = new.set_index(value).to_dict()
    for key in list(dic):
        if value !="":
            old[mapper[key]]=dic[key]
        else:
            old[mapper[key]]=list(dic[key].values())[0]
#%%           
def load_data():
    """
    This function returns the data for the dispatch model 
    - Default Values are specified in DH_technology_cost.xlsx
    - User input Data can be specified in  "\FEAT\F16\input.xlsx"
    - extern data saved as "dat" files
          i.e:    1. load_profiles.dat
                  2. prices.dat
                  3. radiation_profiles.dat
                  4. temperature_profile.dat
         
            each file contains a dictionary, whos elemenst are the anual profiles,
            that are repesented by numpy arrays 
            the keys of the dictionarys are as as follows generated:
                ( shorthand symbol <string> , year <int> ), i.e: ("UK",2012)
            
            in order to distungish between the symbols, each file has a 
            mapping table that are established also as "dat" Files: 
              i.e:    1. load_name_map.dat
                      2. price_name_map.dat
                      3. radiation_name_map.dat
                      4. temperature_name_map.dat
             
                each file contains a dictionary, whos elemenst are strings that 
                describe the shorthand symbols. i.e: {"UK":"United Kingdom"}
    Paramters: 
        No paramters needed

    Returns:
        data:           dict
                        This is the model data
                        
        inv_flag:       int or bool
                        default: 0
                        i.e.: 0 or False for pure Dispatch without investment
                              1 or True for Dispacth with investment
    """
    # Load Initial Data from "DH_technology_cost.xls"
    data1 = pd.read_excel(path_parameter,skiprows=[1])
    tec = list(data1.tec.values)
    data1 = data1.set_index("tec").to_dict()
    data2 = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[1]).fillna(0).set_index("energy_carrier").to_dict()
    data3 = pd.read_excel(path_parameter,"financal and other parameteres",skiprows=[1]).fillna(0).to_dict("records")[0]
    data_hs = pd.read_excel(path_parameter,"Heat Storage",skiprows=[1]).fillna(0)
    tec_hs = list(data_hs.hs_name.values)
    data_hs = data_hs.set_index("hs_name").to_dict()
    data = {**data1, **data2,**data3, **data_hs}
    
    # Load user input form "\FEAT\F16\input.xlsx"
    try:
        data4 = pd.read_excel(path_parameter2,"Data",skiprows=range(3,5)).fillna(0).drop([np.nan])
    except:
        data4 = pd.read_excel(path_parameter2,"Data").fillna(0)
    
    data5 = pd.read_excel(path_parameter2,"Parameter for Powerplants",skiprows=range(21,26)).fillna(0)
    data6 = pd.read_excel(path_parameter2,"prices and emmision factors").fillna(0)
    
    # Generate Mapping tables to distinguish the input data
    input_list_mapper = return_mapper()
    input_price_list_mapper = return_mapper("prices and emmision factors")
    parameter_list_mapper = return_mapper("financal and other parameteres")
    
     # Overwrite default values with user input data 
    overwrite(data,data5,"name",input_list_mapper)
    overwrite(data,data6,"energy carrier",input_price_list_mapper)
    overwrite(data,data4,"",parameter_list_mapper)

    # Load externel data like demand, radiation,temperature, electricity price     
    demand = pickle.load(open(path2data+r"\load_profiles.dat", "rb"))[init_data]    
    demand_neu = demand / sum(demand) * float(data4["Total Demand[ MWh]"].values[0])
    data["demand_th"] = dict(zip(range(1,len(demand_neu)+1),demand_neu.tolist()))
    data["radiation"] = return_dict("radiation_profiles")
    data["temp"] = return_dict("temperature_profile")
    data["energy_carrier_prices"]["electricity"] = return_dict("prices")
    data["tec"] = tec
    data["tec_hs"] = tec_hs
    
    # Set investment flag
    inv_flag = 0
    
    return data, inv_flag 


if __name__ == "__main__":
    print('Loading Data...')
    val,flag = load_data()
    print('Loading done')
    
    

