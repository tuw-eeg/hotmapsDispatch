# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import json
import numpy as np
import pandas as pd
import copy
#%%
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
#%%
path2solution = os.path.join(path, "AD", "F16_input", "Solution")

def save_sol_to_json (instance,results,inv_flag,path2solution = path2solution):
#%%
    unit_dict = {    
            'Anual Investment Cost': 'EUR', 
            'Anual Investment Cost (of existing heat storages)': 'EUR', 
            'Anual Investment Cost (of existing power plants and heat storages)': 'EUR', 
            'Anual Investment Cost (of existing power plants)': 'EUR', 
            'Anual Investment Cost Heat Storage': 'EUR', 
            'Anual Investment Cost:': 'EUR', 
            'Anual Total Costs': 'EUR', 
            'Anual Total Costs (with costs of existing power plants and heat storages)': 'EUR', 
            'Anual Total Costs (with costs of existing power plants)': 'EUR', 
            'CO2 Emission Electricity': 'kg CO2', 
            'CO2 Emission Heat': 'kg CO2', 
            'CO2 Emission Heat Storages': 'kg CO2', 
            'Coldstart Costs': 'EUR', 
            'Coldstart Count': '-', 
            'Electrical Consumption of Heatpumps and Power to Heat devices': 'MWh', 
            'Electrical Peak Load Costs': 'EUR', 
            'Electricity Price': 'EUR/MWh', 
            'Electricity Production by CHP': 'MWh', 
            'Fuel Costs': 'EUR', 
            'Fuel Costs Heat Storages': 'EUR', 
            'Fuel Costs:': 'EUR', 
            'Full Load Hours': 'EUR', 
            'Full Load Hours Heat Storage': 'EUR', 
            'Full Load Hours:': 'h', 
            'HS-Capacities': 'MWh', 
            'Heat Demand': 'MW', 
            'Heat Price': 'EUR/MWh', 
            'Heat Storage Technologies': '-', 
            'Installed Capacities': 'MW', 
            'Installed Capacities Heat Storages': 'MW', 
            'Installed Capacities:': 'MW', 
            'LCOH': 'EUR/MWh', 
            'LCOH Heat Storage': 'EUR/MWh', 
            'LCOH:': 'EUR/MWh', 
            'Loading Heat Storage': 'MW', 
            'MC': 'EUR/MWh', 
            'Marginal Costs': 'EUR/MWh', 
            'Marginal Costs:': 'EUR/MWh', 
            'Maximum Electrical Load of Heatpumps and Power to Heat devices': 'MW', 
            'Mean Value Heat Price': 'EUR/MWh', 
            'Mean Value Heat Price (with costs of existing power plants and heat storages)': 'EUR/MWh', 
            'Mean Value Heat Price (with costs of existing power plants)': 'EUR/MWh', 
            'Median Value Heat Price': 'EUR/MWh', 
            "Operating Hours Heat Storage":"h",
            'Operating Hours':"h",
            "Operating Hours:":"h",
            'Operational Cost': 'EUR', 
            'Operational Cost of Heat Storages': 'EUR', 
            'Operational Cost:': 'EUR', 
            'Ramping Costs': 'EUR', 
            'Renewable Share': '-', 
            'Revenue From Electricity': 'EUR', 
            'Revenue From Electricity:': 'EUR', 
            'Revenue from Heat Storages': 'EUR', 
            'Seasonal Performance Factor': '-', 
            'Specific Capital Costs of Installed Capacities:': 'EUR/MW', 
            'Specific Capital Costs of installed Capacities': 'EUR/MW', 
            'Specific Capital Costs of installed Heat Storages': 'EUR/MWh', 
            'State of Charge': 'MWh', 
            'Technologies': '-', 
            'Technologies:': '-', 
            'Thermal Generation Mix': 'MWh', 
            'Thermal Generation Mix:': 'MWh', 
            'Thermal Power Energymix': 'MW', 
            'Thermal Power Energymix:': 'MW', 
            'Thermal Production by CHP': 'MWh', 
            'Total CO2 Emission': 'kg CO2', 
            'Total CO2 Emission:': 'kg CO2', 
            'Total CO2 Emissions': 'kg CO2', 
            'Turn Over Rate': '-', 
            'Turn Over Rate Heat Storages': '-', 
            'Turn Over Rate:': '-', 
            'Unloading Heat Storage': 'MW', 
            'Unloading Heat Storage over year': 'MW', 
            "Variable Cost CHP's": 'EUR', 
            'all_heat_geneartors': '-', 
            'efficiency': '-', 
            'model_Coldstarts': '-', 
            "CO2 Costs:":'EUR', 
            "CO2 Costs":'EUR', 
            "CO2 Costs Heat Storages":"EUR", 
            "Total Fuel Costs":"EUR", 
            "Total CO2 Costs":"EUR", 
            "Total Operational Costs":"EUR", 
            "Total Investment Costs":"EUR", 
            "Total Thermal Generation":"MWh", 
            "Total Electricty Consumption":"MWh", 
            "Source Temperature River":"°C", 
            "Source Temperature Waset Water": "°C", 
            "Flow Temperature":"°C", 
            "Return Temperature": "°C", 
            "Ambient Temperature": "°C", 
            "Radiation": "W/m²", 
            } 
