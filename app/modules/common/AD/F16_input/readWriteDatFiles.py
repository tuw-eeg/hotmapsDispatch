# -*- coding: utf-8 -*-
"""
Copyright © 2021, jh

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


module name:  readWriteDatFiles.py
Created on:   2021-03-22
@author:      jh

This script is for reading and writing dat files
"""
# =============================================================================
# needed modules
# =============================================================================
from pathlib import Path
from pprint import pprint
import pandas as pd
import numpy as np
import pickle

# =============================================================================
# global paths and variables
# =============================================================================
BASE_DIR = Path(__file__).parent.resolve()

# =============================================================================
# functions and classes
# =============================================================================
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

def empty_dats(BASE_DIR):
    for fp in BASE_DIR.glob("*profiles.dat"):
        with open(fp,"wb") as f:
            pickle.dump({('default', 2016):np.ones(8760)*1e-3},f)
    for fp in BASE_DIR.glob("*map.dat"):
        with open(fp,"wb") as f:
            pickle.dump(dict(default="Wien"),f)
    return None
# =============================================================================
    
def add_profile(short,name,year,profile,string,new=True):
    """This function adds a numpy array into the dat files

    Args:
        short (str): short hand name of the profile
        name (str): long name of the profile
        year (int): year of the profile
        profile (numpy.array): (8760,) vector   
        string (str): name of the dat file 
                      options available:
                        "inlet_temperature",
                        "load",
                        "price",
                        "radiation",
                        "return_temperature",
                        "river_temperature",
                        "temperature",
                        "wastewater_temperature"
        new (bool, optional): flag to create a new dat file or to add . 
                              Defaults to True (creates a new dat file with the profile).

    Returns:
        (bool): True if it succeed and False if it failed to add the profile
    """

    dat_files = ["inlet_temperature","load","price","radiation", "return_temperature",
                 "river_temperature","temperature","wastewater_temperature"]
    if string not in dat_files:
        print(f"{string} is not a valid dat file, select one of {dat_files}")
        return False
    if len(profile) != 8760:
        print(f"The profile you want to add is not 8760 long but {len(profile)} ")
        return False
    m = {short:name}
    p = {(short,int(year)):profile}
    if new:
        p2,m2 = {('default', 2016):np.ones(8760)*1e-3},dict(default="Wien")
    else:
        p2,m2 = opendat(string)
    m = {**m2,**m}
    # print(m)
    p = {**p2,**p}
    savedat(p,m,string)
    return True


def main(arg,*args,**kwargs):
    print(arg)
    return None

# =============================================================================
# main function
# =============================================================================
if __name__ == "__main__":
    empty_dats(BASE_DIR)  # empty all dat files 
    # add_profile(short="aut",
    #             name="austria",
    #             year=2010,
    #             profile= np.cos(np.linspace(0,4*np.pi,8760)),
    #             string="river_temperatureasf",
    #             new=True)
                


# =============================================================================
