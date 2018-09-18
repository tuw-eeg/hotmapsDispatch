# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""
#%% ===========================================================================
#
# =============================================================================
import os,sys,json,glob
import pandas as pd
from bokeh.plotting import output_file,save
from bokeh.models.widgets import Tabs
from threading import Thread
from plotScenarios import compareScnearioPlot
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
def check_solution(solutions):
    if solutions == "Error1":
        print( 'No Capacities installed !!!')
        return False
    elif solutions == "Error2":
        print("The installed capacities are not enough to cover the load !!!" )
        return False
    elif solutions == "Error3":
        print("Error: Infeasible or Unbounded model !!!")
        return False
    elif solutions == None:
        print("Error: Something get Wrong")
        return False
    else:
        print('calculation done')
        return True
# =============================================================================
#     
# =============================================================================
def save_solution(solutions,path_download,name):
    tabs = plot_solutions(show_plot=False,solution=solutions)
    output = Tabs(tabs=tabs)
    if output == "Error4":
        print("Error @ Ploting  !!!")
    else:
        print("Saving output graphics...")
        filename = name+".html"
        output_file(os.path.join(path_download,filename),
                    title="Dispatch output "+ name)
        save(output)
    print("Saving output data..")
    # -- Download JSON
    filename = name+".json"
    with open(os.path.join(path_download,filename), "w") as f:
        json.dump(solutions, f)
    print("Saving done")

#%% ===========================================================================
#
# =============================================================================
def loadExternalData(path2externalData=path2input, path2database=path2dat,
                     path2output=root_dir):
    global answer
    answer = 0
    def check():
        global answer
        answer = input()
    th = Thread(target=check, daemon=True)
    print("Load individual data to Database ?\n Press <1> for Yes ?\n")
    th.start()
    th.join(10)
    if answer == "1":
        print("Loading individual data to Database...")
        xlsx2dat(path2xlsx = path2externalData, path2dat = path2database)
        print("\nLoading Done")
        print("Updating Database Overview...")
        dat_mapper(output_path=path2output,path2dat=path2database)
        print("\nUpdate Done")
    else:
        print("continuing...")
    del th
#%%
# =============================================================================
# 
# =============================================================================
#%%
def compare(scMapper,subScMapper,solutions,path2output=path2output):
    
# =============================================================================
#     
# =============================================================================
    cost_line_up_names = {"OPEX":"Operational Cost:",
                          "CAPEX":"Anual Investment Cost (of existing power plants and heat storages)",
                          "Fuel costs":"Fuel Costs:",
                          "Revenue Eletricity":"Revenue From Electricity:"}
    cost_data = {sub_sc: { cost: {sc: None for sc in scMapper.name} for cost in cost_line_up_names } for sub_sc in subScMapper.name}
    tgms = {(sc,sub_sc) : None for sub_sc in subScMapper.name for sc in scMapper.name}
    data_lcoe = {sc: {sub_sc :None for sub_sc in subScMapper.name} for sc in scMapper.name}
    heat_generators = {sc:None for sc in scMapper.name}
    max_vals = {sub_sc:[] for sub_sc in subScMapper.name}
    cost_line_up_vals = {}
# =============================================================================
#
# =============================================================================
    for sc in scMapper.name:
        for sub_sc in subScMapper.name:
            sol = solutions[sc][sub_sc]
            if sol:
                heat_generators[sc] = sol["all_heat_geneartors"]
    
                for cost,modelname in cost_line_up_names.items():
                    cost_data[sub_sc][cost][sc] = sol[modelname]
                    max_vals[sub_sc].append(max(list(sol[modelname].values())))
    
                tgms[sc,sub_sc] = sol["Thermal Generation Mix:"]
    
                data_lcoe[sc][sub_sc] = sol["Mean Value Heat Price (with costs of existing power plants and heat storages)"]
                for hg in heat_generators[sc]:
                    cost_line_up_vals[sc,sub_sc,hg] = dict()
                    for key,sol_key in cost_line_up_names.items():
                        cost_line_up_vals[sc,sub_sc,hg][key] = sol[sol_key][hg] 
# =============================================================================
#
# =============================================================================

    max_vals = {i:max(val) for i,val in max_vals.items()}
# =============================================================================
#
# =============================================================================
    t = compareScnearioPlot( data_LCOE= data_lcoe  ,
                 sub_sc_names= subScMapper.name.tolist(),
                 sc_names = scMapper.name.tolist(),
                 cost_line_up_names = list(cost_line_up_names),
                 max_val = max_vals,
                 heatgeneartors = heat_generators,
                 tgms = tgms,
                 data = cost_data,
                 solutions = solutions,
                 cost_line_up_vals = cost_line_up_vals,
                 t= range(0,8760)
                 )

    output_file(os.path.join(path2output,"output_scenarios_compare.html"))
    save(t)    
#%% ===========================================================================
# MAIN-FUNCTION
# =============================================================================
if __name__ == "__main__":

# =============================================================================
#
# =============================================================================
    loadExternalData()
# =============================================================================
#
# =============================================================================
    print('calculation started')
    scMapper = pd.read_excel(path2scMapper)
    subScMapper = pd.read_excel(path2scMapper,"sub-scenarios")
    print("\n Caution No Creation-and-Solver Progress will be shown ! \
          \n please be patient, this will take some time\n\n Calculation \
          started...")
    tec_scenarios =  glob.glob(os.path.join(path2scenario,"*.xlsx"))
    sub_scenario_len= sum([pd.read_excel(_,"Default - External Data").
                             fillna(0).shape[0] for _ in tec_scenarios])
    j=0
# =============================================================================
#     
# =============================================================================
    dict_of_solutions =  {sc:{sub_sc: None for sub_sc in subScMapper.name} for sc in scMapper.name}
    for t_sc in tec_scenarios:
        file_name = os.path.basename(t_sc).split(".")[0].strip()
        scenario_name = str(scMapper.name[scMapper.file==file_name].values[0])
        print('~~~~~~~~~~~~~~~~~')
        print("\nCalculation Scenario: "+ scenario_name+"...")
        print('~~~~~~~~~~~~~~~~~')
        for sub_sc in range(pd.read_excel(t_sc,"Default - External Data").
                            fillna(0).shape[0]):
            j=j+1
            print("+++++++++++++++++")
            print(str(j)+"/"+str(sub_scenario_len))
            print("+++++++++++++++++")
            subScenario_name = str(subScMapper.name[subScMapper.Prefix==sub_sc].values[0])
            print("Sub Szenario: " +subScenario_name)
            data,inv_flag = load_data(t_sc,sub_sc)
            solutions,instance,results = execute(data,
                                                 inv_flag,selection=[[],[]])
            if check_solution(solutions):
                dict_of_solutions[scenario_name][subScenario_name] = solutions
    
                name = scenario_name+"_"+subScenario_name
                path_download = create_folder(os.path.join(scenario_name,subScenario_name))
                save_solution(solutions,path_download,name)
            else:
                dict_of_solutions[scenario_name][subScenario_name] = None
                print("Error @ "+subScenario_name+" # "+scenario_name)

        print('~~~~~~~~~~~~~~~~~')
        print("\n\tCalculation of Scenario: "+ scenario_name+" Done !")
        print('~~~~~~~~~~~~~~~~~')

# =============================================================================
#     
# =============================================================================
    print("\n\n\nCreating Compare Figures...")
    compare(scMapper,subScMapper,dict_of_solutions)

    print("\n\nSee calculation output in: <"+path2output+">")






