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
from bokeh.layouts import widgetbox,layout,row,column
from bokeh.models import ColumnDataSource,TableColumn,DataTable,CustomJS,TextInput, Slider
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs, Button,Div,Toggle,Select,CheckboxGroup
import os,sys,io,base64
import pickle
from bokeh.plotting import figure
from bokeh.models import PanTool,WheelZoomTool,BoxZoomTool,ResetTool,SaveTool,HoverTool

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

#TODO: Upgrade to new bokeh version 
from bokeh import __version__
if __version__ != '0.12.10':
    print("Your current bokeh version ist not compatible (Your Version:" +__version__+")")
    print("Please install bokeh==0.12.10")
    sys.exit()    
    
from AD.F16_input.main import load_data 
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch


#%% Setting Global default paramters and default paths
path_parameter = path+r"\AD\F16_input\DH_technology_cost.xlsx"
path2data = path+r"\AD\F16_input"
path_download_js = "download.js"
path_download_output= path + r"\FEAT\F16\download_input.xlsx"
path_upload_js = "upload.js"
path_spinner_html = "spinner2.html" 
#%%
io_loop = IOLoop.current()
global data_table,data_table_prices,data_table_data,f
#%%
def invert_dict(d):
    return dict([ (v, k) for k, v in d.items() ])

def load_extern_data(name):
    dict_map = pickle.load(open(path2data+"\\"+name+"_name_map.dat","rb"))
    dict_map_inv = invert_dict(dict_map)
    dic = pickle.load(open(path2data+"\\"+name+"_profiles.dat","rb"))
    return dict_map,dict_map_inv,dic
    
def mapper(path2excel,worksheet_name=""):
    if worksheet_name == "":
        data = pd.read_excel(path2excel)[0:1]
    else:        
        data = pd.read_excel(path2excel,worksheet_name)[0:1]
    return dict(zip(data.values[0].tolist(),list(data)))
    
    
price_name_map,price_name_map_inv,prices = load_extern_data("price")
load_name_map,load_name_map_inv,load_profiles = load_extern_data("load")
radiation_name_map, radiation_name_map_inv,radiation = load_extern_data("radiation")
temperature_name_map, temperature_name_map_inv, temperature = load_extern_data("temperature")


input_list_mapper = mapper(path_parameter)
input_price_list_mapper = mapper(path_parameter,"prices and emmision factors")
parameter_list_mapper = mapper(path_parameter,"financal and other parameteres")
heat_storage_list_mapper = mapper(path_parameter,"Heat Storage")

input_list= ['name',
 'installed capacity (MW_th)',
 'efficiency th',
 'efficiency el',
 'investment costs (EUR/MW_th)',
 'OPEX fix (EUR/MWa)',
 'OPEX var (EUR/MWh)',
 'life time',
 'renewable factor']

input_price_list = ["energy carrier","prices(EUR/MWh)","emission factor"]

parameter_list = ['CO2 Price',
 'Interes Rate [0-1]',
 'Total Renewable Factor [0-1]',
 'Total Demand[ MWh]']


#%%   

def execute(data,inv_flag,selection=[[],[]],demand_f=1):
    val = dispatch.main(data,inv_flag,selection,demand_f) 
    return val

def drop_down(dic,map_dic):
    options =  list(set([map_dic[i[0]]+"_"+str(i[1]) for i in list(dic)]))
    options = sorted(options)
    return Select(title="Country-Year:", value="Wien_2016", options=options)

def cds(dd,dic,map_dic_inv):
    c,y = dd.value.split("_")
    y = dic[map_dic_inv[c],int(y)]
    x = np.arange(len(y))
    return ColumnDataSource(data=dict(x=x, y=y))

def init_load(select_load,data_table_data,load_profiles,source_load,map_dic_inv):
    c,year = select_load.value.split("_")
    y = float(data_table_data.source.data[parameter_list[3]][0])*load_profiles[map_dic_inv[c],int(year)]
    x = np.arange(len(y))
    source_load.data = dict(x=x, y=y)
    
def genearte_selection(dic,dict_key_map):
    """
    This function returns three objects:
        1. A Drop down menu
        2. A colum data source
        3. A Figure
    
    Parameters:
        dictionary:     dict
                        The data that should be ploted and selected,
                        
        dict_key_map:   dict
                        Mapping table, that maps the keys to a name
                        for example {AT:Austria}
        
        returns:        tuple
                        (dropdown,columDataSource,figure)
    """
    select = drop_down(dic,dict_key_map)
    source = cds(select,dic,invert_dict(dict_key_map))
    hover = HoverTool(tooltips=[("(x,y)", "($x, $y)")])
    TOOLS = [PanTool(),WheelZoomTool(),BoxZoomTool(),ResetTool(),SaveTool(),hover]
    fig = figure(tools=TOOLS)
    fig.line('x', 'y', source=source, line_alpha=0.6)
    fig.toolbar.logo = None
    
    return select,source,fig


