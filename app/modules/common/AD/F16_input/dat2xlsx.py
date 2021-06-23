# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 15:43:09 2018

@author: root
"""
# =============================================================================
# 
# =============================================================================
import pandas as pd
import os,pickle
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
def dat2DataFrames(p,m):
    suM = []
    maX = []
    i = [x[0]+"-"+str(x[1]) for x in list(p)]
    for key,val in p.items():
        suM.append(round(sum(val),2))
        maX.append(round(max(val),2))    
    df2 = pd.DataFrame(dict(zip(["ID","Summe","Max"],[i,suM,maX])))
    df = pd.DataFrame(dict(zip(["ID","Name"],[list(m),list(m.values())])))
    return df,df2
# =============================================================================
# 
# =============================================================================
def dat_mapper(output_path=root_dir , path2dat = root_dir):
    output_path = os.path.join(output_path,"Database-Overview.xlsx")
    writer = pd.ExcelWriter(output_path)
    external_data = ["radiation","temperature","load","price"]
    for file in external_data:
        print(file)
        p,m = opendat(file,path2dat)
        df1,df2=dat2DataFrames(p,m)
        df1.to_excel(writer,file+"-"+"Mapper")
        df2.to_excel(writer,file+"-"+"Aviable Data")
    writer.save()
#%%    
def dat2xls(countries,years,rootdir=root_dir):
    external_data = ["radiation","temperature","load","price"]
    flag = False
    for file in external_data:
        print(file)
        try:
            path2xls = os.path.join(root_dir, file+".xlsx")
            writer = pd.ExcelWriter(path2xls)
            profile, mapper = opendat(file)
            for cty in countries:
                for year in years:
                    try:
                        df = pd.DataFrame(data=profile[cty,year],columns=[file])
                        df.to_excel(writer,str(cty)+"."+str(mapper[cty])+"-"+str(year))
                        flag = True
                    except:
                        continue
            if flag:
                writer.save()
                flag = False
        except:
            continue
# =============================================================================
# 
# =============================================================================
if __name__ == "__main__":
    countries = ["LZ"]
#    years = range(2007,2017)  
#    dat_mapper()
#    dat2xls(countries,years)
# =============================================================================
# 
# =============================================================================

