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
import pickle
from threading import Thread

#%% Get current absolute file path
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
#%% Setting Global default paramters and default paths
path2data = os.path.split(os.path.abspath(__file__))[0]
# path to user input data
path_parameter2 = os.path.join(path, "FEAT", "F16", "input.xlsx")
# path to default values
path_parameter = os.path.join(path2data, "DH_technology_cost.xlsx")
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
    with open(os.path.join(path2data,name_dat+".dat"),"rb") as file:
        val = pickle.load(file)[init_data]
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
def find_FiT(string):
    """
    This function extracts from the string two values for the Feed in Tarif
    and for the constant value.
    Parameters:
        string:     str
                    String that specifies the feed in Tarif or Offset
                    Has to be in this form "XXf + XXh""
                        XX... value (float)
                        h... constant hourly
                        f... Offset hourly
                    like: "20f + 35.05h"
    Return
        (fit,constant)  tuple
                        fit         float
                        constant    float/str ("nan")
    """
    feed_in_tarif = 0
    fix_price = "nan"
    string = string.strip()
    if  string != "0" and string !="" and string != "0.0":
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
                    fix_price = "nan"
            else:
                print("User Input for modyfing profiles is wrong")
                print("""String that specifies the feed in Tarif or Offset\nHas to be in this form "XXf + XXh"":\n\tXX... value (float)\n\th... constant hourly\n\tf... Offset hourly\n\tlike: "20f + 35.05h""")
                sys.exit()

    return feed_in_tarif,fix_price

def write_fit(string,profil):
    """
    This function return a dict that uses the string input to
    modulate te profile

    Parameters:
        string:     str
                    String that specifies the feed in Tarif or Offset

        profile:    dict
                    profile from .dat Database
    Return:
        dictionary  dict
                    Returns the dict with spezified Feed in Tarif and or
                    Fix Price for the given profile
    """
    feed_in_tarif,fix_price = find_FiT(string)
    if fix_price == "nan":
        return dict(zip(range(1,8760+1),(np.array(list(profil.values()))+feed_in_tarif).tolist()))
    else:
        return dict(zip(range(1,8760+1),[feed_in_tarif+fix_price]*8760))
#%%
def extract(string):
    """
    string has to be in the form : "ID#xx , XXf +XXh"
    where <ID> is a string that corrospond with the data in the dat file,
    <xx> is an int, <XX> is a float
    example: "Wien#2016, 20f + -10.1h"
    """
    if type(string) != str:
        return "no external data specified"

    strings = string.split(",")


    if len(strings) == 2:
        data = strings[0]
        fit = strings[1].strip()

        datas = data.split("#")
        if len(datas) !=2:
            return "invalid format for external data"
        iD = datas[0].strip()
        xx = datas[1].strip()
        try:
            xx=int(xx)
        except:
            return "invalid format for external data, please use an integer"
        return (iD,xx),fit


    elif len(strings) ==1:

        fit_or_data = string.split("#")

        if len(fit_or_data) == 2:
            iD = fit_or_data[0].strip()
            xx = fit_or_data[1].strip()
            try:
                xx=int(xx)
            except:
                return "invalid format for external data, please use an integer"
            return (iD,xx),"0"

        return (0,0),string.strip()
    else:
        return "to many arguments for external data specified"
#%%
def load_external_default_values(path,scenario=0):
    default = mangle_dupe(pd.read_excel(path,"Default - External Data").fillna(0))

    try:
        default = default.iloc[[scenario],:]
    except:
        default = askToGo(default,name="Default - External Data",y=[0])

    default_vals = {}
    for column in default.columns:
        x = extract(default[column].values[0])
        if type(x) == str:
            print(x + "@ " + column)
            print("Exiting Calculation")
            sys.exit()
        default_vals[column] = dict(zip(["id","fit"],x))
    return default_vals
#%%
def profile_jt(**kwargs):
    output = {}
    iD,fit = extract(kwargs["fit_string"])
    if iD == (0,0):
        iD = kwargs["default_id"]
        if fit == "0.0" or fit == "0":
            fit = kwargs["default_fit"]
        else:
            f1,h1 = find_FiT(fit)
            f2,h2 = find_FiT(kwargs["default_fit"])
            f = f1 + f2
            h = "nan" if [h1,h2] == ["nan", "nan"] else (h2 if h1 == "nan" else (h1 if h2 == "nan" else h1 + h2))
            if h == "nan":
                fit = str(f)+"f"
            else:
                 fit = str(f)+"f"+"+"+str(h)+"h"
#    print(kwargs["j"],iD,fit)
    dic_profil = write_fit(fit,return_dict(kwargs["profile_string"],iD))
    for t,val in dic_profil.items():
        output[kwargs["j"],t] = val
    return output
#%%
def askToGo(df,name,y="",x=""):
    global answer # need to be global to work, I don't know why
    answer = 0
    def check():
        global answer
        answer = input()
    th = Thread(target=check, daemon=True)
    print("This Scenario is not in the Excelsheet <"+name+"> aviable")
    print("Do you wish to continue with default values ?")
    print("Press <1> to abbort calculation")
    print("continue automatically in 10 sec or press any key")
    th.start()
    th.join(10)
    if answer == "1":
        del th
        print("\n\n\n\nForce Exiting !!...\n\n\n\n")
        sys.exit()
    else:
        del th
        print("continuing...\n\n\n\n\n")
        if type(y)== str and type(x) == str:
            return  df.iloc[:,:]
        elif type(y)== str and type(x) == list:
            return df.iloc[:,x]
        elif type(y)== list and type(x) == str:
            return df.iloc[y,:]
        elif type(y)== list and type(x) == list:

            return df.iloc[y,x]
        else:
            print("Loading failed !\n Wrong Indexing \n Exit calculation")
            sys.exit()
