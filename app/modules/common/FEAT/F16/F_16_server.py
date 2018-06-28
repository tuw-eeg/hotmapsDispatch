# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 15:30:16 2018

@author: root
"""
import matplotlib
matplotlib.use('agg',warn=False)
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
root_dir = os.path.dirname(os.path.abspath(__file__))

if path not in sys.path:
    sys.path.append(path)

#TODO: Upgrade to new bokeh version
import bokeh
if bokeh.__version__ != '0.12.10':
    print("Your current bokeh version ist not compatible (Your Version:" +bokeh.__version__+")")
    print("Please install bokeh==0.12.10")
    sys.exit()

import tornado
if tornado.version != '4.5.3':
    print("Your current tornado version ist not compatible (Your Version:" +tornado.version +")")
    print("Please install tornado==4.5.3")
    sys.exit()



from AD.F16_input.main import load_data
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch

#%%
def uniqueid():
    seed = 0
    while True:
       yield seed
       seed += 1

unique_id = uniqueid()
#%% Setting Global default paramters and default paths
path_parameter = os.path.join(path,*(r"\AD\F16_input\DH_technology_cost.xlsx".split("\\")))
path2data = os.path.join(path,*(r"\AD\F16_input".split("\\")))
path_download_js = "download.js"
path_download_output= os.path.join(path,*(r"\FEAT\F16\download_input.xlsx".split("\\")))
path_upload_js = os.path.join(root_dir, "upload.js")
path_spinner_html = os.path.join(root_dir, "spinner2.html")
path_spinner_load_html = os.path.join(root_dir, "spinner.html")
with open(path_spinner_load_html) as file:
    load_text = file.read()

with open(path_spinner_html) as file:
    spinner_text = file.read()
#%%
io_loop = IOLoop.current()
global data_table,data_table_prices,data_table_data,f,carrier_dict
carrier_dict ={}
#%%
def invert_dict(d):
    return dict([ (v, k) for k, v in d.items() ])

def load_extern_data(name):
    with open(os.path.join(path2data,name+"_name_map.dat"),"rb") as file:
        dict_map = pickle.load(file)
    dict_map_inv = invert_dict(dict_map)
    with open(os.path.join(path2data,name+"_profiles.dat"),"rb") as file:
        dic = pickle.load(file)
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
 'renewable factor',
 'must run [0-1]']

input_price_list = ["energy carrier","prices(EUR/MWh)","emission factor"]

parameter_list = ['CO2 Price',
 'Interest Rate [0-1]',
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
        data = pd.read_excel(path_parameter,skiprows=[0])[columns]
        data = pd.DataFrame({x:[] for x in columns})
    else:
        data = pd.read_excel(path_parameter,name,skiprows=[0])[columns]


    col = [TableColumn(field=name, title=name) for name in columns]
    source = ColumnDataSource(data)
    #,width=1550,height=700
    table = DataTable(source=source,columns=col,width=1550,
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
    label1 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; ">Heat Generators </h1>  """, width=210, height=10)
    button1= Button(label='🞧', width=30)
    label2 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; ">Heat Storages </h1>  """, width=180, height=10)
    button2= Button(label='🞧', width=30)

    col_hp_hs = column([row(label1,button1),data_table,row(label2,button2),data_table_heat_storage])

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
        global carrier_dict
        div_spinner.text = load_text
        print("Download...")

        df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        if df.shape[0] == 0:
            del df
            carrier_dict ={}
            div_spinner.text = """<strong style="color: red;">Nothing to download </strong>"""
            return
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
        data_hs_df.to_excel(writer,'Heat Storage')


        df_carrier = pd.DataFrame.from_dict(carrier_dict,orient="index")
        df_carrier["name"]=df_carrier.index
        df_carrier["carrier"] = df_carrier[0]
        del df_carrier[0]
        df_carrier.index = range(df_carrier.shape[0])
        df_carrier.to_excel(writer,'Energy Carrier')

        writer.save()

        print("Download done.\nSaved to <"+path_download_output+">")
        div_spinner.text = """<strong style="color: green;">Download done.\nSaved to: """+path_download_output+"""</strong>"""
    #%%
    def run_callback():
        global carrier_dict

        div_spinner.text = load_text
        output.tabs = []
        if type(grid.children[0]) != type(Div()):
            grid.children = [Div()]
        div_spinner.text = ""

        df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        if df.shape[0] == 0:
            del df
            carrier_dict ={}
            div_spinner.text = """<strong style="color: red;">No Heat Generators aviable </strong>"""
            return
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

        data["energy_carrier"] = {**data["energy_carrier"],**carrier_dict}

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
            output_tabs = plot_solutions()
            print('calculation done')
            if output_tabs == "Error4":
                print("Error @ Ploting  !!!")
                div_spinner.text = """<strong style="color: red;">Error: @ Ploting !!!</strong>"""
            else:
                output.tabs = output_tabs
                div_spinner.text = """<strong style="color: green;">Calculation done</strong>"""