#%%
    try:
#        if os.path.isdir(path2solution) ==False:
#            print("Create Solution Dictionary")
#            os.mkdir(path2solution)
        print("Saving Solver Output ....")

        c_inv_stock = {j:instance.x_th_cap_j[j] * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j}
        c_ramp = {j:sum( instance.ramp_jt[j,t]() * instance.c_ramp_j[j] for t in instance.t) for j in instance.j}
        print("Here")
        rev_tot = {j:sum(instance.x_el_jt[j,t]()*instance.sale_electricity_price_jt[j,t] for t in instance.t) for j in instance.j}

        c_tot_inv = instance.cost() + sum ([c_inv_stock[j]  for j in instance.j])


        solution={ "Thermal Power Energymix":{j:[instance.x_th_jt[(j,t)]() for t in instance.t] for j in instance.j},
                  "Installed Capacities": {j:instance.Cap_j[j]() for j in instance.j},
                  "Heat Price": [results.solution(0).constraint["genearation_covers_demand_t["+str(t)+"]"]["Dual"] for t in instance.t],
                  "Electricity Production by CHP" : sum([instance.x_el_jt[(j,t)]() for j in instance.j_chp for t in instance.t]),
                  "Thermal Production by CHP" : sum([instance.x_th_jt[(j,t)]() for j in instance.j_chp for t in instance.t]),
                  "Electrical Consumption of Heatpumps and Power to Heat devices" : \
                                       sum([instance.x_th_jt[(j,t)]() / instance.n_th_jt[j,t] for j in instance.j_hp for t in instance.t])+\
                                       sum([instance.x_th_jt[(j,t)]() / instance.n_th_jt[j,t] for j in instance.j_pth for t in instance.t]),
                  "Maximum Electrical Load of Heatpumps and Power to Heat devices" : \
                                       max([max(np.array([instance.x_th_jt[(j,t)]() / instance.n_th_jt[j,t] for j in instance.j_hp for t in instance.t]),default=0),
                                          max(np.array([instance.x_th_jt[(j,t)]() / instance.n_th_jt[j,t] for j in instance.j_pth for t in instance.t]),default=0)]),
                  "Thermal Generation Mix":{j:sum([instance.x_th_jt[(j,t)]() for t in instance.t]) for j in instance.j}
                  }

        solution["Ramping Costs"] = c_ramp
        solution["Revenue From Electricity"] = rev_tot
        solution["Heat Demand"] = [instance.demand_th_t[t] for t in instance.t]
        try:
            _x = list(instance.j_bp)[0] 
        except:
            _x = list(instance.j)[0]
        solution["Electricity Price"] = [instance.electricity_price_jt[_x,t] for t in instance.t]
        solution["Mean Value Heat Price"] = np.mean(np.array(solution["Heat Price"]))
        solution["Mean Value Heat Price (with costs of existing power plants)"] =  c_tot_inv/sum([instance.demand_th_t[t] for t in instance.t])
        solution["Median Value Heat Price"] = np.median(np.array(solution["Heat Price"]))
        solution["Operational Cost"]= {j:(instance.Cap_j[j]() * instance.OP_fix_j[j] + sum(instance.x_th_jt[j,t]() * instance.OP_var_j[j]for t in instance.t))for j in instance.j}
        solution["Variable Cost CHP's"]= sum([instance.mc_jt[j,t] * instance.x_th_jt[j,t]() - instance.sale_electricity_price_jt[j,t] * instance.x_el_jt[j,t]() for j in instance.j_chp for t in instance.t])
        solution["Fuel Costs"] = {j:sum([(instance.mc_jt[j,t]-instance.em_j[j]*instance.pco2/instance.n_th_jt[j,t]) * instance.x_th_jt[j,t]() for t in instance.t]) for j in instance.j} 
        solution["MC"] = {j:[instance.mc_jt[j,t] for t in instance.t] for j in instance.j} 
        solution["CO2 Costs"]= {j:sum([(instance.em_j[j]*instance.pco2/instance.n_th_jt[j,t]) * instance.x_th_jt[j,t]() for t in instance.t]) for j in instance.j} 
        solution["CO2 Costs Heat Storages"] = {hs:0 for hs in instance.j_hs} 
        solution["CO2 Costs:"] = {**solution["CO2 Costs"], **solution["CO2 Costs Heat Storages"]} 
           #FIXME
        solution["Anual Total Costs"] = instance.cost() #Operational + Fuel + Ramping + el. Peakload-el. Revenues without Investmentcosts of existing Powerplants
        solution["Anual Total Costs (with costs of existing power plants)"] = c_tot_inv

        solution["Anual Investment Cost"] =  {j:0 for j in instance.j}
        solution["Anual Investment Cost Heat Storage"] = {hs:0 for hs in instance.j_hs}
        if inv_flag:
            solution["Anual Investment Cost"] = {j:(instance.Cap_j[j]() - instance.x_th_cap_j[j])  * instance.IK_j[j] * instance.alpha_j[j] for j in instance.j}
            solution["Anual Investment Cost Heat Storage"] = {hs:instance.Cap_hs[hs]()  * instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in instance.j_hs}

        solution["Anual Investment Cost (of existing power plants)"] = c_inv_stock
        solution["Anual Investment Cost (of existing heat storages)"] = {hs:instance.cap_hs[hs] * instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in instance.j_hs}
        solution["Anual Investment Cost (of existing power plants and heat storages)"]={**solution["Anual Investment Cost (of existing power plants)"],
                 **solution["Anual Investment Cost (of existing heat storages)"],
                 }
        solution["Anual Total Costs (with costs of existing power plants and heat storages)"] = \
            solution["Anual Total Costs (with costs of existing power plants)"] + \
            sum(solution["Anual Investment Cost (of existing heat storages)"].values())

        solution["Mean Value Heat Price (with costs of existing power plants and heat storages)"] = solution["Anual Total Costs (with costs of existing power plants and heat storages)"] / sum([instance.demand_th_t[t] for t in instance.t])

        solution["Electrical Peak Load Costs"] = instance.P_el_max()*10000
        solution["Specific Capital Costs of installed Capacities"] = {j:instance.IK_j[j] * instance.alpha_j[j] for j in solution["Installed Capacities"].keys() if solution["Installed Capacities"][j] !=0 }
        solution["Technologies"] = [j for j in instance.j]
        solution["Marginal Costs"] = [np.mean([instance.mc_jt[j,t] for t in instance.t]) - instance.n_el_j[j]/np.mean([instance.n_th_jt[j,t] for t in instance.t]) *np.mean([instance.sale_electricity_price_jt[j,t] for t in instance.t]) if j in instance.j_chp else np.mean([instance.mc_jt[j,t] for t in instance.t]) for j in instance.j]
        for i,val in enumerate(instance.j):
            if val in instance.j_chp:
                solution["Marginal Costs"][i] = solution["Marginal Costs"][i] - instance.n_el_j[val]/np.mean([instance.n_th_jt[val,t] for t in instance.t])*np.mean([instance.sale_electricity_price_jt[val,t] for t in instance.t])
        solution["State of Charge"] = {hs:[instance.store_level_hs_t[hs,t]() for t in instance.t] for hs in instance.j_hs}

        solution["HS-Capacities"] = {hs:instance.Cap_hs[hs]()+instance.cap_hs[hs] if instance.Cap_hs[hs]() != None else instance.cap_hs[hs] for hs in instance.j_hs }
        solution["Loading Heat Storage"] = dict()
        solution["Unloading Heat Storage"] = dict()
        for hs,array in {hs:np.array([instance.x_load_hs_t[hs,t]() for t in instance.t]) for hs in instance.j_hs}.items():
            solution["Loading Heat Storage"][hs] = np.where(array>0,array,0).tolist()
            solution["Unloading Heat Storage"][hs] = abs(np.where(array<0,array,0)).tolist()
            
        # since pyomo 5.7 deprecated .value() attribute 
        try:     
            solution["Heat Storage Technologies"] = list(instance.j_hs.data()) 
        except: 
            solution["Heat Storage Technologies"] = list(instance.j_hs.value)  
        solution["Unloading Heat Storage over year"] =  {hs:sum(solution["Unloading Heat Storage"][hs]) for hs in instance.j_hs}
        solution["Revenue from Heat Storages"]  = {hs:0 for hs in instance.j_hs}
        solution["Operational Cost of Heat Storages"]= {hs:solution["HS-Capacities"][hs] * instance.OP_fix_hs[hs] for hs in instance.j_hs }
        solution["Specific Capital Costs of installed Heat Storages"] = {hs:instance.IK_hs[hs] * instance.alpha_hs[hs] for hs in solution["HS-Capacities"].keys() if solution["HS-Capacities"][hs] !=0 }
        solution["Fuel Costs Heat Storages"] = {hs:0 for hs in instance.j_hs}
        solution["Installed Capacities Heat Storages"] = {hs:instance.unload_cap_hs[hs] if solution["HS-Capacities"][hs]>0 else 0 for hs in instance.j_hs  } 
        solution["Turn Over Rate Heat Storages"] = {hs: solution["Unloading Heat Storage over year"][hs]  / solution["HS-Capacities"][hs] if solution["HS-Capacities"][hs]>0 else "" for hs in instance.j_hs } 
        solution["Turn Over Rate"] = {j:"" for j in instance.j } 
        solution["Turn Over Rate:"] =  {**solution["Turn Over Rate"] ,**solution["Turn Over Rate Heat Storages"]}  
