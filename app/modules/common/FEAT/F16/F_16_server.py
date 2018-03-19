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
from bokeh.layouts import widgetbox,layout
from bokeh.models import ColumnDataSource,TableColumn,DataTable,CustomJS,TextInput
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs, Button,Div
import os,sys,io,base64
import pickle

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
    
    
from AD.F16_input.main import load_data 
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch


#%%
path_parameter = path+r"\AD\F16_input\DH_technology_cost.xlsx"
path2data = path+r"\AD\F16_input"
path_download_js = "download.js"
path_download_output= path + r"\FEAT\F16\download_input.xlsx"
path_upload_js = "upload.js"
path_spinner_html = "spinner2.html" 
#%%
io_loop = IOLoop.current()
global data_table,input_list,data_table_prices,data_table_data
#%%
data1 = pd.read_excel(path_parameter)[0:1]
input_list_mapper = dict(zip(data1.values[0].tolist(),list(data1)))
data2 = pd.read_excel(path_parameter,"prices and emmision factors")[0:1]
input_price_list_mapper = dict(zip(data2.values[0].tolist(),list(data2)))
data3 = pd.read_excel(path_parameter,"financal and other parameteres")[0:1]
parameter_list_mapper = dict(zip(data3.values[0].tolist(),list(data3)))

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

input_price_list = ["energy carrier","prices(EUR/MWh)","emission factor"]
parameter_list = ['CO2 Price',
 'Interes Rate [0-1]',
 'Total Renewable Factor [0-1]',
 'Total Demand[ MWh]']


#%%
def modify_doc(doc):      
 #%%   
    def execute(data,inv_flag,demand_f=1):
        val = dispatch.main(data,inv_flag,demand_f) 
        return val 
  #%%  
    data = pd.read_excel(path_parameter,skiprows=[0])
    col = [TableColumn(field=name, title=name) for name in input_list]
    source = ColumnDataSource(data)
    data_table = DataTable(source=source,columns=col,width=1550, 
                           height=800,editable=True)
    
    data_prices = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[0])
    col_prices = [TableColumn(field=name, title=name) for name in input_price_list]
    source_prices = ColumnDataSource(data_prices)
    data_table_prices = DataTable(source=source_prices,columns=col_prices,
                                  width=800, height=800,editable=True)
    
    data_data = pd.read_excel(path_parameter,"financal and other parameteres",skiprows=[0])
    col_data = [TableColumn(field=name, title=name) for name in parameter_list]
    source_data = ColumnDataSource(data_data)
    data_table_data = DataTable(source=source_data,columns=col_data,
                                  width=800, height=800,editable=True)
    
    
    dic = {"Parameter for Powerplants":data_table,"parameters":data_table_data,"prices & emission factors":data_table_prices}
    tabs_liste = [Panel(child=p, title=name) for name, p in dic.items()]
    tabs = Tabs(tabs=tabs_liste)


    #%%
    def download_callback():
        div_spinner.text = spinner_text
        print("Download...")
        df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
#        df = df.fillna(0)
        writer = pd.ExcelWriter(path_download_output)  
        df.to_excel(writer,'Parameter for Powerplants')
        
        data_prices_df = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore')
#        data_prices_df = data_prices_df.fillna(0)
        data_prices_df.to_excel(writer,'prices and emmision factors')
        
        data_data_df = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore')
#        data_data_df = data_data_df.fillna(0)
        data_data_df.to_excel(writer,'Data')
        writer.save()
        print("Download done.\nSaved to <"+path_download_output+">")
        div_spinner.text = """<strong style="color: green;">Download done.\nSaved to: """+path_download_output+"""</strong>""" 
    #%%
    def run_callback():
        output.tabs = []
        div_spinner.text = spinner_text
        print('calculation started...')
        data,inv_flag = load_data()
        elec = data["energy_carrier_prices"]["electricity"]
        
        data1= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        data1 = data1.fillna(0)
   
        data_prices = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore')
        data_prices = data_prices.fillna(0)
        
        data_data = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore')
        data_data = data_data.fillna(0)
        
        demand = np.array(list(data["demand_th"].values()))
        sum_demand = sum(demand)
 
        demand_neu = demand / float(sum_demand) * float(data_data[parameter_list[3]].values[0])
        data["demand_th"] = dict(zip(range(1,len(demand_neu)+1),demand_neu.tolist()))
        dic1 = data1.set_index("name").to_dict()
        for key in list(dic1):
            data[input_list_mapper[key]] = dic1[key]

        dic2 = data_prices.set_index(input_price_list[0]).to_dict()

        for key in list(dic2):
            data[key] = dic2[key]

        data["P_co2"] = float(data_data[parameter_list[0]].values[0])

        data["interest_rate"] = float(data_data[parameter_list[1]].values[0])

        data["toatl_RF"] = float(data_data[parameter_list[2]].values[0])

        data["total_demand"] = float(data_data[parameter_list[3]].values[0])
        
        data["energy_carrier_prices"]["electricity"] = elec
        
        solutions = None
        solutions,_,_ = execute(data,inv_flag)
        if solutions == "Error1":
#            print( 'No Capacities installed !!!')
            div_spinner.text = """<strong style="color: red;">Error: No Capacities are installed !!!</strong>"""
        elif solutions == "Error2":
