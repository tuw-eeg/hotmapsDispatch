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
import matplotlib.pyplot as plt
from pandas.core.algorithms import mode
import seaborn as sns; sns.set()
import hotmapsloadprofiles as hlp
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

def load_data_fw_kwk_2020(save,path2dat,path):   
    df = pd.read_excel(path)

    kwargs_ued_2017 = dict(tot_res_sh=199.43e3,tot_res_hw=18.93e3,tot_ser_sh=0,tot_ser_hw=0,tot=1000e3,output_path=path2dat)

    # CLuster 1
    kwargs = dict(name="Cluster 1 (WEM)",year=2030,nuts_code="AT13",savings=0.2,abs_profile=df['wien 2017'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=True,**kwargs)

    kwargs = dict(name="Cluster 1 (WEM)",year=2050,nuts_code="AT13",savings=0.4,abs_profile=df['wien 2017'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 1 (WAM)",year=2030,nuts_code="AT13",savings=0.24,abs_profile=df['wien 2017'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 1 (WAM)",year=2050,nuts_code="AT13",savings=0.6,abs_profile=df['wien 2017'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    # Cluster 2
    kwargs = dict(name="Cluster 2 (WEM)",year=2030,nuts_code="AT31",savings=0.2,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 2 (WEM)",year=2050,nuts_code="AT31",savings=0.4,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 2 (WAM)",year=2030,nuts_code="AT31",savings=0.24,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 2 (WAM)",year=2050,nuts_code="AT31",savings=0.6,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    # Cluster 3
    kwargs = dict(name="Cluster 3 (WEM)",year=2030,nuts_code="AT32",savings=0.2,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 3 (WEM)",year=2050,nuts_code="AT32",savings=0.4,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 3 (WAM)",year=2030,nuts_code="AT32",savings=0.24,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 3 (WAM)",year=2050,nuts_code="AT32",savings=0.6,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    # Cluster 4
    kwargs = dict(name="Cluster 4 (WEM)",year=2030,nuts_code="AT22",savings=0.2,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 4 (WEM)",year=2050,nuts_code="AT22",savings=0.4,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 4 (WAM)",year=2030,nuts_code="AT22",savings=0.24,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    kwargs = dict(name="Cluster 4 (WAM)",year=2050,nuts_code="AT22",savings=0.6,abs_profile=df['linz 2016'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    # Cluster 5
    kwargs = dict(name="Cluster 5",year=2030,nuts_code="AT11,AT22",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 5",year=2050,nuts_code="AT34,AT33",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    # Cluster 6
    kwargs = dict(name="Cluster 6",year=2030,nuts_code="AT34,AT33",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 6",year=2050,nuts_code="AT34,AT33",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    # Cluster 7
    kwargs = dict(name="Cluster 7",year=2030,nuts_code="AT12,AT31",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 7",year=2050,nuts_code="AT12,AT31",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    # Cluster 8
    kwargs = dict(name="Cluster 8",year=2030,nuts_code="AT34,AT12",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 8",year=2050,nuts_code="AT34,AT12",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    # Cluster 9
    kwargs = dict(name="Cluster 9",year=2030,nuts_code="AT33,AT31,AT21",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 9",year=2050,nuts_code="AT33,AT31,AT21",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    # Cluster 10
    kwargs = dict(name="Cluster 10",year=2030,nuts_code="AT12,AT21",savings=0.22,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)
    
    kwargs = dict(name="Cluster 10",year=2050,nuts_code="AT12,AT21",savings=0.5,abs_profile=df['Kirchdorf 2011'].values,**kwargs_ued_2017)
    y,profile,mapper,df2 = hlp.add_profile(path2dat,save=save,new=False,**kwargs)

    
    return profile,mapper

#%%% main function
if __name__ == "__main__":
    pprint("Main entered")
    PROFILE_PATH = BASE_DIR.joinpath("load profiles.xlsx")
    DAT_PATH = BASE_DIR
    load_profile,load_name_map = load_data_fw_kwk_2020(save=True,path2dat=DAT_PATH,path=PROFILE_PATH)     
    df_load = pd.DataFrame(load_profile)
    print("Main End")