def generate_tables(columns,name="",):
    if name == "":
        data = pd.read_excel(path_parameter,skiprows=[0])
    else:
        data = pd.read_excel(path_parameter,name,skiprows=[0])
        
    col = [TableColumn(field=name, title=name) for name in columns]
    source = ColumnDataSource(data)
    table = DataTable(source=source,columns=col,width=1550,height=550,
                           editable=True,row_headers =True)  
    
    return table  

def update_pmax(pmax,source_load,data_table,to_install):
    pmax.value = str(max(source_load.data["y"]))        
    _data1= pd.DataFrame(data_table.source.data)[input_list[1]].apply(pd.to_numeric, errors='ignore')
    _data1 = _data1.fillna(0)
    x = float(pmax.value) - sum(_data1)
    if x>=0 :
        to_install.value = str(x)
    else:
        to_install.value = "0"  
#%%
def modify_doc(doc):      
    
    data_table = generate_tables(input_list)
    data_table_prices = generate_tables(input_price_list,"prices and emmision factors") 
    data_table_data = generate_tables(parameter_list,"financal and other parameteres")
    data_table_heat_storage = generate_tables(list(heat_storage_list_mapper),"Heat Storage")
    
    scale_load = Slider(start=0, end=10, value=1, step=.1,title="Scale Demand")
    scale_price = Slider(start=0, end=10, value=1, step=.1,title="Scale Price")
    scale_price_sale = Slider(start=0, end=10, value=1, step=.1,title="Scale Price")
    scale_radiation = Slider(start=0, end=10, value=1, step=.1,title="Scale Radiation") 
    scale_temperature = Slider(start=0, end=10, value=1, step=.1,title="Scale Temperature")  
    

    select_load, source_load, plot_load = genearte_selection(load_profiles,load_name_map)    
    init_load(select_load,data_table_data,load_profiles,source_load,load_name_map_inv)
    total_demand = TextInput(value=str(data_table_data.source.data[parameter_list[3]][0]), title="Total Demand [MWh]")  
    
    def load_callback(attrname, old, new):
        total_demand.value = str(data_table_data.source.data[parameter_list[3]][0])
        c,year = select_load.value.split("_")
        y = float(data_table_data.source.data[parameter_list[3]][0])*load_profiles[load_name_map_inv[c],int(year)]*scale_load.value
        source_load.data["y"] = y.tolist() 
        update_pmax(pmax,source_load,data_table,to_install)
            
    select_load.on_change('value', load_callback)
    scale_load.on_change('value', load_callback)
    
    def load_callback2(attrname, old, new):
        data_table_data.source.data[parameter_list[3]] = [new]
        load_callback(None,None,None)
        
    total_demand.on_change("value",load_callback2)
    
    select_price, source_price, plot_price = genearte_selection(prices,price_name_map)
    feed_in_tarif = TextInput(value="0", title="Offset- FiT ( Feed in Tarif) :")
    const_price = TextInput(value="0", title="Constant - Flat Price:")
    mean_price = CheckboxGroup(labels=["use mean electricity price"])
    
    def price_callback(attrname, old, new):
        if mean_price.active != []:
            c,year = select_price.value.split("_")
            source_price.data["y"] = [np.mean(prices[price_name_map_inv[c],int(year)])]*8760       
        else:
            if feed_in_tarif.value =="":
                feed_in_tarif.value = "0"
            if const_price.value =="":
                const_price.value = "0"
            if float(const_price.value) == 0 :
                c,year = select_price.value.split("_")
                source_price.data["y"] = (np.array(prices[price_name_map_inv[c],int(year)]) * scale_price.value + float(feed_in_tarif.value)).tolist()          
            else:
                source_price.data["y"] = (np.array([float(feed_in_tarif.value)+float(const_price.value)]*8760) * scale_price.value ).tolist() 
            
    select_price.on_change('value', price_callback)
    feed_in_tarif.on_change("value", price_callback)
    const_price.on_change("value", price_callback)   
    scale_price.on_change('value', price_callback)
    mean_price.on_change('active', price_callback)