#            print("The installed capacities are not enough to cover the load !!!" )
            div_spinner.text = """<strong style="color: red;">Error: The installed capacities are not enough to cover the load !!!</strong>""" 
        elif solutions == "Error3":
            print("Error in Saving Solution to JSON !!!")
            print("Cause: Infeasible or unbounded model !!!")
            div_spinner.text = """<strong style="color: red;">Error: Infeasible or unbounded model !!!</strong>""" 
        elif solutions == None:
            print("Error: Something get Wrong")
            div_spinner.text = """<strong style="color: red;">Error: Something get Wrong</strong>""" 
        else:
            tabs = plot_solutions()
            print('calculation done')
            if solutions == "Error4":
                print("Error @ Ploting  !!!")
                div_spinner.text = """<strong style="color: red;">Error: @ Ploting !!!</strong>""" 
            else:
                output.tabs = tabs
                div_spinner.text = """<strong style="color: green;">Calculation done</strong>""" 
        

#%%
    def upload_callback(attr, old, new):
        div_spinner.text = spinner_text
        print('Upload started')
        file_type = file_source.data['file_name'][0].split(".")[1]
        raw_contents = file_source.data['file_contents'][0]
        prefix, b64_contents = raw_contents.split(",", 1)
        file_contents = base64.b64decode(b64_contents)
        if  file_type in ["xlsx","xls"]:
            print(file_type)
            file_io = io.BytesIO(file_contents)
            excel_object = pd.ExcelFile(file_io, engine='xlrd')
            data2 = excel_object.parse(sheet_name = 'Parameter for Powerplants', index_col = 0,skiprows = range(21,50)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table.source.data.update(data2)
            
            data2 = excel_object.parse(sheet_name = 'prices and emmision factors', index_col = 0,skiprows = range(13,50)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_prices.source.data.update(data2)
            
            data2 = excel_object.parse(sheet_name = 'Data', index_col = 0).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            r = data2.shape[0] 
            data2 = excel_object.parse(sheet_name = 'Data', index_col = 0,skiprows = range(2,r+1)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_data.source.data.update(data2)
            
        elif file_type == "csv":
            print(file_type)
            file_io = io.StringIO(bytes.decode(file_contents))
            data2 = pd.read_csv(file_io).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table.source.data.update(data2)
        else:
            print("Not a valid file to upload")
            div_spinner.text = "Not a valid file to upload"
        print('Upload done')
        div_spinner.text = """<strong style="color: green;">Upload done</strong>"""
    #%%
    
    download_code=open(path_download_js).read()
    download_callback_js = CustomJS(args=dict(source=source), code=download_code)
    download_button = Button(label='Download Power Plant Parameters', button_type='success', callback=download_callback_js)
    download_button.on_click(download_callback)
    
    file_source = ColumnDataSource({'file_contents':[], 'file_name':[]})
    file_source.on_change('data', upload_callback)

     
    run_button = Button(label='Run Dispatch Model', button_type='primary')
    run_button.on_click(run_callback)
    
    upload_button = Button(label="Upload Power Plant Parameters", button_type="danger")
    upload_code=open(path_upload_js).read()
    upload_button.callback = CustomJS(args=dict(file_source=file_source), code =upload_code)
    
    spinner_text = open(path_spinner_html).read()

    div_spinner = Div(text="")
    output = Tabs(tabs=[])
    
    def reset_callback():
        div_spinner.text = spinner_text
        output.tabs = []
        div_spinner.text = ""
        
    reset_button = Button(label="Reset View", button_type="warning")
    reset_button.on_click(reset_callback)
    pmax = TextInput(title="Pmax [MW]")
    to_install = TextInput(title="Missing Capacities [MW]")
    
    _val = pickle.load(open(path2data+r"\data.dat", "rb"))
    _demand = np.array(list(_val["demand_th"].values()))
    _sum_demand = sum(_demand)
    f = max(_demand / _sum_demand)
    _val =  f * float(data_data[parameter_list[3]].values[0])
    pmax.value = str(_val)
    
    _data1= pd.DataFrame(data_table.source.data)[input_list[1]].apply(pd.to_numeric, errors='ignore')
    _data1 = _data1.fillna(0)
    x = float(pmax.value) - sum(_data1)
    if x>=0 :
        to_install.value = str(x)
    else:
        to_install.value = "0"
    
    
    
    def data_data_callback(attr, old, new):
        _val =  f * float(new[parameter_list[3]][0])
        pmax.value = str(_val)
        _data1= pd.DataFrame(data_table.source.data)[input_list[1]].apply(pd.to_numeric, errors='ignore')
        _data1 = _data1.fillna(0)
        x = float(pmax.value) - sum(_data1)
        if x>=0 :
            to_install.value = str(x)
        else:
            to_install.value = "0"
        
    
    def data_tabel_callback(attr, old, new):
        _data1= pd.DataFrame(new)[input_list[1]].apply(pd.to_numeric, errors='ignore')
        _data1 = _data1.fillna(0)
        x = float(pmax.value) - sum(_data1)
        if x>=0 :
            to_install.value = str(x)
        else:
            to_install.value = "0"
    
    data_table_data.source.on_change("data",data_data_callback)
    data_table.source.on_change("data",data_tabel_callback)
    
    
    l = layout([
            [widgetbox(download_button,upload_button,run_button,reset_button),
             widgetbox(div_spinner),widgetbox(Div(width=200, height=100)),widgetbox(pmax,Div(),to_install)],
            [widgetbox(output)],
            [widgetbox(tabs)],
            ], sizing_mode='fixed')

    doc.add_root(l)
    
#    doc.add_root(widgetbox(div_spinner,Panel(),download_button,upload_button,run_button,Panel(),tabs,Panel()))


bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Dispath Application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    try:
        io_loop.start()
    except:
        pass