#%%
    def upload_callback(attr, old, new):
        global carrier_dict
        div_spinner.text = load_text
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
            data2["index"] = data2.index
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

            data2 = excel_object.parse(sheet_name = 'Heat Storage', index_col = 0).apply(pd.to_numeric, errors='ignore')
            data2 = data2.fillna(0)
            data_table_heat_storage.source.data.update(data2)

            data2 = excel_object.parse(sheet_name = 'Energy Carrier', index_col = 0)
            global carrier_dict
            data2 = data2.set_index(data2["name"])
            del data2["name"]
            carrier_dict = data2.to_dict()["carrier"]
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
    with open(path_upload_js) as file:
        upload_code=file.read()
    upload_button.callback = CustomJS(args=dict(file_source=file_source), code =upload_code)

    div_spinner = Div(text="")
    output = Tabs(tabs=[])

    def reset_callback():
        div_spinner.text = load_text
        output.tabs = []
        div_spinner.text = ""
        grid.children = [Div()]

    reset_button = Button(label="Reset View", button_type="warning")
    reset_button.on_click(reset_callback)
    pmax = TextInput(title="Pmax [MW]",disabled=True)
    to_install = TextInput(title="Missing Capacities [MW]",disabled=True)

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

#%%

    data_tec = pd.read_excel(path_parameter,skiprows=[0])
    heat_pumps = {}
    flow_temp_dic = {}
    return_temp_dic = {}
    tec_mapper = {}
    for sheet in pd.ExcelFile(path_parameter).sheet_names:
        if sheet in ['Heat Generators','prices and emmision factors','financal and other parameteres',"Heat Storage", "Techologies"]:
            continue
        tec_mapper[sheet] = pd.read_excel(path_parameter,sheet).columns[0]
        heat_pumps[sheet] = pd.read_excel(path_parameter,sheet,skiprows=[0]).fillna(0).set_index("COP")
        flow_temp_dic[sheet] = heat_pumps[sheet].columns.values.tolist()
        return_temp_dic[sheet] = heat_pumps[sheet].index.values.tolist()




    tec_mapper_inv = invert_dict(tec_mapper)
    select_tec2_options= {"heat pump": list(tec_mapper.values()),
                          "CHP": data_tec[data_tec["output"] == "CHP"]["name"].values.tolist(),
                          "boiler":data_tec[data_tec["type"] == "boiler"]["name"].values.tolist()}

    grid = column(children=[Div()])
    ok_button = Button(label='✓ ADD', button_type='success',width=60)
    cancel_button = Button(label='	🞮 CANCEL', button_type='danger',width=60)
    select_tec = Select(title="Add Heat Generator:", options = pd.read_excel(path_parameter,"Techologies")["Techologies"].values.tolist())
    select_tec2 = Select()

    tabs_geneator = Tabs(tabs=[] ,width = 800)
    tec_buttons = widgetbox(children = [select_tec])
    children = [tec_buttons,widgetbox(tabs_geneator),row(children = [ok_button,cancel_button])]

    def add_heat_generator():
        output.tabs = []
        div_spinner.text = load_text
        grid.children = children
        select_tec.value = select_tec.options[0]
        div_spinner.text = ""
        installed_cap.end=int(float(pmax.value))+1
    button1.on_click(add_heat_generator)

    def cancel():
        div_spinner.text = load_text
        grid.children = [Div()]
        div_spinner.text = ""
    cancel_button.on_click(cancel)

    def add_to_cds():
        global carrier_dict
        div_spinner.text = load_text
        df2 = pd.DataFrame(data_table.source.data)
        df2.set_index(df2["index"])
        del df2["index"]
        new_data={}
        for x in input_list:
            if x == "name":
                new_data[x] = str(name_label.value)
            elif  x == 'must run [0-1]':
                new_data[x] = str(int(widgets_dict[x].active))
            else:
                new_data[x] = str(widgets_dict[x].value)

        df2 = df2.append(new_data,ignore_index=True)
        df2 = df2.apply(pd.to_numeric, errors='ignore')
        df2["index"] = df2.index
        _df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        if _df.shape[0] == 0:
            carrier_dict={}
        data_table.source.data.update(df2)
        del df2