#%%#TODO: Modify for non redundant code  
    select_price_sale, source_price_sale, plot_price_sale = genearte_selection(prices,price_name_map)
    feed_in_tarif_sale = TextInput(value="0", title="Offset- FiT ( Feed in Tarif) :")
    const_price_sale = TextInput(value="0", title="Constant - Flat Price:")
    mean_price_sale = CheckboxGroup(labels=["use mean electricity price"])
    
    def price_callback_sale(attrname, old, new):
        if mean_price_sale.active != []:
            c,year = select_price_sale.value.split("_")
            source_price_sale.data["y"] = [np.mean(prices[price_name_map_inv[c],int(year)])]*8760       
        else:
            if feed_in_tarif_sale.value =="":
                feed_in_tarif_sale.value = "0"
            if const_price_sale.value =="":
                const_price_sale.value = "0"
            if float(const_price_sale.value) == 0 :
                c,year = select_price_sale.value.split("_")
                source_price_sale.data["y"] = (np.array(prices[price_name_map_inv[c],int(year)]) * scale_price_sale.value + float(feed_in_tarif_sale.value)).tolist()          
            else:
                source_price_sale.data["y"] = (np.array([float(feed_in_tarif_sale.value)+float(const_price_sale.value)]*8760) * scale_price_sale.value ).tolist() 
            
    select_price_sale.on_change('value', price_callback_sale)
    feed_in_tarif_sale.on_change("value", price_callback_sale)
    const_price_sale.on_change("value", price_callback_sale)   
    scale_price_sale.on_change('value', price_callback_sale)
    mean_price_sale.on_change('active', price_callback_sale) 
#%%
    select_radiation,source_radiation,plot_radiation = genearte_selection(radiation,radiation_name_map)
    select_temperature, source_temperature, plot_temperature = genearte_selection(temperature,temperature_name_map)
    
    def temperature_callback(attrname, old, new):
        c,year = select_temperature.value.split("_")
        y = temperature[temperature_name_map_inv[c],int(year)]*scale_temperature.value
        source_temperature.data["y"] = y.tolist() 
    
    select_temperature.on_change('value', temperature_callback)
    scale_temperature.on_change('value', temperature_callback)
        
    def radiation_callback(attrname, old, new):
        c,year = select_radiation.value.split("_")
        y = radiation[radiation_name_map_inv[c],int(year)]*scale_radiation.value
        source_radiation.data["y"] = y.tolist() 
        
    scale_radiation.on_change('value', radiation_callback)
    select_radiation.on_change('value', radiation_callback)
    
    row_load = row(column(widgetbox(select_load),plot_load),
                    column(widgetbox(scale_load),widgetbox(total_demand))
                    )
 
    row_temp = row(column(widgetbox(select_temperature),plot_temperature),
                    column(widgetbox(scale_temperature))
                    )
    
    row_rad = row(column(widgetbox(select_radiation),plot_radiation),
                    column(widgetbox(scale_radiation))
                    )
    
    row_price = row(column(widgetbox(select_price),plot_price),
                    column(widgetbox(feed_in_tarif),widgetbox(const_price),
                           widgetbox(scale_price),widgetbox(mean_price))
                    )
                    
    row_price_sale = row(column(widgetbox(select_price_sale),plot_price_sale),
                    column(widgetbox(feed_in_tarif_sale),widgetbox(const_price_sale),
                           widgetbox(scale_price_sale),widgetbox(mean_price_sale))
                    )
    label1 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; "> Heat Generators:</h1> """)
    label2 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; "> Heat Storages:</h1> """)
    col_hp_hs = column(label1,data_table,label2,data_table_heat_storage)
    
    dic = {"Heat Producers and Heat Storage":col_hp_hs,
           "Parameters":data_table_data,
           "Prices & Emission factors":data_table_prices,
           "Head Demand":row_load,
           "Electricity price":row_price,
           "Sale Electricity price":row_price_sale,
           "Temperature":row_temp,
           "Radiation":row_rad}
    
    tabs_liste = [Panel(child=p, title=name) for name, p in dic.items()]
    
    tabs = Tabs(tabs=tabs_liste)


    def download_callback():
        div_spinner.text = spinner_text
        print("Download...")
        df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
#        df = df.fillna(0)
        writer = pd.ExcelWriter(path_download_output)  
        df.to_excel(writer,'Heat Generators')
        
        data_prices_df = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore')
#        data_prices_df = data_prices_df.fillna(0)
        data_prices_df.to_excel(writer,'prices and emmision factors')
        
        data_data_df = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore')
#        data_data_df = data_data_df.fillna(0)
        data_data_df.to_excel(writer,'Data')
        
        data_hs_df = pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore')