#XXX
        solution["Technologies:"] =  solution["Technologies"] + solution["Heat Storage Technologies"]

        solution["Thermal Power Energymix:"] = {**solution["Thermal Power Energymix"],
                                        **solution["Unloading Heat Storage"]}

        solution["Installed Capacities:"] ={**solution["Installed Capacities"],
                                        **solution["Installed Capacities Heat Storages"]}

        solution["Thermal Generation Mix:"] = {**solution["Thermal Generation Mix"],
                                        **solution["Unloading Heat Storage over year"]}

        solution["Marginal Costs:"] = solution["Marginal Costs"]+[1e100]*len(solution["Heat Storage Technologies"])

        solution["Anual Investment Cost:"] =  {**solution["Anual Investment Cost"],
        **solution["Anual Investment Cost Heat Storage"]}

        solution["Revenue From Electricity:"] = {**solution["Revenue From Electricity"],
                **solution["Revenue from Heat Storages"]}



        solution["Operational Cost:"] = {**solution["Operational Cost"],
                **solution["Operational Cost of Heat Storages"]}

        solution["Specific Capital Costs of Installed Capacities:"] = {**solution["Specific Capital Costs of installed Capacities"],
                **solution["Specific Capital Costs of installed Heat Storages"]}
        solution["Fuel Costs:"] = {**solution["Fuel Costs"],
                **solution["Fuel Costs Heat Storages"]}
        # since pyomo 5.7 deprecated .value() attribute 
        try:     
            solution["all_heat_geneartors"] = list(instance.all_heat_geneartors.data()) 
        except: 
            solution["all_heat_geneartors"] = list(instance.all_heat_geneartors.value) 
        # CO2 Emissions
        solution["Total CO2 Emission"]= {j:1e3*solution["Thermal Generation Mix"][j]*instance.em_j[j]/np.mean([instance.n_th_jt[j,t] for t in instance.t]) for j in instance.j} 
        solution["CO2 Emission Heat"] = {j: solution["Total CO2 Emission"][j]*np.mean([instance.n_th_jt[j,t] for t in instance.t])/(np.mean([instance.n_th_jt[j,t] for t in instance.t])+instance.n_el_j[j]) for j in instance.j} 
        solution["CO2 Emission Electricity"] = {j:solution["Total CO2 Emission"][j]*instance.n_el_j[j]/(np.mean([instance.n_th_jt[j,t] for t in instance.t])+instance.n_el_j[j]) for j in instance.j} 
        solution["CO2 Emission Heat Storages"] = {hs:0 for hs in instance.j_hs}
        solution["Total CO2 Emission:"]= {**solution["Total CO2 Emission"],**solution["CO2 Emission Heat Storages"]}
        solution["Total CO2 Emissions"] = sum(solution["Total CO2 Emission:"].values())
        # Full Load Hours
        
        solution["Full Load Hours"] = {j:solution["Thermal Generation Mix"][j]/solution["Installed Capacities"][j] if solution["Installed Capacities"][j]!=0 else 0 for j in instance.j} 
        solution["Full Load Hours Heat Storage"] = {hs: solution["Unloading Heat Storage over year"][hs]/solution["Installed Capacities Heat Storages"][hs] if solution["Installed Capacities Heat Storages"][hs]!=0 else 0 for hs in instance.j_hs} 
        solution["Full Load Hours:"] = {**solution["Full Load Hours"],**solution["Full Load Hours Heat Storage"]} 

        solution["Operating Hours"] = { j: int(sum(np.array(solution["Thermal Power Energymix"][j])>0)) for j in instance.j}  
        solution["Operating Hours Heat Storage"] = {hs: int(sum(np.array(solution["Unloading Heat Storage"][hs])>0)) for hs in instance.j_hs}  
        solution["Operating Hours:"] = {**solution["Operating Hours"],**solution["Operating Hours Heat Storage"]} 
         

        solution["LCOH"] =  {j:(solution["Anual Investment Cost"][j]+solution["Anual Investment Cost (of existing power plants)"][j]+solution["Operational Cost"][j]+solution["Fuel Costs"][j]-solution["Revenue From Electricity"][j])/solution["Thermal Generation Mix"][j] if solution["Thermal Generation Mix"][j]>0 else "" for j in instance.j  } 
        solution["LCOH Heat Storage"] =  {hs:(solution["Anual Investment Cost Heat Storage"][hs]+solution["Anual Investment Cost (of existing heat storages)"][hs]+solution["Operational Cost of Heat Storages"][hs]+solution["Fuel Costs Heat Storages"][hs]-solution["Revenue from Heat Storages"][hs])/solution["Unloading Heat Storage over year"][hs] if solution["Unloading Heat Storage over year"][hs]>0 else "" for hs in instance.j_hs  } 
        solution["LCOH:"] = {**solution["LCOH"] ,**solution["LCOH Heat Storage"]} 
        
        solution["efficiency"] = { j: [instance.n_th_jt[j,t] for t in instance.t] for j in instance.j }  
        solution["Renewable Share"] = 100*sum([sum([(instance.x_th_jt[j,t]()+instance.x_el_jt[j,t]()) for t in instance.t])*instance.rf_j[j] for j in instance.j]) / sum([sum([(instance.x_th_jt[j,t]()+instance.x_el_jt[j,t]()) for t in instance.t])for j in instance.j]) 
        
        solution["Total Operational Costs"] = sum(solution["Operational Cost:"].values()) 
        solution["Total Investment Costs"] = sum(solution["Anual Investment Cost (of existing power plants and heat storages)"].values()) 
        solution["Total Thermal Generation"] = sum(solution["Thermal Generation Mix:"].values()) 
        solution["Total Electricty Consumption"] = solution["Electrical Consumption of Heatpumps and Power to Heat devices"] 
        solution["Total Fuel Costs"] = sum(solution["Fuel Costs:"].values()) 
        solution["Total CO2 Costs"] = sum(solution["CO2 Costs:"].values()) 
        solution["unit"] = unit_dict
        solution["Ambient Temperature"] = [instance.temperature_t[t] for t in instance.t] 
        solution["Radiation"] = [instance.radiation_t[t] for t in instance.t] 
        

        # only sum effective energy -> producton of solar thermal over  heat
        # demand is not shown in the Thermal Generation mix

        matrix = pd.DataFrame(solution["Thermal Power Energymix:"]).values
        sum_matrix = matrix.sum(1)
        demand = solution["Heat Demand"]

        dif = sum_matrix - demand
        mask = sum_matrix > demand
        reduce = mask*dif

        _dic = copy.deepcopy(solution)
        try:
            for j in instance.j_st:
                _dic["Thermal Power Energymix:"][j] = list(np.array(solution["Thermal Power Energymix:"][j]) - reduce)
                null = np.array(solution["Thermal Power Energymix:"][j])
                null *= null > 0
                _dic["Thermal Power Energymix:"][j] = list(null)
                solution["Thermal Generation Mix:"]  = pd.DataFrame(_dic["Thermal Power Energymix:"]).sum().to_dict()
        except:
            pass

