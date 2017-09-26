# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import os
import json


def save_sol_to_json (instance,path2solution = os.path.split(os.path.abspath("__file__"))[0]+"\Solution" ):
    
    if os.path.isdir(path2solution) ==False:
        print("Create Solution Dictionary")
        os.mkdir(path2solution)
        
    solution={"Thermal Power Energymix":{j:[instance.x_th_jt[(j,t)]() for t in instance.t] for j in instance.j},
              "Installed Capacities": {j:instance.Cap_j[j]() for j in instance.j},
              "Eletrical Power Energymix (CHP's)":{j:[instance.x_el_jt[(j,t)]() for t in instance.t] for j in instance.j_kwk},
              "Eletrical Power Reserve (CHP's)": {j:[instance.x_el_bestand_jt[(j,t)]() for t in instance.t] for j in instance.j_kwk},
              "Thermal Power Reserve (CHP's)": {j:[instance.x_th_bestand_jt[(j,t)]() for t in instance.t] for j in instance.j_kwk},
               "Heat Storage Level": {k:[instance.stor_level_kt[(k,t)]() for t in instance.t] for k in instance.k},
               "Load Heat Storage Level": {k:[instance.load_kt[(k,t)]() for t in instance.t] for k in instance.k},
               "Unload Heat Storage Level": {k:[instance.unload_kt[(k,t)]() for t in instance.t] for k in instance.k},
               "Cogeneration Ramping": {j:[instance.ramp_KWK_jt[(j,t)]() for t in instance.t] for j in instance.j_kwk},
              "Waste Incineration Ramping": {j:[instance.ramp_muell_jt[(j,t)]() for t in instance.t] for j in instance.j_mv},
              "Maximum Capacity of Heat Storage": {k:instance.Cap_store_max_k[k]() for k in instance.k},
              "Load Capacity of Heat Storage": {k:instance.Cap_store_LadeLeistung_k[k]() for k in instance.k},
              "Unload Capacity of Heat Storage": {k:instance.Cap_store_Ent_LadeLeistung_k[k]() for k in instance.k},
              "Maximum electrical Power": instance.P_el_max()
            }
       
                                                                                                     
    
    with open(path2solution+r"\solution.json", "w") as f:
        json.dump(solution, f)