#        data_hs_df = data_hs_df.fillna(0)
        data_hs_df.to_excel(writer,'Heat Storages')
        
        writer.save()
        print("Download done.\nSaved to <"+path_download_output+">")
        div_spinner.text = """<strong style="color: green;">Download done.\nSaved to: """+path_download_output+"""</strong>""" 
    #%%
    def run_callback():
        output.tabs = []
        div_spinner.text = spinner_text
        print('calculation started...')
        data,_ = load_data()
        
                
        data1= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        data1 = data1.fillna(0)
   
        data_prices = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore')
        data_prices = data_prices.fillna(0)
        
        data_data = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore')
        data_data = data_data.fillna(0)
        
        data_heat_storages = pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore')
        data_heat_storages = data_heat_storages.fillna(0)
        dic_hs = data_heat_storages.set_index("name").to_dict()
        for key in list(dic_hs):
            data[heat_storage_list_mapper[key]] = dic_hs[key]
        

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
        
        data["demand_th"] = dict(zip(range(1,len(source_load.data["y"])+1),source_load.data["y"]))
        data["energy_carrier_prices"]["electricity"] = dict(zip(range(1,len(source_price.data["y"])+1),source_price.data["y"]))
        data["sale_electricity"] = dict(zip(range(1,len(source_price_sale.data["y"])+1),source_price_sale.data["y"]))

        data["radiation"] = dict(zip(range(1,len(source_radiation.data["y"])+1),source_radiation.data["y"]))
        data["temp"] = dict(zip(range(1,len(source_temperature.data["y"])+1),source_temperature.data["y"]))
        
        data["tec_hs"] = list(data_heat_storages["name"].values)
        data["tec"] = list(data1["name"].values)
        
        data["all_heat_geneartors"] = data["tec"] + data["tec_hs"]
        
        solutions = None
        selection = [[],[]]
        inv_flag = False
        if invest.active:
            inv_flag = True
            selection0 = data_table.source.selected["1d"]["indices"]
            selection1 = data_table_heat_storage.source.selected["1d"]["indices"]
            selection = [selection0,selection1]
            if selection[0] == []:
                div_spinner.text = """<strong style="color: red;">Error: Please specify the technologies for for the invesment model !!!</strong>"""
                return
        solutions,_,_ = execute(data,inv_flag,selection)
        if solutions == "Error1":
            div_spinner.text = """<strong style="color: red;">Error: No Capacities are installed !!!</strong>"""
        elif solutions == "Error2":
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
            if tabs == "Error4":
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
            data2 = excel_object.parse(sheet_name = 'Heat Generators', index_col = 0,skiprows = range(22,50)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table.source.data.update(data2)
            
            data2 = excel_object.parse(sheet_name = 'prices and emmision factors', index_col = 0,skiprows = range(14,50)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_prices.source.data.update(data2)
            
            data2 = excel_object.parse(sheet_name = 'Data', index_col = 0).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            r = data2.shape[0] 
            data2 = excel_object.parse(sheet_name = 'Data', index_col = 0,skiprows = range(2,r+1)).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_data.source.data.update(data2)
            
            data2 = excel_object.parse(sheet_name = 'Heat Storages', index_col = 0).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_heat_storage.source.data.update(data2)
            div_spinner.text = """<strong style="color: green;">Upload done</strong>"""
        else:
            print("Not a valid file to upload")
            div_spinner.text = """<strong style="color: red;">Not a valid file to uploade</strong>"""
        print('Upload done')
        
    #%%
#XXX: How to Download file from Server with JS ?  (currently obsoulete, saves to path of this file)    
#    download_code=open(path_download_js).read()
#    download_callback_js = CustomJS(args=dict(source=source), code=download_code)
#    download_button = Button(label='Download Power Plant Parameters', button_type='success', callback=download_callback_js)
    download_button = Button(label='Download Power Plant Parameters', button_type='success')
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
    
    update_pmax(pmax,source_load,data_table,to_install)    
    
    data_table_data.source.on_change("data",load_callback)
    data_table.source.on_change("data",load_callback)
    
    invest = Toggle(label="Invest", button_type="default")
    
    def ivest_callback(active):
        if active:
            div_spinner.text = """<strong style="color: red;">Mark Technologies by pressing "CTRL" +  "left mouse", Rows are marked yellow </strong>""" 
        else:
            div_spinner.text = ""
            
            
    invest.on_click(ivest_callback)
    
    l = layout([
            [widgetbox(download_button,upload_button,run_button,reset_button,invest),
             widgetbox(div_spinner),widgetbox(Div(width=100, height=100)),widgetbox(pmax,Div(),to_install)],
            [widgetbox(output)],
            [widgetbox(tabs)],
            ], sizing_mode='scale_width')

    doc.add_root(l)
    
if __name__ == '__main__':
    bokeh_app = Application(FunctionHandler(modify_doc))
    server = Server({'/': bokeh_app}, io_loop=io_loop)
    server.start()
    print('Opening Dispath Application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    try:
        io_loop.start()
    except:
        pass