# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 16:43:40 2018

@author: root
"""
# =============================================================================
#
# =============================================================================
import pandas as pd
import os,pickle,xlrd
import numpy as np
# =============================================================================
#
# =============================================================================
root_dir = os.path.dirname(os.path.abspath(__file__))
# =============================================================================
#
# =============================================================================
def printSameLine(string):
    print(end="\r")
    print(string,end="\r")
    print(flush=True,end="\r")
# =============================================================================
#
# =============================================================================
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
# =============================================================================
#
# =============================================================================
def xlsx2dat(external_data = ["radiation","temperature","load","price"] ,
             path2xlsx = root_dir,
             path2dat = root_dir):
    for file in external_data:
        print("\n Loading "+file+"...")
        try:
            path2xls = os.path.join(path2xlsx, file+".xlsx")
            tabs = [sheet.name for sheet in xlrd.open_workbook(path2xls, on_demand=True).sheets()]
            profile, mapper = opendat(file,path2dat)
            for sheet in tabs:
                printSameLine(sheet)
                try:
                    cty,year = sheet.strip().split(".")
                    cty_id,cty_name = cty.split("-")
                    y=np.round(pd.read_excel(path2xls,sheet).fillna(method='ffill', limit=50).values[:8760,0],2)
                    profile[cty_id,int(year)] = y
                    mapper[cty_id]=cty_name
                except Exception as e:
#                    print(e,type(e))
                    if str(type(e)) == "<class 'ValueError'>":
                        print("\n Invalid Sheetname:"+sheet+ " in"+str(path2xls))
                        print(" Please use a number instead of "+ year)
                    continue
            savedat(profile, mapper, file, path2dat)
        except Exception as e:
            print(e)
            continue
# =============================================================================
#
# =============================================================================
if __name__ == "__main__":
    external_data = ["radiation","temperature","load","price"]
#    xlsx2dat()
# =============================================================================
#
# =============================================================================
