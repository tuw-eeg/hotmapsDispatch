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

Created on Sat Feb 29 22:48:23 2020

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
import json
from save_sol_to_json import json2xlsx,scenarioJson2xlsx
from scenario_chart import scenario_chart,create_chart_definitions,prerpare_data
from plot_bokeh import plot_solutions
import altair as alt
import pickle
# =============================================================================
# GLOBAL PATHS AND VARIABLES
# =============================================================================
BASE_DIR = Path(__file__).parent.resolve()

# =============================================================================
# FUNCTIONS
# =============================================================================

def compare_plot(data_available,inputpath,path2output,):
    key1 = "Data (single values)"
    key2 = "Generator Data (single values)"
    print("loading indicators and creating charts..")              
    if data_available:
        out_dict = {key1:pd.read_excel(inputpath.joinpath(f"{key1}.xlsx")),
                    key2:pd.read_excel(inputpath.joinpath(f"{key2}.xlsx"))}
    else:
        dict_of_solutions,scenario_mapper = get_all_Solutions(path=inputpath)
        out_dict = scenarioJson2xlsx(scenario_mapper,dict_of_solutions,path2output)
        
    print("creating charts..")                     
    sources1,len_sub_sc1 = prerpare_data(out_dict[key1])       
    sources2,len_sub_sc2 = prerpare_data(out_dict[key2])
    
    # sources1 = sources1[sources1["Sub Scenario 3"] != "T8"]
    # sources2 = sources2[sources2["Sub Scenario 3"] != "T8"]
    
    costs = ["Total Coldstart Costs","Total Ramping Costs","Total Operational Costs","Total Fuel Costs","Total CO2 Costs","Total Investment Costs (of new build plants and heat storages)","Total Investment Costs of (of existing power plants and heat storages)"]
    topic2flag1 = zip([ ["Total Costs"],["Total Revenue From Electricity"],["Total Thermal Generation"],["Total Final Energy"],["Total LCOH"],["Total CO2 Emissions"],costs],
                        ['###tot_cost1','###tot_rev1','###tot_ue1','###tot_fe1','###tot_lcoh1','###tot_co21','###tot_cost_mix1'])
    
    costs_hg = ["Coldstart Costs:","Ramping Costs:","Operational Cost:","Fuel Costs:","CO2 Costs:","Anual Investment Cost:","Anual Investment Cost (of existing power plants and heat storages)"]
    topic2flag2 = zip( [["Total Cost:"],["Revenue From Electricity:"],["Thermal Generation Mix:"],["Final Energy Mix"],["Installed Capacities:"],["Total CO2 Emission:"],["Full Load Hours:"],["LCOH:"],costs_hg,["max thermal efficiency"],["Final Energy Mix By Energy Carrier"],['Total CO2 Emission: By Energy Carrier']],
                        ['###tot_cost2',"###tot_rev2",'###tot_ue2','###tot_fe2','###capacities2','###tot_co22','###full_load_hours2','###tot_lcoh2','###tot_cost_mix2','###efficience1','###fembyec1','###co2embec1'])


    topic2flag3 = zip( [["Total Cost:"],["Revenue From Electricity:"],["Thermal Generation Mix:"],["Final Energy Mix"],["Installed Capacities:"],["Total CO2 Emission:"],["Full Load Hours:"],["LCOH:"],["max thermal efficiency"],["Final Energy Mix By Energy Carrier"],['Total CO2 Emission: By Energy Carrier']],
                        ['###tot_cost3',"###tot_rev3",'###tot_ue3','###tot_fe3','###capacities3','###tot_co23','###full_load_hours3','###tot_lcoh3','###efficience2','###fembyec2','###co2embec2'])        

    topic2flag4 = zip([ ["Total Costs"],["Total Revenue From Electricity"],["Total Thermal Generation"],["Total Final Energy"],["Total LCOH"],["Total CO2 Emissions"]],
                        ['###tot_cost4','###tot_rev4','###tot_ue4','###tot_fe4','###tot_lcoh4','###tot_co24'])


    chart_definions1 = create_chart_definitions(topic2flag1,sources1,len_sub_sc1)
    chart_definions3 = create_chart_definitions(topic2flag2,sources2,len_sub_sc2)
    chart_definions4 = create_chart_definitions(topic2flag3,sources2,len_sub_sc2)
    chart_definions2 = create_chart_definitions(topic2flag4,sources1,len_sub_sc1)       
        
    
    print("creating comparison charts...")
    chart_definions = chart_definions1 + chart_definions2 + chart_definions3 + chart_definions4
    output_html = scenario_chart(chart_definions,path2output)
    print("creating comparison charts done")
    return output_html

def get_all_Solutions(rename=False,plot=False,cmap=None,path=r"C:\Users\hasani\Documents\Workplace\Dispatch\app\modules\common\AD\F16_input\static\2019-11-01-00-37-30-062111"):
    data = {}
    mapper = {}
    for filename in Path(path).glob('**/*.json'):
        sz,sub=filename.parent.parent.stem,filename.parent.stem
        data[sz] = data.get(sz,{})
        mapper[sz] = mapper.get(sz,[]) + [sub]
        with open(filename) as data_file:
            output_data = json.load(data_file)
            data[sz][sub] = output_data
            if plot:
                plot_solutions(show_plot=False,path2json=str(filename),cmap=cmap,path2output=filename.parent)
            if rename:
                x= Path(filename.parent).joinpath("output.html")
                if x.parent.joinpath(f"output_{sz}_{sub}_2.html").is_file():
                    x.parent.joinpath(f"output_{sz}_{sub}_2.html").unlink()
                    
                x.rename(x.parent.joinpath(f"output_{sz}_{sub}_2.html"))
    for sc,sub_list in mapper.items():
        mapper[sc] = list(sorted(set(sub_list)))
        
    return data,mapper

# =============================================================================
def main(*args,**kwargs):
    cmap = pickle.load(open(r"C:\Users\hasani\Desktop\cmap3.dat","rb"))
    get_all_Solutions(rename=True,plot=True,cmap=cmap,path=Path(r"C:\Users\hasani\Documents\Workplace\Dispatch\app\modules\common\AD\F16_input\static\2020-03-27-00-10-59-540080"))
    # get_all_Solutions(rename=True,plot=True,cmap=cmap,path=Path(r"C:\Users\hasani\Documents\Workplace\Dispatch\app\modules\common\AD\F16_input\static\invest"))
    return None

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    path = Path(r"C:\Users\hasani\Documents\Workplace\Dispatch\app\modules\common\AD\F16_input\static\2020-11-22-23-35-49-226610")

    # main()
    inputpath = Path(r"C:\Users\hasani\Documents\Workplace\Dispatch\app\modules\common\AD\F16_input\static\2020-03-27-00-10-59-540080")
    inputpath = path
    data_available = True
    hmtl = compare_plot(data_available,inputpath,BASE_DIR)