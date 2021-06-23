# -*- coding: utf-8 -*-
"""
# =============================================================================
# Copyright (c) 2020 jh
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

Created on Fri Jan 17 09:49:52 2020

@author: jh

Description: this script extract and add the SetNaV electricity into dat files

"""

# =============================================================================
# IMPORT NEEDED MODULES
# =============================================================================
import numpy as np
import pandas as pd
from pathlib import Path
import pprint as pp
import pickle,glob
import io,requests
# =============================================================================
# GLOBAL PATHS AND VARIABLES
# =============================================================================
BASE_DIR = Path(__file__).parent.resolve()
elec_keys = ["Diversification","National Champions","Directed Vision","Localisation"]
elec_urls = ["https://gitlab.com/hotmaps/load_electricity/electricity_prices_hourly/-/raw/SetNaV_electricity_prices_hourly/data/34919_Diversification.csv",
            "https://gitlab.com/hotmaps/load_electricity/electricity_prices_hourly/-/raw/SetNaV_electricity_prices_hourly/data/35036_National%20Champions.csv",
            "https://gitlab.com/hotmaps/load_electricity/electricity_prices_hourly/-/raw/SetNaV_electricity_prices_hourly/data/34920_Directed%20Vision.csv",
            "https://gitlab.com/hotmaps/load_electricity/electricity_prices_hourly/-/raw/SetNaV_electricity_prices_hourly/data/34944_Localisation.csv"]
elec_dict = dict(zip(elec_keys,elec_urls))
#%%
#%%
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
def setNav_whole_sale_electricity_prices(nuts0="DE",year=2050,elec_dict=elec_dict):
    """ This function load the SetNav electricity whole sale prices and cuts off 
    the outliers by replacing it with the maximum bandwith where 99.35% of all 
    values are
    
    Params:
        nuts0   string
        year    int
        path    string
    
    Returns:
        price_profile   dict
        price_name_map  dict
    
    """    
    price_profile = dict()
    price_name_map = dict()


    for name,url in elec_dict.items():
        df = pd.read_csv(io.StringIO(requests.get(url).text))
        name = f"{nuts0}-{name}"
        price_name_map[name] =name
        y = df[(df.country == f"{nuts0}_0") & (df.simyear ==year)].value.values
        max_val = np.percentile(y,99.35)
        y[y>max_val] = max_val
        price_profile[(name,int(year))] = y

    return price_profile,price_name_map


def add_electricity_prices(nuts0,dat_path,output_path=BASE_DIR,new=False,year=2050):
    
    profile_price, mapper_price = opendat("price", dat_path) if not new else ({},{})
    price,price_name_map = setNav_whole_sale_electricity_prices(nuts0=nuts0,year=year)    
    profile_price = {**profile_price,**price}
    mapper_price = {**mapper_price,**price_name_map}
    savedat(profile_price, mapper_price, "price", output_path)
    return price,profile_price, mapper_price
    
def main(*args,**kwargs):
    return None

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    main()
    dat_path = BASE_DIR
    price,profile_price, mapper_price = add_electricity_prices("AT",dat_path,output_path=dat_path,new=False,year=2030)
    df = pd.DataFrame(profile_price)