#%%
def mangle_dupe(df):
     df.columns = [c.split(".")[0] for c in df.columns]
     return df
#%%
def load_data(path_parameter2 = path_parameter2, default_scenario=2):
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
    data_input_params = mangle_dupe(pd.read_excel(path_parameter2,"Data").fillna(0))
    data_input_ef = mangle_dupe(pd.read_excel(path_parameter2,"emmision factors").fillna(0))
    data_input_prices = mangle_dupe(pd.read_excel(path_parameter2,"energy carrier prices").fillna(0))
    data_input_hg = pd.read_excel(path_parameter2,"Heat Generators").fillna(0)
    data_input_hs = pd.read_excel(path_parameter2,"Heat Storage").fillna(0)

    try:
        data_input_params = data_input_params.iloc[[default_scenario],:]
    except:
        data_input_params = askToGo(data_input_params,name="Data",y=[0])

    try:
        data_input_ef = data_input_ef.iloc[:,[0,default_scenario+1]]
    except:
        data_input_ef = askToGo(data_input_ef,name="emmision factors", x=[0,1])

    try:
        data_input_prices = data_input_prices.iloc[:,[0,default_scenario+1]]
    except:
        data_input_prices = askToGo(data_input_prices,name="energy carrier prices",x=[0,1])



    # Generate Mapping tables to distinguish the input data
    input_list_mapper = return_mapper()
    input_price_list_mapper = return_mapper("prices and emmision factors")
    parameter_list_mapper = return_mapper("financal and other parameteres")
    hs_mapper = return_mapper("Heat Storage")

    # Overwrite default values with user input data
    # skip columns that are not in the inital excel
    x=[x for x in data_input_hg.columns.tolist() if x in list(input_list_mapper)]
    overwrite(data,data_input_hg[x],"name",input_list_mapper)
    overwrite(data,data_input_ef,"energy carrier",input_price_list_mapper)
    overwrite(data,data_input_prices,"energy carrier",input_price_list_mapper)
    overwrite(data,data_input_params,"",parameter_list_mapper)
    overwrite(data,data_input_hs,"name",hs_mapper)

    # Categorize Technologies
    select_tec_options = pd.read_excel(path_parameter,"Techologies")["Techologies"].values.tolist()
    data["categorize"] = {}
    for j in select_tec_options:
        data["categorize"][j] = data_input_hg["name"][data_input_hg["type"] == j].values.tolist()

    # Load externel data like demand, radiation,temperature, sale-/electricity price
    default_vals = load_external_default_values(path_parameter2,default_scenario)

    data["energy_carrier_prices"]["electricity"] = {}
    data["sale_electricity"] = {}
    tec = data_input_hg.name.tolist()
    for j in tec:
        string = str(data_input_hg["Electricity Price"][data_input_hg.name ==j].values[0])
        kwargs_elec = dict(fit_string =     string,
                           default_id =     default_vals["Electricity Price"]["id"],
                           default_fit =    default_vals["Electricity Price"]["fit"] ,
                           profile_string = "price_profiles",
                           j = j)

        data["energy_carrier_prices"]["electricity"] =  {** data["energy_carrier_prices"]["electricity"],**profile_jt(**kwargs_elec)}

        string = str(data_input_hg["Sale Electricity Price"][data_input_hg.name ==j].values[0])
        kwargs_elec = dict(fit_string =     string,
                           default_id =     default_vals["Sale Electricity Price"]["id"],
                           default_fit =    default_vals["Sale Electricity Price"]["fit"] ,
                           profile_string = "price_profiles",
                           j = j)
        data["sale_electricity"]  = {**data["sale_electricity"],**profile_jt(**kwargs_elec)}


    data["temp"] = write_fit(default_vals["Temperature"]["fit"],return_dict("temperature_profiles",default_vals["Temperature"]["id"]))
    data["radiation"]  = write_fit(default_vals["Radiation"]["fit"],return_dict("radiation_profiles",default_vals["Radiation"]["id"]))
    data["demand_th"] = write_fit(default_vals["Demand"]["fit"],return_dict("load_profiles",default_vals["Demand"]["id"]))

    x=np.array(list(data["demand_th"].values()))
    x = x / sum(x) * data["total_demand"]
    data["demand_th"] = dict(zip(range(1,8760+1),x.tolist()))
    del x

    ec = pd.read_excel(path_parameter2,"Energy Carrier").fillna(0)
    ec = ec.set_index(ec.name)
    data["energy_carrier"] = ec.to_dict()["carrier"]

    data["tec"] = tec

    tec_hs = data_input_hs.name.tolist()
    data["tec_hs"] = tec_hs

    data["all_heat_geneartors"] = data["tec"] + data["tec_hs"]

    return data, inv_flag


if __name__ == "__main__":
    print('Loading Data...')
    val,flag = load_data()
    print('Loading done')



