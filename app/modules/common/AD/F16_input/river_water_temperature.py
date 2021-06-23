# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author:  root

(Insert here your moduel description)

"""

#%%% needed modules
from pathlib import Path
from pprint import pprint
import pandas as pd
import numpy as np
import altair as alt
import pickle,os
from monthly_data import *
#%%% global paths and variables
BASE_DIR = Path(__file__).parent.resolve()

#%%% functions and classes
def opendat(string,path2dat = BASE_DIR):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"rb") as file:
        profile = pickle.load(file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"rb") as file:
        mapper = pickle.load(file)

    return profile, mapper
# =============================================================================
def savedat(profile, mapper, string, path2dat = BASE_DIR):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"wb") as file:
        pickle.dump(profile,file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"wb") as file:
        pickle.dump(mapper,file)
# =============================================================================
def main(arg1,*args,**kwargs):
    """
    (Describe your function)

    Parameters
    ----------
    arg1 : TYPE
        DESCRIPTION.
    *args : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    print(arg1)
    
    return None
# %%
def upsample_day2hour(string):
    df = pd.read_csv(io.StringIO(string),sep="\t").unstack()
    df = df[df != -999]
    df.index = pd.date_range('2017-01-01', periods=df.shape[0], freq='D')
    df = df.asfreq('H', method='ffill')
    return df

def mean_of_str_list(str_list):
    return pd.DataFrame([upsample_day2hour(str_io)for str_io in str_list]).mean()

def river_water_data_fw_kwk_2020(save,path2dat):
    df_wien = upsample_day2hour(str_wien)
    df_graz = upsample_day2hour(str_graz)
    df_linz = upsample_day2hour(str_linz)
    df_salzburg = upsample_day2hour(str_salzburg)
    df_typ1 = mean_of_str_list([str_typ1a,str_typ1b])
    df_typ2 = mean_of_str_list([str_typ2a,str_typ2b])
    df_typ3 = mean_of_str_list([str_typ3a,str_typ3b])
    df_typ5 = mean_of_str_list([str_typ5a,str_typ5b,str_typ5c])

    data = dict(wien=df_wien,linz=df_linz,salzburg=df_salzburg,graz=df_graz, typ1=df_typ1, typ2=df_typ2,typ3=df_typ3,typ5=df_typ5)

    df = pd.DataFrame(data)
    df2 = df.rolling(24,center=True,min_periods=1).mean()  # gleitender 24 stunden mittel 

    mappp = dict(wien="Cluster 1",linz="Cluster 2",salzburg="Cluster 3",graz="Cluster 4", typ1="Cluster 5", typ2="Cluster 6",typ3="Cluster 7",typ5="Cluster 9")

    river_water_name_map = dict()
    river_water_profile = dict()
    for col,name  in mappp.items():
        river_water_name_map[name] = name
        _y = df2[col].values
        num2pad = 8760-len(_y)
        if num2pad !=0:
            river_water_profile[(name,0)] = np.pad(_y,pad_width =(0,num2pad),mode="mean",stat_length=(0,num2pad))
        else:
            river_water_profile[(name,0)] = _y

    river_water_name_map["Cluster 8"] = "Cluster 8"
    river_water_profile[("Cluster 8",0)] = np.zeros(8760)+.1
    river_water_name_map["Cluster 10"] = "Cluster 10"
    river_water_profile[("Cluster 10",0)] = np.zeros(8760)+.1

    river_water_name_map["default"] = "Wien"
    river_water_profile[("default",2016)] = np.zeros(8760)

    if save:
        savedat(river_water_profile, river_water_name_map, "river_temperature",path2dat=path2dat)
    return river_water_profile,river_water_name_map
# %%
#%%% main function

if __name__ == "__main__":
    pprint("Main entered")
    DAT_PATH = BASE_DIR
    river_water_profile,river_water_name_map = river_water_data_fw_kwk_2020(save=True,path2dat=DAT_PATH)
    df_river = pd.DataFrame(river_water_profile)
        
    print("Main End")
    
    