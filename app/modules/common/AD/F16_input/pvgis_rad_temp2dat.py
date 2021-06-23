# -*- coding: utf-8 -*-
"""
# =============================================================================
# Copyright (c) <year> <copyright holders>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

Created on Wed Jan 15 13:21:04 2020

@author: hasani

Description: <insert here the description of your script>

"""

# =============================================================================
# IMPORT NEEDED MODULES
# =============================================================================
import numpy as np
import pandas as pd
from pathlib import Path
import pprint as pp
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
# =============================================================================
# GLOBAL PATHS AND VARIABLES
# =============================================================================
file_path = Path(__file__).parent.resolve()

# =============================================================================
# FUNCTIONS
# =============================================================================

# =============================================================================
# functions for reading and writing hotmaps dispatch model dat files
# =============================================================================
def opendat(string,path2dat):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"rb") as file:
        profile = pickle.load(file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"rb") as file:
        mapper = pickle.load(file)

    return profile, mapper

def savedat(profile, mapper, string, path2dat):
    profile_path = path2dat.joinpath(f"{string}_profiles.dat")
    with open(profile_path,"wb") as file:
        pickle.dump(profile,file)

    mapper_path = path2dat.joinpath(f"{string}_name_map.dat")
    with open(mapper_path,"wb") as file:
        pickle.dump(mapper,file)
# =============================================================================
#         
# =============================================================================
def getPVGISprofiles(lat,lon,name,dat_path,output_path,save=False,new=False):
    req = f"https://re.jrc.ec.europa.eu/api/tmy?lat={lat}&lon={lon}"
    print(req)
    df = pd.read_csv(req,sep=",",skiprows=list(range(16))+list(range(8777,8790)))
    y_gi = df["G(h)"].values
    y_tamb = df["T2m"].values

    # df = pd.read_csv(url,skiprows=list(range(16))+list(range(8777,8790)))
    # y_gi= df["G(h)"].values
    # y_tamb= df.T2m.values
    fh = y_gi.sum() / max(y_gi)
    print(f"Full Load Hours Radiation {name}: {round(fh,2)}h")
    
    profile_temp, mapper_temp = opendat("temperature", dat_path) if not new else ({},{})
    profile_rad, mapper_rad = opendat("radiation", dat_path) if not new else ({},{})
    
    mapper_temp[name] = name
    profile_temp[(name,0)] = y_tamb
    
    mapper_rad[name] = name
    profile_rad[(name,0)] = y_gi
    
    mapper_temp["default"] = "Wien"
    profile_temp[("default",2016)] = np.zeros((8760,))
    
    mapper_rad["default"] = "Wien"
    profile_rad[("default",2016)] = np.zeros((8760,))
    
    if save:
        savedat(profile_rad, mapper_rad, "radiation", output_path)  
        savedat(profile_temp, mapper_temp, "temperature", output_path)  

    return y_tamb,[profile_temp,profile_rad],[mapper_temp,mapper_rad],y_gi

def mittel(list_of_gps,name,dat_path,output_path,save=False,new=True):
    tamb = np.zeros(8760)
    gi = np.zeros(8760)
    for (lat,lon) in list_of_gps:
        y_tamb,_,__,y_gi = getPVGISprofiles(lat,lon,name,dat_path,dat_path,save=False,new=False)
        tamb += y_tamb
        gi += y_gi
    tamb /= len(list_of_gps)
    gi /= len(list_of_gps)

    profile_temp, mapper_temp = opendat("temperature", dat_path) if not new else ({},{})
    profile_rad, mapper_rad = opendat("radiation", dat_path) if not new else ({},{})
    
    mapper_temp[name] = name
    profile_temp[(name,0)] = tamb
    
    mapper_rad[name] = name
    profile_rad[(name,0)] = gi
    
    mapper_temp["default"] = "Wien"
    profile_temp[("default",2016)] = np.zeros((8760,))
    
    mapper_rad["default"] = "Wien"
    profile_rad[("default",2016)] = np.zeros((8760,))
    
    if save:
        savedat(profile_rad, mapper_rad, "radiation", output_path)  
        savedat(profile_temp, mapper_temp, "temperature", output_path)  

    return tamb,[profile_temp,profile_rad],[mapper_temp,mapper_rad],gi       

def main(*args,**kwargs):
    return None
    
def data_for_fw_kwk2020(dat_path,outputpath):
    name="Cluster 1"    # Wien
    lon,lat = 16.37784329004169, 48.20844288082456
    _ = getPVGISprofiles(lat,lon,name,dat_path,outputpath,save=True,new=True)
    name="Cluster 2"    # Linz   
    lat,lon = 48.303056,14.290556
    _ = getPVGISprofiles(lat,lon,name,dat_path,outputpath,save=True,new=False)
    name= "Cluster 3" # Salzburg
    lat,lon= 47.8028623,13.0214107
    _ = getPVGISprofiles(lat,lon,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 4" # Graz
    lat,lon = 47.0736852,15.3717504
    _ = getPVGISprofiles(lat,lon,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 5" # Pamhagen,Kapfenberg
    list_of_gps = [(47.7213724,16.8779107),(47.4551677,15.2420957)]  #typ1
    _ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 6" # Bludenz,Lienz
    list_of_gps = [(47.1512831,9.8283807),(46.8297781,12.7339305)] # typ2
    _ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 7" # StPölten, Laakirchen
    list_of_gps = [(48.1938732,15.5769756),(47.9760971,13.8051357)] #typ3
    _ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 8" # Dornbirn, Baden
    list_of_gps = [(47.3670099,9.7004805),(47.9943122,16.2023156)] # typ4
    _ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 9" # Innsbruck,Wels,Villach
    list_of_gps = [(47.2855502,11.3087505),(48.1683569,13.9918257),(46.6136015,13.7663806)] # typ5
    _ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    name = "Cluster 10" # Wiener Neustadt , Klagenfurt
    list_of_gps = [(47.807904,16.1458355),(46.6414215,14.2427155)] # typ6
    _,profiles,mappers,__ = mittel(list_of_gps,name,dat_path,outputpath,save=True,new=False)
    
    return profiles,mappers
# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    main()
    dat_path = file_path
    name = "San Sebastian"
    lat,lon = 43.309226, -1.981061
    name="Frankfurt"
    lat,lon = 50.110924, 8.682127
    # y_tamb,profiles,mappers,y_gi = getPVGISprofiles(lat,lon,name,dat_path,outputpath,save=True,new=False)
    # profiles,mappers = data_for_fw_kwk2020(dat_path,dat_path)
   

    # from random import uniform
    # for _ in range(100):
    #     lot, lat = uniform(40,50), uniform(-5, 70)        
    