#        grid.children = [Div()]
        div_spinner.text = """<strong style="color: green;">Heat Generator ADDED</strong>"""
        carrier_dict[name_label.value] = energy_carrier_select.value




    ok_button.on_click(add_to_cds)

    cop_label = TextInput(placeholder="COP", title="COP",disabled= True)
    flow_temp = Select(title="Flow Temperature")
    return_temp = Select(title="Return Temperature")
    cop_layout= column([row([return_temp,flow_temp]),cop_label])
    cop_panel = Panel(child=cop_layout, title="Coefficient of Performance, COP")

    energy_carrier_options = pd.read_excel(path_parameter,"prices and emmision factors",skiprows=[0])["energy carrier"].values.tolist()
    energy_carrier_select = Select(options = energy_carrier_options, title="Energy Carrier")
    energy_carrier_select.value = energy_carrier_options[0]

    n_th_label = TextInput(placeholder="-", title="Thermal Efficiency")
    n_el_label = TextInput(placeholder="-", title="Electrical Efficiency")

    opex_fix_label = TextInput(placeholder="-", title="OPEX fix (EUR/MWa)'")
    opex_var_label = TextInput(placeholder="-", title="OPEX var (EUR/MWh)")

    lt_label = TextInput(placeholder="-", title="life time (a)")
    ik_label = TextInput(placeholder="-", title="investment costs (EUR/MW_th")

    must_run_box = Toggle(label="Must Run",  button_type="warning")
    renewable_factor = Slider(start=0, end=1, value=0, step=.1, title="Renewable Factor")
    installed_cap = Slider(start=0, end=int(float(pmax.value))+1, value=0, step=1, title="Installed Capacity")

    name_label = TextInput(placeholder="-", title="Name",disabled=True)

    widgets_list= [
            [select_tec,select_tec2], installed_cap, n_th_label, n_el_label,
            ik_label, opex_fix_label, opex_var_label,lt_label,
            renewable_factor, must_run_box
            ]

    widgets_dict = dict(zip(input_list,widgets_list))


    tec_param_layout = column(children=[row(children=[energy_carrier_select,name_label]),
                                            row(children=[n_th_label,
                                                          n_el_label])])

    finance_param_layout = column(children=[row(children=[ik_label,lt_label]),
                                            row(children=[opex_fix_label,
                                                          opex_var_label])])
    model_param_layout = widgetbox(must_run_box,renewable_factor,installed_cap)

    tec_param_panel = Panel(child=tec_param_layout, title="Technical Parameters")
    finance_param_panel = Panel(child=finance_param_layout, title="Finance Parameters")
    model_param_panel = Panel(child=model_param_layout, title="Model Parameters")

    def add_heat_pump():

        flow_temp.options = flow_temp_dic[tec_mapper_inv[select_tec2.value]]
        flow_temp.value = flow_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback, thus need of try block
        return_temp.options = return_temp_dic[tec_mapper_inv[select_tec2.value]]
        return_temp.value = return_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback,
        cop_label.value = str(heat_pumps[tec_mapper_inv[select_tec2.value]].loc[return_temp.value,flow_temp.value])
        n_th_label.value = cop_label.value
        n_th_label.disabled = True
        tabs_geneator.tabs = [ cop_panel , tec_param_panel, finance_param_panel , model_param_panel]

    def add_tec(name,old,new):
        div_spinner.text = load_text
        n_th_label.disabled = False
        ###
        energy_carier_search = data_tec["input"][data_tec["type"].str.contains(select_tec.value)]
        if energy_carier_search.empty:
            energy_carrier_value = energy_carrier_select.options[0]
        else:
            energy_carrier_value = str(energy_carier_search.iloc[0])
        energy_carrier_select.value = energy_carrier_value
        ###
        for x in input_list:
            if x == "name":
                if widgets_dict[x][0].value not in widgets_dict[x][1].value:
                    name_label.value =  widgets_dict[x][0].value
                else:
                    name_label.value =  widgets_dict[x][1].value
                continue
            search = data_tec[x][data_tec["type"].str.contains(select_tec.value)]
            if search.empty:
                value = ""
            else:
                value = str(search.iloc[0])
            try:
                widgets_dict[x].value = value
            except:
                if x == 'must run [0-1]':
                    try:
                        widgets_dict[x].active = bool(int(x))
                    except:
                        widgets_dict[x].active = False
                    continue
                widgets_dict[x].value = 0

        if select_tec.value in ["heat pump","CHP","boiler"]:
            select_tec2.title= "Select a "+str(select_tec.value)+":"
            select_tec2.options = select_tec2_options[select_tec.value]
            tec_buttons.children = [select_tec,select_tec2]
            select_tec2.value = select_tec2.options[0]
        else:
            tec_buttons.children = [select_tec]
            tabs_geneator.tabs = [tec_param_panel, finance_param_panel , model_param_panel]

        div_spinner.text = ""

    select_tec.on_change('value', add_tec)
    ###
    def auto_load(name,old,new):
        if widgets_dict["name"][0].value not in widgets_dict["name"][1].value:
            name_label.value =  widgets_dict["name"][0].value
        else:
            name_label.value =  widgets_dict["name"][1].value

        if select_tec.value == "heat pump":
            add_heat_pump()
        else:
            energy_carrier_select.value = str(data_tec[data_tec["name"] == select_tec2.value]["input"].values[0])
            n_el_label.value =   str(data_tec[data_tec["name"] == select_tec2.value]["efficiency el"].values[0])
            n_th_label.value =   str(data_tec[data_tec["name"] == select_tec2.value]["efficiency th"].values[0])

            opex_fix_label.value = str(data_tec[data_tec["name"] == select_tec2.value]["OPEX fix (EUR/MWa)"].values[0])
            opex_var_label.value = str(data_tec[data_tec["name"] == select_tec2.value]["OPEX var (EUR/MWh)"].values[0])

            lt_label.value = str(data_tec[data_tec["name"] == select_tec2.value]["life time"].values[0])
            ik_label.value = str(data_tec[data_tec["name"] == select_tec2.value]["investment costs (EUR/MW_th)"].values[0])
            tabs_geneator.tabs = [tec_param_panel, finance_param_panel , model_param_panel]
    select_tec2.on_change('value', auto_load)

    def update_slider(name,old,new):
        try:
            installed_cap.end=int(float(pmax.value))+1
        except:
            pass
    pmax.on_change("value",update_slider)



    def cop_callback(name,old,new):
        try: # because of empty fields at the start no COP can be found
            cop_label.value = str(heat_pumps[tec_mapper_inv[select_tec2.value]].loc[return_temp.value,flow_temp.value])
            n_th_label.value = cop_label.value
            n_th_label.disabled = True
        except:
            pass
    flow_temp.on_change('value', cop_callback)
    return_temp.on_change('value', cop_callback)
