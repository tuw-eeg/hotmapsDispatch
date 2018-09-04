# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% ===========================================================================
#
# =============================================================================
import os,sys,json,datetime,glob,xlrd
import pandas as pd
from bokeh.plotting import output_file,save
from bokeh.models.widgets import Tabs
#%% ===========================================================================
#
# =============================================================================
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__)))))
if path not in sys.path:
    sys.path.append(path)
from AD.F16_input.main import load_data
from AD.F16_input.xlsx2dat import xlsx2dat
from AD.F16_input.dat2xlsx import dat_mapper
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch
#%% ===========================================================================
#
# =============================================================================
root_dir = os.path.dirname(os.path.abspath(__file__))
path2scenario = os.path.join(root_dir,"scenarios")
path2input = os.path.join(root_dir,"individual_input_data")
path2dat = os.path.join(path,"AD","F16_input")
path2scMapper = os.path.join(root_dir,"scenarios-mapper.xlsx")
path2output = os.path.join(root_dir,"output")
#%% ===========================================================================
#
# =============================================================================
def execute(data,inv_flag,selection=[[],[]],demand_f=1):
    val = dispatch.main(data,inv_flag,selection,demand_f)
    return val
#%% ===========================================================================
#
# =============================================================================
def create_folder(name,path=path2output):
    """ This function creates a folder in path and returns its path"""
    path_download_dir = os.path.join(path,name)
    if not os.path.exists(path_download_dir):
        os.makedirs(path_download_dir)
    return path_download_dir
#%% ===========================================================================
#
# =============================================================================
def save_solution(solutions,scenario_name,name):
    if solutions == "Error1":
        print( 'No Capacities installed !!!')
    elif solutions == "Error2":
        print("The installed capacities are not enough to cover the load !!!" )
    elif solutions == "Error3":
        print("Error: Infeasible or Unbounded model !!!")
    elif solutions == None:
        print("Error: Something get Wrong")
    else:
        print('calculation done')
        tabs = plot_solutions(show_plot=False,solution=solutions)
        output = Tabs(tabs=tabs)
        if output == "Error4":
            print("Error @ Ploting  !!!")
        else:
            print("Download output_graphics started...")
            filename = name+".html"
            path_download = os.path.join(create_folder(scenario_name),filename)
            output_file(path_download,title="Dispatch output")
            save(output)
            print("Graphics Download done")
            print("Download output data started...")
            # -- Download JSON
            filename = name+".json"
            path_download = os.path.join(create_folder(scenario_name),filename)
            with open(path_download, "w") as f:
                json.dump(solutions, f)
#%% ===========================================================================
# MAIN-FUNCTION
# =============================================================================
if __name__ == "__main__":
    print('calculation started')
    y = input("Load individual data to Database ?\n Press <1> for Yess ?\n")
    if y == "1":
        print("Loading individual data to Database...")
        xlsx2dat(path2xlsx = path2input, path2dat = path2dat)
        print("\nLoading Done")
        print("Updating Database Overview...")
        dat_mapper(output_path=root_dir,path2dat=path2dat)
        print("\nUpdate Done")
# =============================================================================
#
# =============================================================================
    scMapper = pd.read_excel(path2scMapper)
    print("\n Caution No Creation-and-Solver Progress will be shown ! \
          \n please be patient, this will take some time\n\n Calculation started...")
    tec_scenarios =  glob.glob(os.path.join(path2scenario,"*.xlsx"))
    price_scenario_len= sum([pd.read_excel(_,"Default - External Data").
                             fillna(0).shape[0] for _ in tec_scenarios])
    j=0
    for t_sc in tec_scenarios:
        file_name = os.path.basename(t_sc).split(".")[0].strip()
        scenario_name = scMapper.name[scMapper.file==file_name].values[0]
        print("\nCalculation Scenario: "+ scenario_name+"...")
        for p_sc in range(pd.read_excel(t_sc,"Default - External Data").
                          fillna(0).shape[0]):
            j=j+1
            print(str(j)+"/"+str(price_scenario_len))
            data,inv_flag = load_data(t_sc,p_sc)
            solutions,instance,results = execute(data,inv_flag,selection=[[],[]])
            name = scenario_name+"_"+str(p_sc)
            save_solution(solutions,scenario_name,name)