#        solfile = os.path.join(path2solution, "solution.json")
#        with open(solfile, "w") as f:
#            json.dump(solution, f)
#        print("Done ! ,\nsaved to: <"+solfile+r"> ...")
            
        print("Done !")
        return solution
    except Exception as e:
        print("Error in creating JSON")
        print(e)
        return "Error3#"
#%%
def json2xlsx(data,output_path,scenario_flag=False): 
    json_data = copy.deepcopy(data) 
    unit_dict = json_data.pop("unit") 
    try:
        df5 = pd.DataFrame(json_data.pop("Loading Heat Storage"))
        df6 = pd.DataFrame(json_data.pop("efficiency"))  
        y = [pd.DataFrame([val],columns=list(val),index=[key]).T for key,val in json_data.items() if type(val)==dict and bool(val)]
        anual_per_tec_values= dict()
        for k,i in enumerate(y):
            if i[i.columns[0]].dtypes == object:
                key = f"{i.columns[0]} ({unit_dict[i.columns[0]].replace('/',' per ')})" 
                anual_per_tec_values[key] = i[i.columns[0]].apply(pd.Series).T 
                y.pop(k)
        # Worksheet technology data     
        df = y[0][:]
        for i in y[1:]:
            df = pd.concat([df,i],axis=1, sort = True)
        # Worksheet: anual data
        df2 = pd.DataFrame({key:val for key,val in json_data.items() if type(val)==list and len(val)==8760})
        # More Data
        df3 = pd.DataFrame([{key:val for key,val in json_data.items() if type(val)!=list and type(val)!=dict}],index=["value"]).T

        df.columns = df.columns.str.cat([f' [{unit_dict[x]}]' for x in df.columns]) 
        df2.columns = df2.columns.str.cat([f' [{unit_dict[x]}]' for x in df2.columns]) 
        df3.index = df3.index.str.cat([f' [{unit_dict[x]}]' for x in df3.index]) 
    
        dfs = {"Generator Data (single values)":df,
              "Anual Data":df2,
              "More Data":df3,
              **anual_per_tec_values,
              "Loading Heat Storage (MW)":df5,
              "efficiency (-)":df6,} 
        
        if scenario_flag: 
            return dfs 
        
        # alichaudry from stackoverflow
        # https://stackoverflow.com/questions/17326973/is-there-a-way-to-auto-adjust-excel-column-widths-with-pandas-excelwriter/32679806#32679806
        writer = pd.ExcelWriter(output_path,engine='xlsxwriter')
        for sheetname, df in dfs.items():  # loop through `dict` of dataframes
            sheetname=sheetname.replace(":","_")
            sheetname = sheetname[:31] # Excel worksheet name must be <= 31 chars 
            df.to_excel(writer, sheet_name=sheetname)  # send df to writer
            worksheet = writer.sheets[sheetname]  # pull worksheet object
            for idx, col in enumerate(df):  # loop through all columns
                series = df[col]
                max_len = max((
                    series.astype(str).map(len).max(),  # len of largest item
                    len(str(series.name))  # len of column name/header
                    )) + 1  # adding a little extra space
                worksheet.set_column(idx, idx, max_len)  # set column width
        writer.save()
        print("JSON to EXCEL Done")
