# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 15:30:16 2018

@author: root
"""
from tornado.ioloop import IOLoop
import pandas as pd
import numpy as np
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource,TableColumn,DataTable,CustomJS
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs, Button
import os,sys,io,base64

global data_table,input_list,data_table_prices,data_table_data

io_loop = IOLoop.current()

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

from AD.F16_input.main import load_data 
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch

def execute(data,inv_flag,demand_f=1):
    val = dispatch.main(data,inv_flag,demand_f) 
    return val 


#%%

input_list= ['name',
 'installed capacity (MW_th)',
 'efficiency th',
 'efficiency el',
 'investment costs (EUR/MW_th)',
 'OPEX fix (EUR/MWa)',
 'OPEX var (EUR/MWh)',
 'life time',
 'potential restriction (MW_th)',
 'renewable factor']




path_parameter = r"C:\Users\Nesa\Desktop\DH_technology_cost.xlsx"
path_download_js = "download.js"
path_download_output= r"C:\Users\Nesa\Desktop\outputs.xlsx"
path_upload_js = "upload.js"

data1 = pd.read_excel(path_parameter)[0:1]
input_list_mapper = dict(zip(data1.values[0].tolist(),list(data1)))


def modify_doc(doc):      
        
    data = pd.read_excel(path_parameter,skiprows=[0])
    col = [TableColumn(field=name, title=name) for name in input_list]
    source = ColumnDataSource(data)
    data_table = DataTable(source=source,columns=col,width=1550, 
                           height=800,editable=True)
    
    data_prices = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[1])
    col_prices = [TableColumn(field="energy_carrier", title="energy carrier"), 
                  TableColumn(field="energy_carrier_prices",title="prices(EUR/MWh)"),
                  TableColumn(field="em",title="emission factor")]
    source_prices = ColumnDataSource(data_prices)
    data_table_prices = DataTable(source=source_prices,columns=col_prices,
                                  width=800, height=800,editable=True)
    
    data_data = pd.read_excel(path_parameter,"financal and other parameteres")
    col_data = [TableColumn(field="P_co2", title="C02 Price"), 
                  TableColumn(field="interest_rate",title="Interes Rate [0-1]"),
                  TableColumn(field="toatl_RF",title="Renewable Factor"),
                  TableColumn(field="total_demand",title="Total Demand")]
    source_data = ColumnDataSource(data_data)
    data_table_data = DataTable(source=source_data,columns=col_data,
                                  width=800, height=800,editable=True)
    
    
    
    dic = {"Parameter for Powerplants":data_table,"parameters":data_table_data,"prices & emission factors":data_table_prices}
    tabs_liste = [Panel(child=p, title=name) for name, p in dic.items()]
    tabs = Tabs(tabs=tabs_liste)

    download_code=open(path_download_js).read()
    download_callback_js = CustomJS(args=dict(source=source), code=download_code)
    #%%
    def download_callback():
        print("Download...")
        df= pd.DataFrame(data_table.source.data)[input_list]
        writer = pd.ExcelWriter(path_download_output)  
        df.to_excel(writer,'Parameter for Powerplants')
        
        data_prices_df = pd.DataFrame(data_table_prices.source.data)[["energy_carrier","energy_carrier_prices","em"]]
        data_prices_df.to_excel(writer,'prices and emmision factors')
        
        data_data_df = pd.DataFrame(data_table_data.source.data)[["total_demand","interest_rate","toatl_RF","P_co2"]]
        print(data_data_df)
        data_data_df.to_excel(writer,'Data')
        writer.save()
        print("Download done.\nSaved to <"+path_download_output+">")
        
    download_button = Button(label='Download', button_type='success', callback=download_callback_js)
    download_button = Button(label='Download', button_type='success')
    download_button.on_click(download_callback)
    #%%
    def run_callback():
        print('calculation started...')
        data,inv_flag = load_data()
       
        data1= pd.DataFrame(data_table.source.data)[input_list]
        data_prices = pd.DataFrame(data_table_prices.source.data)[["energy_carrier","energy_carrier_prices","em"]]
        data_data = pd.DataFrame(data_table_data.source.data)[["total_demand","interest_rate","toatl_RF","P_co2"]]
        print(data_data)
        demand = np.array(list(data["demand_th"].values()))
        sum_demand = sum(demand)
        print(sum_demand)
        print(data_data.total_demand.values[0])
        print(demand)
        demand_neu = demand / float(sum_demand) * float(data_data.total_demand.values[0])
        print("here")
        data["demand_th"] = dict(zip(range(1,len(demand_neu)+1),demand_neu.tolist()))
        print("Here2")
        
        dic1 = data1.set_index("name").to_dict()
        print("Here3")
        for key in list(dic1):
            data[input_list_mapper[key]] = dic1[key]
        print("Here4")
        dic2 = data_prices.set_index("energy_carrier").to_dict()
        print("Here5")
        for key in list(dic2):
            data[key] = dic2[key]
        print("Here6")
        data["P_co2"] = float(data_data.P_co2.values[0])
        print("Here7")
        data["interest_rate"] = float(data_data.interest_rate.values[0])
        print("Here8")
        data["toatl_RF"] = float(data_data.toatl_RF.values[0])
        print("Here9")
        data["total_demand"] = float(data_data.total_demand.values[0])
        print("Here10")
        
        
        solutions,instance,results = execute(data,inv_flag)
        if solutions != None:
            plot_solutions()  
        os.system("notepad.exe")
        print('calculation done')
#    %%
    def upload_callback(attr,old,new):
#        data2 = pd.read_excel(path)
        print('Upload started')
        file_type = file_source.data['file_name'][0].split(".")[1]
        raw_contents = file_source.data['file_contents'][0]
        prefix, b64_contents = raw_contents.split(",", 1)
        file_contents = base64.b64decode(b64_contents)
        if  file_type in ["xlsx","xls"]:
            print(file_type)
            file_io = io.BytesIO(file_contents)
            excel_object = pd.ExcelFile(file_io, engine='xlrd')
            data2 = excel_object.parse(sheet_name = 'Parameter for Powerplants', index_col = 0)
    #        print(data2)
            data_table.source.data.update(data2)
        elif file_type == "csv":
            print(file_type)
            file_io = io.StringIO(bytes.decode(file_contents))
            data2 = pd.read_csv(file_io)
            data_table.source.data.update(data2)
        else:
            print("Not a valid file to upload")
        print('Upload done')
    #%%   
    file_source = ColumnDataSource({'file_contents':[], 'file_name':[]})
    file_source.on_change('data', upload_callback)

     
    run_button = Button(label='Run', button_type='primary')
    run_button.on_click(run_callback)
    upload_button = Button(label="Upload", button_type="danger")
    upload_code=open(path_upload_js).read()
    upload_button.callback = CustomJS(args=dict(file_source=file_source), code =upload_code)
    upload_button.on_click(upload_callback)

    
    doc.add_root(widgetbox(download_button,upload_button,run_button,Panel(),tabs))

bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Dispath Application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()