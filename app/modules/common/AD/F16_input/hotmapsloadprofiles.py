# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 16:59:37 2019

@author: hasani
"""

# =============================================================================
#%%import modules
# =============================================================================
import pandas as pd, numpy as np
import os,sys,glob,pickle
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import requests
import io
sns.set()
# =============================================================================
#%% Paths
# =============================================================================
root_dir = os.path.dirname(os.path.abspath(__file__))
# =============================================================================
#%% Global Variables
# =============================================================================
#%% Global Variables
url_res_hw = "https://gitlab.com/hotmaps/load_profile/load_profile_residential_shw_yearlong_2010/raw/master/data/hotmaps_task_2.7_load_profile_residential_shw_yearlong_2010.csv"
url_res_sh = "https://gitlab.com/hotmaps/load_profile/load_profile_residential_heating_yearlong_2010/raw/master/data/hotmaps_task_2.7_load_profile_residential_heating_yearlong_2010.csv"

url_ter_sh = "https://gitlab.com/hotmaps/load_profile/load_profile_tertiary_heating_yearlong_2010/raw/master/data/hotmaps_task_2.7_load_profile_tertiary_heating_yearlong_2010.csv"
url_ter_hw = "https://gitlab.com/hotmaps/load_profile/load_profile_tertiary_shw_yearlong_2010/raw/master/data/hotmaps_task_2.7_load_profile_tertiary_shw_yearlong_2010.csv"

# htmp = os.path.join(root_dir,"hotmpas load profiles")


# x={   
#     "sh_res": os.path.join(htmp,'data_hotmaps_task_2.7_load_profile_residential_heating_yearlong_2010.csv'),
                                
#     "hw_res": os.path.join(htmp,'data_hotmaps_task_2.7_load_profile_residential_shw_yearlong_2010.csv'),
                            
#     "sh_ser": os.path.join(htmp,'data_hotmaps_task_2.7_load_profile_tertiary_heating_yearlong_2010.csv'),
                             
#     "hw_ser": os.path.join(htmp,'data_hotmaps_task_2.7_load_profile_tertiary_shw_yearlong_2010.csv')
                         
#     }
x={   
    "sh_res": io.StringIO(requests.get(url_res_sh).text),
                                
    "hw_res": io.StringIO(requests.get(url_res_hw).text),
                            
    "sh_ser": io.StringIO(requests.get(url_ter_sh).text),
                             
    "hw_ser": io.StringIO(requests.get(url_ter_hw).text)
                         
    }
#%%
def opendat(string,path2dat = root_dir):
    profile_path = os.path.join(path2dat,string+"_profiles.dat")
    with open(profile_path,"rb") as file:
        profile = pickle.load(file)

    mapper_path = os.path.join(path2dat,string+"_name_map.dat")
    with open(mapper_path,"rb") as file:
        mapper = pickle.load(file)

    return profile, mapper
# =============================================================================
#
# =============================================================================
def savedat(profile, mapper, string, path2dat = root_dir):
    profile_path = os.path.join(path2dat,string+"_profiles.dat")
    with open(profile_path,"wb") as file:
        pickle.dump(profile,file)

    mapper_path = os.path.join(path2dat,string+"_name_map.dat")
    with open(mapper_path,"wb") as file:
        pickle.dump(mapper,file)
        
def get_gitlab_profile(nuts_code,path,total):    
    y = pd.read_csv(path).groupby(["NUTS2_code"]).get_group((nuts_code)).loc[:,"load"].values
    y = y / sum(y) * total
    return y

def get_profile(nuts_codes,tot_res_hw,tot_res_sh,tot_ser_hw,tot_ser_sh,mapper=x,tot_hw=1,tot_sh=1,tot=1):
    
    hw = np.zeros(8760)
    sh = np.zeros(8760)
    total = np.zeros(8760)
    for nuts_code in nuts_codes.split(","):
        nuts_code = nuts_code.strip()
        p_res_sh= get_gitlab_profile(nuts_code=nuts_code,path=mapper["sh_res"],total=tot_res_sh)
        p_res_hw= get_gitlab_profile(nuts_code=nuts_code,path=mapper["hw_res"],total=tot_res_hw)
        p_serv_sh= get_gitlab_profile(nuts_code=nuts_code,path=mapper["sh_ser"],total=tot_ser_sh)
        p_serv_hw= get_gitlab_profile(nuts_code=nuts_code,path=mapper["hw_ser"],total=tot_ser_hw)
        
        hw += (p_res_hw + p_serv_hw)*tot_hw
        sh += (p_serv_sh + p_res_sh)*tot_sh
        
        total += (hw +sh)*tot
    n = len(nuts_codes.split(","))
    hw /= n
    sh /= n
    total /=n
    return pd.DataFrame({"total":total,"abs_value_hw":hw,"abs_value_sh":sh,"value_sh":sh/total,"value_hw":hw/total})
# =============================================================================
#%% Functions
def rewrite(df,hotwater,spaceheating):
    """ Set the anual total hotwater & spaceheating demand in MWh and keep profile curve 
    """
    hw = df.loc[:,"abs_value_hw"].values / df.loc[:,"abs_value_hw"].values.sum() * hotwater
    sh = df.loc[:,"abs_value_sh"].values / df.loc[:,"abs_value_sh"].values.sum() * spaceheating
    tot = hw +sh
    hw_rel = hw/tot
    sh_rel = sh/tot
     
    df.loc[:,"value_sh"] = sh_rel
    df.loc[:,"value_hw"] = hw_rel
    df.loc[:,"abs_value_sh"] = sh
    df.loc[:,"abs_value_hw"] = hw
    df.loc[:,"total_value"] = tot
    
    return None


def set_savings(sav,df,abs_profile=None):
    if type(abs_profile) != type(None):
        factor = (df.loc[:,"value_sh"]*(1-sav) + df.loc[:,"value_hw"]).values
        y = abs_profile * factor
    else:
        y = (df.loc[:,"abs_value_sh"]*(1-sav) + df.loc[:,"abs_value_hw"]).values
    
    return y

def duration_curve_with_savings(df,gesamt=1,abs_profile=None,title="Load Duration Curve"):
    data= {}
    data2= {}

    fig,(ax,ax2) = plt.subplots(2,1)
    for sav in range(0,80,10):
        sav /= 100
        y=set_savings(sav,df,abs_profile)
        y2 = y/sum(y) * gesamt 
        y2=np.sort(y2)[::-1]
        y.sort()
        y = y[::-1]
        
        data[f"{str(int(sav*100)).zfill(3)}%"]=y
        data2[f"{str(int(sav*100)).zfill(3)}%"]=y2
        
        ax.plot(range(8760),y,label=f"savings={round(sav,2)*100} & Total Demand={round(sum(y)*1e-3,2)}GWh & Peak: {round(max(y),2)}MW")
        ax2.plot(range(8760),y2,label=f"savings={round(sav,2)*100} & Total Demand={round(sum(y2)) if gesamt==1 else round(sum(y2)*1e-3,2)} {'GWh' if gesamt!=1 else ''} & Peak: {round(max(y2)*1e6,2) if gesamt == 1 else round(max(y2),2)}{'MW' if gesamt!=1 else ''}")
    
    ax.legend()
    ax2.legend()    
    ax.set_title(title)    
    ax.set_xlabel("time [h]")
    ax.set_ylabel('demand [MW]')
    
    ax2.set_title(f'normed {title}')    
    ax2.set_xlabel("time [h]")
    ax2.set_ylabel('[1/h]')
    
    fig.show()
    return fig,data,data2
# =============================================================================
def add_profile(dat_path,name="San Sebastian",year=2070,nuts_code="ES21",tot_res_sh=260e3,tot_res_hw=105e3,tot_ser_sh=202e3,tot_ser_hw=18e3,savings=0.3,tot=1,new=False,output_path=root_dir,abs_profile=None,save=False,tot_hw=1,tot_sh=1,tot_ref=1):
    profile, mapper = opendat("load", dat_path) if not new else ( {("default",2016) : np.zeros(8760) + .1 }, {"default" : "Wien"})
    source = get_profile(nuts_codes=nuts_code,tot_res_sh=tot_res_sh,tot_res_hw=tot_res_hw,tot_ser_sh=tot_ser_sh,tot_ser_hw=tot_ser_hw,tot_hw=tot_hw,tot_sh=tot_sh,tot=tot_ref)
    y = set_savings(savings,source,abs_profile)
    y = y/sum(y)*tot
    mapper[name] = name
    profile[(name,int(year))] = y

    if save:
        savedat(profile, mapper, "load", output_path)
    return y,profile,mapper,source
#%% Main 
# =============================================================================
def main():
    print("Start Main")
    return None
# =============================================================================
#%% Python Main
# =============================================================================
if __name__ == "__main__":
    print("enter main")
    dat_path = root_dir
    
    kwargs = dict(name="San Sebastian",year=2070,nuts_code="ES21",
                  tot_res_sh=260e3,tot_res_hw=105e3,
                  tot_ser_sh=202e3,tot_ser_hw=18e3,savings=0.3,tot=200e3)
    
    y,profile,mapper,df = add_profile(dat_path,save=True,new=True,**kwargs)
    # plt.plot(y)
 