#        print("Saved to"+output_path)
        
    except Exception as e:
        print(e)
        print("Error @ json2xlsx")

# =============================================================================
#%%
def scenarioJson2xlsx(scneario_mapper,solutions,output_path): 
    print("Creating Scenario Excel File...") 
    data = {} 
    writer = pd.ExcelWriter(output_path,engine='xlsxwriter') 
     
    for sc,sub_sc_list in scneario_mapper.items(): 
        for sub_sc in sub_sc_list: 
            x = solutions[sc][sub_sc]  
            if x != None: 
                dfs = json2xlsx(x,"",True) 
                for sheet,df in dfs.items(): 
                    data[sheet] = {**data.get(sheet,{}), **{(sc,sub_sc):df}} 
    for sheetname,_data in data.items(): 
        df = pd.concat(_data,axis= 0 if sheetname == "More Data" else 1) 
        if sheetname == "More Data": 
            df.index.names = ["Szenario","Sub Scenario","Topic"]         
        else: 
            df.columns.names = ["Szenario","Sub Scenario","Topic"]     
        sheetname=sheetname.replace(":","_") 
        sheetname = sheetname[:31] # Excel worksheet name must be <= 31 chars 
        if sheetname == "More Data": 
            df.to_excel(writer, sheet_name=sheetname,merge_cells=False)  # send df to writer 
        else: 
            df.T.to_excel(writer, sheet_name=sheetname,merge_cells=False)  # send df to writer 
        worksheet = writer.sheets[sheetname]  # pull worksheet object 
        for idx, col in enumerate(df):  # loop through all columns 
            series = df[col] 
            max_len = max(( 
                series.astype(str).map(len).max(),  # len of largest item 
                len(str(series.name))  # len of column name/header 
                )) + 1  # adding a little extra space 
            worksheet.set_column(idx, idx, max_len)  # set column width 
     
    writer.save() 
     
    print("Creating Scenario Excel File Done")        
         
     
    return None 