#%%

    l = column([
                row([
                        widgetbox(download_button,upload_button,run_button,
                                  reset_button,invest),
                          widgetbox(div_spinner),
                          widgetbox(Div()),
                          widgetbox(pmax,Div(),to_install)]),
                 widgetbox(Div(height=25)),
                 grid,
                 widgetbox(Div(height=25)),
                 column([widgetbox(output)]),
                 widgetbox(tabs)],
            sizing_mode='scale_width')
#    l = layout([
#            [row([widgetbox(download_button,upload_button,run_button,reset_button,invest),
#             widgetbox(div_spinner),widgetbox(pmax,Div(),to_install)])],
#            [grid],
#            [widgetbox(output)],
#            [widgetbox(tabs)],
#            ], sizing_mode='scale_both')

    doc.add_root(l)

if __name__ == '__main__':
    allow_websocket_origin=None
    f_allow_websocket_origin = os.path.join(root_dir, 'allow_websocket_origin.txt')
    if os.path.exists(f_allow_websocket_origin):
        with open(f_allow_websocket_origin) as fd:
            allow_websocket_origin = [line.strip() for line in fd.readlines()]

    bokeh_app = Application(FunctionHandler(modify_doc))
    server = Server({'/': bokeh_app}, io_loop=io_loop, allow_websocket_origin=allow_websocket_origin)
    server.start()
    print('Opening Dispath Application on http://localhost:5006/')
    try:
        io_loop.start()
    except:
        pass
