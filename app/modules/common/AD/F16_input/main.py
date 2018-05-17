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
# Set investment flag
inv_flag = 0
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
    input data, that are specified in the "\FEAT\F16\input.xlsx" file
    
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
def write_fit(string,profil):
    """
    This function return a dict that uses the string input to specify the 
    
    Parameters:
        string:     str
                    String that specifies the feed in Tarif or Offset
                    Has to be in this form "XXf + XXh""   
                        XX... value (float)
                        f... Fix Price
                        h... Offset
                    like: "20f + 35.05h"
    Return:
        dictionary  dict
                    Returns the dict with spezified Feed in Tarif and or 
                    Fix Price for the given profile
    """
    feed_in_tarif = 0
    fix_price = 0
    string = string.strip()
    if  string != "0" and string !="":
        for string in string.split("+"):
            string = string.strip()
            if string == "":
                continue
            elif string[-1] == 'f':
                try:
                    feed_in_tarif = float(string[:-1])
                except:
                    print("User Input for FiT is wrong,...assuming 0 ")
                    feed_in_tarif = 0
            elif string[-1] == 'h':
                try:
                    fix_price = float(string[:-1])
                except:
                    print("User Input for constant hourly price is wrong,... using variable prices")
                    fix_price = 0
            else:
                print("User Input for electricity is wrong")
                sys.exit()
    if fix_price == 0:    
        return dict(zip(range(1,8760+1),(np.array(list(profil.values()))+feed_in_tarif).tolist()))
    else:
        return dict(zip(range(1,8760+1),[feed_in_tarif+fix_price]*8760))                      
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
    data_hg = pd.read_excel(path_parameter,skiprows=[1])
    tec = list(data_hg.tec.values)
    data_hg = data_hg.set_index("tec").to_dict()
    data_prices_ef = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[1]).fillna(0).set_index("energy_carrier").to_dict()
    data_params = pd.read_excel(path_parameter,"financal and other parameteres",skiprows=[1]).fillna(0).to_dict("records")[0]
    data_hs = pd.read_excel(path_parameter,"Heat Storage",skiprows=[1]).fillna(0)
    tec_hs = list(data_hs.hs_name.values)
    data_hs = data_hs.set_index("hs_name").to_dict()
    data = {**data_hg, **data_prices_ef,**data_params, **data_hs}
    
    # Load user input form "\FEAT\F16\input.xlsx"
    try:
        data_input_params = pd.read_excel(path_parameter2,"Data",skiprows=range(3,5)).fillna(0).drop([np.nan])
    except:
        data_input_params = pd.read_excel(path_parameter2,"Data").fillna(0)
    
    data_input_hg = pd.read_excel(path_parameter2,"Heat Generators",skiprows=range(22,26)).fillna(0)
    data_input_prices_ef = pd.read_excel(path_parameter2,"prices and emmision factors").fillna(0)
    data_input_hs = pd.read_excel(path_parameter2,"Heat Storage").fillna(0)
    
    # Generate Mapping tables to distinguish the input data
    input_list_mapper = return_mapper()
    input_price_list_mapper = return_mapper("prices and emmision factors")
    parameter_list_mapper = return_mapper("financal and other parameteres")
    hs_mapper = return_mapper("Heat Storage")
    
     # Overwrite default values with user input data 
    overwrite(data,data_input_hg,"name",input_list_mapper)
    overwrite(data,data_input_prices_ef,"energy carrier",input_price_list_mapper)
    overwrite(data,data_input_params,"",parameter_list_mapper)
    overwrite(data,data_input_hs,"name",hs_mapper)

    # Load externel data like demand, radiation,temperature, electricity price     
    demand = pickle.load(open(path2data+r"\load_profiles.dat", "rb"))[init_data]    
    demand_neu = demand / sum(demand) * float(data_input_params["Total Demand[ MWh]"].values[0])
    data["demand_th"] = dict(zip(range(1,len(demand_neu)+1),demand_neu.tolist()))
    data["radiation"] = return_dict("radiation_profiles")
    data["temp"] = return_dict("temperature_profiles")
    
    #%%
    fit = data_input_hs = pd.read_excel(path_parameter2,"FiT_Offset").fillna(0)
    
                            
    data["energy_carrier_prices"]["electricity"] = write_fit(data["energy_carrier_prices"]["electricity"],return_dict("price_profiles"))
    data["sale_electricity"] = write_fit(str(fit["Sale Electricity Price"].values[0]),return_dict("price_profiles"))
    data["temp"] = write_fit(str(fit["Temperature"].values[0]),data["temp"])
    data["radiation"]  = write_fit(str(fit["Radiation"].values[0]),data["radiation"])
    data["demand_th"] = write_fit(str(fit["Demand"].values[0]),data["demand_th"])
    
    #%%
    data["tec"] = tec
    data["tec_hs"] = tec_hs
    
    data["all_heat_geneartors"] = data["tec"] + data["tec_hs"]

    return data, inv_flag 


if __name__ == "__main__":
    print('Loading Data...')
    val,flag = load_data()
    print('Loading done')
    
    

