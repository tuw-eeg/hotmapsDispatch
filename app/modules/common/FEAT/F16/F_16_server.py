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
from bokeh.application.handlers import FunctionHandler,DirectoryHandler
from bokeh.application import Application
from bokeh.layouts import widgetbox,row,column,layout
from bokeh.models import ColumnDataSource,TableColumn,DataTable,CustomJS,TextInput, Slider
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs, Button,Div,Toggle,Select,CheckboxGroup
import os,sys,io,base64,pickle,datetime,json#,shutil
from bokeh.plotting import figure,output_file,save
from bokeh.models import PanTool,WheelZoomTool,BoxZoomTool,ResetTool,SaveTool,HoverTool
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
root_dir = os.path.dirname(os.path.abspath(__file__))

if path not in sys.path:
    sys.path.append(path)
#%%
#TODO: Upgrade to new bokeh version
import bokeh
if bokeh.__version__ != '0.12.10':
    print("Your current bokeh version ist not compatible (Your Version:" +bokeh.__version__+")")
    print("Please install bokeh==0.12.10")
    sys.exit()

import tornado 
# früher (4.5.3) aber Download funktioniert dann nicht
if tornado.version != '4.4.2':  
    print("Your current tornado version ist not compatible (Your Version:" +tornado.version +")")
    print("Please install tornado==4.5.3")
    sys.exit()
#%%
from AD.F16_input.main import load_data
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch

#%% Setting Global default paramters and default paths
path_parameter = os.path.join(path, "AD", "F16_input", "DH_technology_cost.xlsx")
path2data = os.path.join(path, "AD", "F16_input")
path_download_js = os.path.join(root_dir, "download.js")
path_static = os.path.join(path2data,"static")
if not os.path.exists(path_static):
    os.makedirs(path_static)
#    f = open(os.path.join(path2data,"main.py"), "w")
#    f.close()
path_upload_js = os.path.join(root_dir, "upload.js")
path_spinner_html = os.path.join(root_dir, "spinner2.html")
path_spinner_load_html = os.path.join(root_dir, "spinner.html")
#%%

global data_table,data_table_prices,data_table_data,f,carrier_dict
carrier_dict ={}
#%%
# =============================================================================
# RUN MODEL
# =============================================================================
def execute(data,inv_flag,selection=[[],[]],demand_f=1):
    val = dispatch.main(data,inv_flag,selection,demand_f)
    return val
#%%
# =============================================================================
# Global Functions
# =============================================================================
def invert_dict(d):
    return dict([ (v, k) for k, v in d.items() ])
# =============================================================================
def load_extern_data(name):
    with open(os.path.join(path2data,name+"_name_map.dat"),"rb") as file:
        dict_map = pickle.load(file)
    dict_map_inv = invert_dict(dict_map)
    with open(os.path.join(path2data,name+"_profiles.dat"),"rb") as file:
        dic = pickle.load(file)
    return dict_map,dict_map_inv,dic
# =============================================================================
def mapper(path2excel,worksheet_name=""):
    if worksheet_name == "":
        data = pd.read_excel(path2excel)[0:1]
    else:
        data = pd.read_excel(path2excel,worksheet_name)[0:1]
    return dict(zip(data.values[0].tolist(),list(data)))
# =============================================================================
def drop_down(dic,map_dic):
    options =  list(set([map_dic[i[0]]+"_"+str(i[1]) for i in list(dic)]))
    options = sorted(options)
    return Select(title="Country-Year:", value="Wien_2016", options=options)
# ===========================================================================
def cds(dd,dic,map_dic_inv):
    c,y = dd.value.split("_")
    y = dic[map_dic_inv[c],int(y)]
    x = np.arange(len(y))
    return ColumnDataSource(data=dict(x=x, y=y))
# ===========================================================================
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
# ===========================================================================
def generate_tables(columns,name="",):
    if name == "":
#        data = pd.read_excel(path_parameter,skiprows=[0])[columns]
        data = pd.DataFrame({x:[] for x in columns+["type"]})
    else:
        data = pd.read_excel(path_parameter,name,skiprows=[0])[columns]


    col = [TableColumn(field=name, title=name) for name in columns]
    source = ColumnDataSource(data)
    #,width=1550,height=700
    table = DataTable(source=source,columns=col,width=1550,
                           editable=True,row_headers =True)
    return table
# ===========================================================================
def modification_tools(**kwargs):
    """
    This function returns 5 Tools for modifaction of the shown input data:
    Parameters:
        kwargs                  dict
                                specify the labels of the tools
    Return:
        list with 5 etnries
        1. offset               bokeh.models.TextInput
        2. constant             bokeh.models.TextInput
        3. scale                bokeh.models.Slider
        4. mean                 bokeh.models.CheckboxGroup
        5. total                bokeh.models.TextInput
        6. tec                  bokeh.models.Select
        7. ok                   bokeh.models.Button
    """
    args = [ TextInput(value="0", title=kwargs.setdefault("offset","Offset- FiT ( Feed in Tarif) :")),
            TextInput(value="-", title=kwargs.setdefault("constant","Constant - Flat Price:")),
            Slider(start=0, end=10, value=1, step=.1,title=kwargs.setdefault("scale","Scale Price:")),
            CheckboxGroup(labels=[kwargs.setdefault("mean","use mean electricity price")]),
            TextInput(value="1", title=kwargs.setdefault("total","Total Price"), disabled=True),
            Select(title=kwargs.setdefault("tec","add to heat producer"), value="Default", options=[]),
            Button(label='✓', button_type='success',width=60)
            ]
    return args
# ===========================================================================
def generate_widgets(data):
    select,source,figure = genearte_selection(data["data"],data["dic"])
    offset,constant,scale,mean,total,tec,ok = modification_tools(**data["labels"])
    return dict(select=select,source=source,figure=figure,offset=offset,
                constant=constant,scale=scale,mean= mean,total=total,tec=tec,
                ok=ok)
# ===========================================================================
def generate_layout(widgets):
    return row( column(widgetbox(widgets["select"]),widgets["figure"]),
                column(widgetbox(widgets["offset"]),widgetbox(widgets["constant"]),
                       widgetbox(widgets["scale"]),widgetbox(widgets["mean"])))
# ===========================================================================
def new_name(name,liste):
    if name in liste:
        try:
            return  new_name(name[:-1]+str(int(name[-1])+1),liste)
        except:
            return new_name(name+" 1",liste)
    else:
        return name
# ===========================================================================
def profil(value_list):
    s = sum(value_list)
    try:
        y= np.array(value_list) / s
    except:
        y = np.zeros(8760)
    return y,s
# =============================================================================
#  Global Data
# =======================================================================

# Load JS Code (for Download and Upload) and HTML Code (for) Spinners)
with open(path_spinner_load_html) as file:
    load_text = file.read()
with open(path_spinner_html) as file:
    spinner_text = file.read()
with open(path_download_js) as file:
    download_code=file.read()
with open(path_upload_js) as file:
    upload_code=file.read()
# Load External Data from .dat files
price_name_map,price_name_map_inv,prices = load_extern_data("price")
load_name_map,load_name_map_inv,load_profiles = load_extern_data("load")
radiation_name_map, radiation_name_map_inv,radiation = load_extern_data("radiation")
temperature_name_map, temperature_name_map_inv, temperature = load_extern_data("temperature")
# Specify Sheet Names of the Excel Database (If Changed)
sheets = ['Heat Generators','prices and emmision factors',
          'financal and other parameteres',"Heat Storage", "Techologies"]
# Mapping model names with names to display in browser, specified in Database-Excel
input_list_mapper = mapper(path_parameter)
input_price_list_mapper = mapper(path_parameter,sheets[1])
parameter_list_mapper = mapper(path_parameter,sheets[2])
heat_storage_list_mapper = mapper(path_parameter,sheets[3])
# select witch parameters to show
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
# select default labels for the modification tools
lab = dict(offset="Offset",constant="Set To Constant",
           mean="Use mean value",total="Sum",scale="Scale")
# Set Names of the tabs for the external data
widgets_keys = ["Radiation","Temperature","Electricity price",
                "Sale Electricity price","Heat Demand"]
# Specify model names for the external data
model_keys = ["radiation","temp","electricity","sale_electricity",
                      "demand_th"]
# string for "Heat Demand"
_hd = widgets_keys[-1]
# string for "electricity prices"
_elec = widgets_keys[2:4]
# Database for the external data manipulation,
widgets_data = [ dict(data=radiation,
                      dic=radiation_name_map,
                      dic_inv = invert_dict(radiation_name_map),
                      labels=lab),
                dict(data=temperature,
                      dic=temperature_name_map,
                      dic_inv = invert_dict(temperature_name_map),
                      labels=lab),
                dict(data=prices,
                      dic=price_name_map,
                      dic_inv = invert_dict(price_name_map),
                      labels=dict()),
                dict(data=prices,
                      dic=price_name_map,
                      dic_inv = invert_dict(price_name_map),
                      labels=dict()),
                dict(data=load_profiles,
                      dic=load_name_map,
                      dic_inv = invert_dict(load_name_map),
                      labels=lab),
                ]
# Create Data structure for better code handling
widget_to_model_keys_dict = dict(zip(widgets_keys,model_keys))
data_kwargs = dict(zip(widgets_keys,widgets_data))
#external_data = dict(zip(widgets_keys,[{}]*len(widgets_keys))) #XXX only copy
external_data = dict(zip(widgets_keys,[{} for _ in range(len(widgets_keys))]))

# =============================================================================
#  Data for adding Technologies
# =============================================================================
data_tec = pd.read_excel(path_parameter,skiprows=[0])
heat_pumps = {}
flow_temp_dic = {}
return_temp_dic = {}
tec_mapper = {}
for sheet in pd.ExcelFile(path_parameter).sheet_names:
    if sheet in sheets:
        continue
    tec_mapper[sheet] = pd.read_excel(path_parameter,sheet).columns[0]
    heat_pumps[sheet] = pd.read_excel(path_parameter,sheet,skiprows=[0]).fillna(0).set_index("COP")
    flow_temp_dic[sheet] = heat_pumps[sheet].columns.values.tolist()
    return_temp_dic[sheet] = heat_pumps[sheet].index.values.tolist()

select_tec_options_model = pd.read_excel(path_parameter,"Techologies")["Techologies"].values.tolist()
select_tec_options = [x.replace("CHP-SE","CHP Steam Extraction").replace("CHP-BP","CHP Back Pressure") for x in select_tec_options_model]
select_tec_mapper = dict(zip(select_tec_options,select_tec_options_model))
tec_mapper_inv = invert_dict(tec_mapper)
select_tec2_options= {"heat pump": list(tec_mapper.values()),
                      "CHP Back Pressure": data_tec[data_tec["output"] == "CHP-BP"]["name"].values.tolist(),
                      "CHP Steam Extraction": data_tec[data_tec["output"] == "CHP-SE"]["name"].values.tolist(),
                      "boiler":data_tec[data_tec["type"] == "boiler"]["name"].values.tolist()}
energy_carrier_options = pd.read_excel(path_parameter,sheets[1],skiprows=[0])[input_price_list[0]].values.tolist()
#%%
#%%
# =============================================================================
# Function Handler
# =============================================================================
def modify_doc(doc):
# =============================================================================
#   MAIN GUI Elements
# =============================================================================
    data_table = generate_tables(input_list)
    data_table_prices = generate_tables(input_price_list,sheets[1])
    data_table_data = generate_tables(parameter_list,sheets[2])
    data_table_heat_storage = generate_tables(list(heat_storage_list_mapper),sheets[3])
    widgets= { i : generate_widgets(data_kwargs[i]) for i in data_kwargs}
    dummy = Div(text="""<strong style="color: #FFFFFF;">1</strong>""")
    download_button = Button(label='Download Power Plant Parameters', button_type='success')
    run_button = Button(label='Run Dispatch Model', button_type='primary')
    upload_button = Button(label="Upload Power Plant Parameters", button_type="danger")
    reset_button = Button(label="Reset View", button_type="warning")
    div_spinner = Div(text="")
    output = Tabs(tabs=[])
    pmax = TextInput(title="Pmax [MW]",disabled=True)
    to_install = TextInput(title="Missing Capacities [MW]",disabled=True)
    invest_button = Toggle(label="Invest", button_type="default")
    label1 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; ">Heat Generators </h1>  """, width=210, height=10)
    button1= Button(label='🞧', width=30)
    label2 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; ">Heat Storages </h1>  """, width=180, height=10)
    button2= Button(label='🞧', width=30)
# =============================================================================
#   Layout for Main GUI
# =============================================================================
    col_hp_hs = column([row(label1,button1),data_table,row(label2,button2),data_table_heat_storage])
    lay = { i : generate_layout(widgets[i]) for i in data_kwargs}
    dic = {"Heat Producers and Heat Storage":col_hp_hs,
           "Parameters":data_table_data,
           "Prices & Emission factors":data_table_prices}
    # Change layout of Heat Demand Tab -> Add Total Demand
    widgets[_hd]["total"].title = "Set Total Demand (MWh)"
    widgets[_hd]["total"].disabled=False
    lay[_hd].children[1].children = [widgetbox(widgets[_hd]["total"])]
    # Change layout of Electricity Tabs -> Select technologies to add external data
    for i in _elec:
        lay[i].children.append(column(widgetbox(widgets[i]["tec"]), widgetbox(widgets[i]["ok"])))
    dic =  {**dic, **lay}
    tabs_liste = [Panel(child=p, title=name) for name, p in dic.items()]
    tabs = Tabs(tabs=tabs_liste)
# =============================================================================
#   Callbacks for Main GUI
# =============================================================================
    def download_callback():
        try:
            global carrier_dict
            div_spinner.text = load_text
            print("Download...")

            df= pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore')
            if df.shape[0] == 0:
                del df
                carrier_dict ={}
                div_spinner.text = """<div align="center"> <strong style="color: red;">Nothing to download </strong> </div>"""
                return
    #        df = df.fillna(0)
            time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
            filename = "download_input.xlsx"
            path_download = os.path.join(create_folder(time_id),filename)

            writer = pd.ExcelWriter(path_download)
            df.to_excel(writer,sheets[0])

            data_prices_df = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore')
    #        data_prices_df = data_prices_df.fillna(0)
            data_prices_df.to_excel(writer,sheets[1])

            data_data_df = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore')
    #        data_data_df = data_data_df.fillna(0)
            data_data_df.to_excel(writer,"Data")

            data_hs_df = pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore')
    #        data_hs_df = data_hs_df.fillna(0)
            data_hs_df.to_excel(writer,sheets[3])


            df_carrier = pd.DataFrame.from_dict(carrier_dict,orient="index")
            df_carrier["name"]=df_carrier.index
            df_carrier["carrier"] = df_carrier[0]
            del df_carrier[0]
            df_carrier.index = range(df_carrier.shape[0])
            df_carrier.to_excel(writer,'Energy Carrier')

            writer.save()
            trigger_download(time_id,filename)
            print("Download done.\nSaved to <"+path_download+">")
    #TODO wait untill download has finished and delete folder
    #       or extra script that delete te content of the static folder after 2 hours or something else
    #        shutil.rmtree(path_download_dir, ignore_errors=True)
            div_spinner.text = """<div align="center"> <strong style="color: green;">Download done.</strong> </div>"""
        except Exception as e:
            print(str(e))
            div_spinner.text = """<div align="center"> <strong style="color: red;">Fatal Error @ Download </strong> </div>"""
# =============================================================================
    def run_callback():
        try:
            global carrier_dict

            df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
            if df.shape[0] == 0:
                del df
                carrier_dict ={}
                div_spinner.text = """<div align="center"> <strong style="color: red;">No Heat Generators aviable </strong> </div>"""
                return

            if float(to_install.value) > 0 and not invest_button.active:
                div_spinner.text = """<div align="center"> <strong style="color: red;">The installed capacities are not enough to cover the load</strong> </div>"""
                return

            div_spinner.text = load_text
            output.tabs = []
            if type(grid.children[0]) != type(Div()):
                grid.children = [Div()]
            div_spinner.text = ""


            div_spinner.text = spinner_text
            print('calculation started...')
#            data,_ = load_data()
            data = {}
            data["energy_carrier_prices"] = {}
            data["energy_carrier"] = {}
            data["threshold_heatpump"] = 0


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
                data[input_price_list_mapper[key]] = dic2[key]


            data["P_co2"] = float(data_data[parameter_list[0]].values[0])
            data["interest_rate"] = float(data_data[parameter_list[1]].values[0])
            data["toatl_RF"] = float(data_data[parameter_list[2]].values[0])
            data["total_demand"] = float(data_data[parameter_list[3]].values[0])

            for wk,mk in widget_to_model_keys_dict.items():
                if mk == "electricity":
                   data["energy_carrier_prices"][mk]= dict(zip(range(1,len(widgets[wk]["source"].data["y"])+1),widgets[wk]["source"].data["y"]))
                else:
                    data[mk]= dict(zip(range(1,len(widgets[wk]["source"].data["y"])+1),widgets[wk]["source"].data["y"]))

            data["tec_hs"] = list(data_heat_storages["name"].values)
            data["tec"] = list(data1["name"].values)

            data["all_heat_geneartors"] = data["tec"] + data["tec_hs"]

            data["energy_carrier"] = {**data["energy_carrier"],**carrier_dict}
            ##
            for i in _elec:
                mk = widget_to_model_keys_dict[i]
                ext=[]
                for j in data["tec"] :
                    jt = list(zip([j]*8760,range(1,8760+1)))
                    if j in list(external_data[i]):
                        ext.append(dict(zip(jt,external_data[i][j])))
                    else:
                        ext.append(dict(zip(jt,external_data[i]["Default"])))
                ext = {k: v for d in ext for k, v in d.items()}
                if  mk == "electricity":
                    data["energy_carrier_prices"][mk] = ext
                else:
                    data[mk] = ext
            ##
            data["categorize"] = {}
            _dataframe= pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore')
            select_tec_options = [x.replace("CHP Steam Extraction","CHP-SE").replace("CHP Back Pressure","CHP-BP") for x in select_tec_options_model]
            for j in select_tec_options:
                data["categorize"][j] = _dataframe["name"][_dataframe["type"] == j].values.tolist()

            solutions = None
            selection = [[],[]]
            inv_flag = False
            if invest_button.active:
                inv_flag = True
                selection0 = data_table.source.selected["1d"]["indices"]
                selection1 = data_table_heat_storage.source.selected["1d"]["indices"]
                selection = [selection0,selection1]
                if selection[0] == []:
                    div_spinner.text = """<div align="center"> <strong style="color: red;">Error: Please specify the technologies for the invesment model !!!</strong></div>"""
                    return
            solutions,_,_ = execute(data,inv_flag,selection)
            print('calculation done')
            print ("Ploting started..")
            if solutions == "Error1":
                div_spinner.text = """<div align="center"> <strong style="color: red;">Error: No Capacities are installed !!!</strong></div>"""
            elif solutions == "Error2":
                div_spinner.text = """<div align="center"> <strong style="color: red;">Error: The installed capacities are not enough to cover the load !!!</strong></div>"""
            elif solutions == "Error3":
                print("Error in Saving Solution to JSON !!!")
                print("Cause: Infeasible or unbounded model !!!")
                div_spinner.text = """<div align="center"><strong style="color: red;">Error: Infeasible or unbounded model !!!</strong></div>"""
            elif solutions == None:
                print("Error: Something get Wrong")
                div_spinner.text = """<div align="center"> <strong style="color: red;">Error: Something get Wrong</strong></div>"""
            else:
                output_tabs = plot_solutions(solution=solutions)

                if output_tabs == "Error4":
                    print("Error @ Ploting  !!!")
                    div_spinner.text = """<div align="center"> <strong style="color: red;">Error: @ Ploting !!!</strong></div>"""
                else:
                    output.tabs = output_tabs
                    print("Ploting done")
                    print("Download output_graphics started...")
                    time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                    filename = "output_graphs.html"
                    
                    path_download = os.path.join(create_folder(time_id),filename)
                    output_file(path_download,title="Dispatch output")
                    save(output)
                    path_download_html = os.path.join("download","static",time_id,filename)
#                    trigger_download(time_id,filename)
                    print("Graphics Download done")
                    print("Download output data started...")
                    # -- Download JSON
                    time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                    filename = "output_data.json"
                    path_download = os.path.join(create_folder(time_id),filename)
                    with open(path_download, "w") as f:
                        json.dump(solutions, f)
                    path_download_json = os.path.join("download","static",time_id,filename)
#                    trigger_download(time_id,filename)
                    print("Download output data done")
                    # --
                    div_spinner.text = """<div align="center"> 
                    <style>
                    a:link, a:visited {
                        background-color: white;
                        color: green;
                        border: 2px solid green;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                    }
                    
                    a:hover, a:active {
                        background-color: green;
                        color: white;
                    }
                    </style>
                    <strong style="color: green">
                    <p>Calculation done<p>
                    <p><a href="""+"'"+path_download_html+"'"""" download="output.html">Download HTML File </a> <p>
                    <p><a href="""+"'"+path_download_json+"'"""" download="output.json">Download JSON File </a>  <p>
                    </strong>
                    </div>
                    """
        except Exception as e:
            print(str(e))
            print(e)
            print(type(e))
            div_spinner.text = """<div align="center"><strong style="color: red;">Fatal Error @ Running </strong></div>"""
# =============================================================================
    def upload_callback(attr, old, new):
        try:
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
                data2 = excel_object.parse(sheet_name = sheets[0], index_col = 0,skiprows = range(22,50)).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                data2["index"] = data2.index
                data_table.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = sheets[1], index_col = 0,skiprows = range(14,50)).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                data_table_prices.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = 'Data', index_col = 0).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                r = data2.shape[0]
                data2 = excel_object.parse(sheet_name = 'Data', index_col = 0,skiprows = range(2,r+1)).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                data_table_data.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = sheets[3], index_col = 0).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                data_table_heat_storage.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = 'Energy Carrier', index_col = 0)
                global carrier_dict
                data2 = data2.set_index(data2["name"])
                del data2["name"]
                carrier_dict = data2.to_dict()["carrier"]
                div_spinner.text = """<div align="center"><strong style="color: green;">Upload done</strong></div>"""
            else:
                print("Not a valid file to upload")
                div_spinner.text = """<div align="center"><strong style="color: red;">Not a valid file to uploade</strong></div>"""
            print('Upload done')

        except Exception as e:
            print(str(e))
            div_spinner.text = """<div align="center"><strong style="color: red;">Fatal Error @ Update </strong></div>"""
# =============================================================================
    def args_callback(attrname, old, new):


        _heat_generators= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        _heat_generators = _heat_generators.fillna(0)
        _opt = list(_heat_generators["name"].values)

        # update energy carrier mapping if name of heat producer was changed
        new_key = [j for j in _opt if j not in list(carrier_dict)]
        if len(new_key):
            new_key = new_key[0]
        old_key = [j for j in [j for j in list(carrier_dict) if j not in _opt] if j !="Default"]
        if len(old_key):
            old_key = old_key[0]
        if new_key and old_key:
            carrier_dict[new_key] = carrier_dict.pop(old_key)
        #

        _options = ["Default"] + _opt

        for i in data_kwargs:
            widgets[i]["tec"].options = _options
            c,year = widgets[i]["select"].value.split("_")
            y = data_kwargs[i]["data"][data_kwargs[i]["dic_inv"][c],int(year)]
            y_profil,s = profil(y)

            if i != _hd:
                widgets[i]["total"].value = str(round(s,2))
            else:
                widgets[_hd]["total"].value = str(data_table_data.source.data[parameter_list[3]][0])

            if widgets[i]["mean"].active != []:
                widgets[i]["source"].data["y"] = [np.mean(y)]*8760
            else:
                if widgets[i]["offset"].value =="":
                    widgets[i]["offset"].value = "0"
                if widgets[i]["constant"].value =="":
                    widgets[i]["constant"].value = "-"
                if widgets[i]["constant"].value == "-" :
                    y_new = y_profil * float(widgets[i]["total"].value) * widgets[i]["scale"].value + float(widgets[i]["offset"].value)
                    widgets[i]["source"].data["y"] = y_new.tolist()
                else:
                    y = np.array([float(widgets[i]["constant"].value)]*8760) + float(widgets[i]["offset"].value)
                    y_new = y * widgets[i]["scale"].value
                    widgets[i]["source"].data["y"] = y_new.tolist()

# =============================================================================
    def create_folder(time_id):
        """ This function creates a folder in the static directory and returns its path"""
        path_download_dir = os.path.join(path_static,time_id)
        if not os.path.exists(path_download_dir):
            os.makedirs(path_download_dir)
        return path_download_dir
# =============================================================================
    def trigger_download(time_id,filename):
        """ This function triggers the download of the file specified in the static folder """
        id_source.data = dict(id=[time_id],filename=[filename])
        if int(dummy.text[32] ) == 0:
            dummy.text= dummy.text.replace("0","1")
        else:
            dummy.text= dummy.text.replace("1","0")
# =============================================================================
    def reset_callback():
        div_spinner.text = load_text
        output.tabs = []
        div_spinner.text = ""
        grid.children = [Div()]
# =============================================================================
    def update_pmax(attrname, old, new):
        pmax.value = str(round(max(widgets[_hd]["source"].data["y"]),2))
        _data1= pd.DataFrame(data_table.source.data)[input_list[1]].apply(pd.to_numeric, errors='ignore')
        _data1 = _data1.fillna(0)
        x = float(pmax.value) - sum(_data1)
        if x>=0 :
            to_install.value = str(round(x,2))
        else:
            to_install.value = "0"
# =============================================================================
    def load_callback2(attrname, old, new):
        data_table_data.source.data[parameter_list[3]] = [new]
# =============================================================================
    def ivest_callback(active):
        if active:
            div_spinner.text = """<div align="center"><strong style="color: red;">Mark Technologies by pressing "CTRL" +  "left mouse", Rows are marked yellow </strong></div>"""
        else:
            div_spinner.text = ""
# =============================================================================
    def add_external_data_to_heat_producers():
        for i in data_kwargs:
            if widgets[i]["ok"].clicks > 0 :
                external_data[i][widgets[i]["tec"].value]= widgets[i]["source"].data["y"]
                if widgets[i]["tec"].value == "Default":
                    div_spinner.text = """<div align="center"><strong style="color: green;"> """+i+""" Data is set as """+widgets[i]["tec"].value+"""</strong></div>"""
                else:
                    div_spinner.text = """<div align="center"><strong style="color: green;"> """+i+""" Data For """+widgets[i]["tec"].value+""" is added </strong></div>"""
                widgets[i]["ok"].clicks = 0 # this calls again this function

# =============================================================================
#   Signal Emitting / Coupling of Main GUI
# =============================================================================
    for i in data_kwargs:
        widgets[i]["select"].on_change('value', args_callback)
        widgets[i]["offset"].on_change("value", args_callback)
        widgets[i]["constant"].on_change("value", args_callback)
        widgets[i]["scale"].on_change('value', args_callback)
        widgets[i]["mean"].on_change('active', args_callback)
        widgets[i]["ok"].on_click( add_external_data_to_heat_producers)
        widgets[i]["ok"].clicks = 1 # Initi Default Values
    div_spinner.text = "" # Clear Info Screen for Default Values
    widgets[_hd]["total"].on_change("value",load_callback2)

    data_table_data.source.on_change("data",args_callback)
    data_table.source.on_change("data",args_callback)
    data_table_heat_storage.source.on_change("data",args_callback)

    widgets[_hd]["source"].on_change("data",update_pmax)

    invest_button.on_click(ivest_callback)

    id_source = ColumnDataSource(data=dict())
    download_callback_js = CustomJS(args=dict(source=id_source), code=download_code)
    dummy.js_on_change('text', download_callback_js)

    download_button.on_click(download_callback)

    file_source = ColumnDataSource({'file_contents':[], 'file_name':[]})
    file_source.on_change('data', upload_callback)
    upload_button.callback = CustomJS(args=dict(file_source=file_source), code =upload_code)

    run_button.on_click(run_callback)

    reset_button.on_click(reset_callback)
# =============================================================================
#   Initilizing GUI with Default Values
# =============================================================================
    # Pmax Initilizing
    update_pmax(None,None,None)
    # Total Demand initilize with input
    args_callback(None,None,None)
#%%
# =============================================================================
#  GUI Elements for adding Technologies
# =============================================================================
    grid = column(children=[Div()],height=300)
    ok_button = Button(label='✓ ADD', button_type='success',width=60)
    cancel_button = Button(label='	🞮 CANCEL', button_type='danger',width=60)
    select_tec = Select(title="Add Heat Generator:", options = select_tec_options )
    select_tec2 = Select()

    tabs_geneator = Tabs(tabs=[] ,width = 800)
    tec_buttons = widgetbox(children = [select_tec])

    children = [tec_buttons,widgetbox(tabs_geneator),row(children = [ok_button,cancel_button])]

    cop_label = TextInput(placeholder="COP", title="COP",disabled= True)
    flow_temp = Select(title="Flow Temperature")
    return_temp = Select(title="Return Temperature")

    energy_carrier_select = Select(options = energy_carrier_options, title="Energy Carrier",value = energy_carrier_options[0])

    n_th_label = TextInput(placeholder="-", title="Thermal Efficiency")
    n_el_label = TextInput(placeholder="-", title="Electrical Efficiency")

    opex_fix_label = TextInput(placeholder="-", title="OPEX fix (EUR/MWa)'")
    opex_var_label = TextInput(placeholder="-", title="OPEX var (EUR/MWh)")

    lt_label = TextInput(placeholder="-", title="life time (a)")
    ik_label = TextInput(placeholder="-", title="investment costs (EUR/MW_th")

    must_run_box = Toggle(label="Must Run",  button_type="warning")
    renewable_factor = Slider(start=0, end=1, value=0, step=.1, title="Renewable Factor")
    installed_cap = Slider(start=0, end=int(float(pmax.value))+1, value=0, step=1, title="Installed Capacity")

    name_label = TextInput(placeholder="-", title="Name",disabled=False)

    widgets_list= [
            [select_tec,select_tec2], installed_cap, n_th_label, n_el_label,
            ik_label, opex_fix_label, opex_var_label,lt_label,
            renewable_factor, must_run_box
            ]

    widgets_dict = dict(zip(input_list,widgets_list))

# =============================================================================
#  Widget Layout for adding Technologies
# =============================================================================
    cop_layout= column([row([return_temp,flow_temp]),cop_label])
    tec_param_layout = column(children=[row(children=[energy_carrier_select,name_label]),
                                            row(children=[n_th_label,
                                                          n_el_label])])
    finance_param_layout = column(children=[row(children=[ik_label,lt_label]),
                                            row(children=[opex_fix_label,
                                                          opex_var_label])])
    model_param_layout = widgetbox(must_run_box,renewable_factor,installed_cap)

    cop_panel = Panel(child=cop_layout, title="Coefficient of Performance, COP")
    tec_param_panel = Panel(child=tec_param_layout, title="Technical Parameters")
    finance_param_panel = Panel(child=finance_param_layout, title="Finance Parameters")
    model_param_panel = Panel(child=model_param_layout, title="Model Parameters")
    layout1 = [ cop_panel , tec_param_panel, finance_param_panel , model_param_panel]
    layout2 = [tec_param_panel, finance_param_panel , model_param_panel]
# =============================================================================
#  Callbacks for adding Technologies
# =============================================================================
    def add_heat_generator():
        output.tabs = []
        div_spinner.text = load_text
        grid.children = children
        select_tec.value = select_tec.options[0]
        div_spinner.text = ""
        installed_cap.end=int(float(pmax.value))+1
# =============================================================================
    def cancel():
        div_spinner.text = load_text
        grid.children = [Div()]
        div_spinner.text = ""
# =============================================================================
    def add_to_cds():
        global carrier_dict
        # if user refreshes site, create new dict
        _df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        if _df.shape[0] == 0:
            carrier_dict={}
        div_spinner.text = load_text
        df2 = pd.DataFrame(data_table.source.data)
        df2.set_index(df2["index"])
        del df2["index"]
        new_data={}
        for x in input_list:
            if x == "name":
                try:
                    new_data[x] = new_name(str(name_label.value),data_table.source.data["name"].tolist())
                    carrier_dict[new_name(str(name_label.value),data_table.source.data["name"].tolist())] = energy_carrier_select.value
                except:
                    new_data[x] = new_name(str(name_label.value),data_table.source.data["name"])
                    carrier_dict[new_name(str(name_label.value),data_table.source.data["name"])] = energy_carrier_select.value
            elif  x == 'must run [0-1]':
                new_data[x] = str(int(widgets_dict[x].active))
            else:
                new_data[x] = str(widgets_dict[x].value)
        new_data["type"] = select_tec_mapper[select_tec.value]
        df2 = df2.append(new_data,ignore_index=True)
        df2 = df2.apply(pd.to_numeric, errors='ignore')
        df2["index"] = df2.index
        data_table.source.data.update(df2)
        del df2
#        grid.children = [Div()]
        div_spinner.text = """<div align="center"> <strong style="color: green;">Heat Generator ADDED</strong> </div>"""
# =============================================================================
    def add_heat_pump():

        flow_temp.options = flow_temp_dic[tec_mapper_inv[select_tec2.value]]
        flow_temp.value = flow_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback, thus need of try block
        return_temp.options = return_temp_dic[tec_mapper_inv[select_tec2.value]]
        return_temp.value = return_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback,
        cop_label.value = str(heat_pumps[tec_mapper_inv[select_tec2.value]].loc[return_temp.value,flow_temp.value])
        n_th_label.value = cop_label.value
        n_th_label.disabled = True
        tabs_geneator.tabs = layout1
# =============================================================================
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

        if select_tec.value in ["heat pump","CHP Back Pressure", "CHP Steam Extraction", "boiler"]:
            select_tec2.title= "Select a "+str(select_tec.value)+":"
            select_tec2.options = select_tec2_options[select_tec.value]
            tec_buttons.children = [select_tec,select_tec2]
            select_tec2.value = select_tec2.options[0]
        else:
            tec_buttons.children = [select_tec]
            tabs_geneator.tabs = layout2

        div_spinner.text = ""
# =============================================================================
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
            tabs_geneator.tabs = layout2
# =============================================================================
    def update_slider(name,old,new):
        try:
            installed_cap.end=int(float(pmax.value))+1
        except:
            pass
# =============================================================================
    def cop_callback(name,old,new):
        try: # because of empty fields at the start no COP can be found
            cop_label.value = str(heat_pumps[tec_mapper_inv[select_tec2.value]].loc[return_temp.value,flow_temp.value])
            n_th_label.value = cop_label.value
            n_th_label.disabled = True
        except:
            pass
# =============================================================================
    def change_name_if_carrier_changes(name,old,new):
        name_label.value = name_label.value.replace(old,new)
# =============================================================================
#   Signal Emitting / Coupling for adding Technologies
# =============================================================================
    button1.on_click(add_heat_generator)
    cancel_button.on_click(cancel)
    ok_button.on_click(add_to_cds)
    select_tec.on_change('value', add_tec)
    select_tec2.on_change('value', auto_load)
    pmax.on_change("value",update_slider)
    flow_temp.on_change('value', cop_callback)
    return_temp.on_change('value', cop_callback)
    energy_carrier_select.on_change('value', change_name_if_carrier_changes)
# =============================================================================
#   Set Global Layout
# =============================================================================
    from imageHTML import header_html
    header = widgetbox(Div(text= header_html))
    
#    l = column([header,
#                row([
#                        widgetbox(download_button,upload_button,run_button,
#                                  reset_button,invest_button),
#                          widgetbox(div_spinner),
#                          widgetbox(Div()),
#                          widgetbox(pmax,Div(),to_install)]),
#                 widgetbox(Div(height=25)),
#                 grid,
#                 widgetbox(dummy),
#                 column([widgetbox(output)]),
#                 widgetbox(tabs),
#                 ],
#            sizing_mode='scale_width')  #XXX: scale_width -> invest_button not clickable

    l = layout([[header],
                    [row(children=[
                            column(children=[download_button,upload_button,run_button,
                               reset_button,invest_button]),
                     widgetbox(div_spinner,width=1000),column([pmax,to_install])])],
                   [grid],
                   [widgetbox(dummy)],
                   [widgetbox(output,width=1500)],
                   [widgetbox(tabs,width=1500)],
            ],sizing_mode='scale_width')

    doc.add_root(l)
    
    return doc
#%%
if __name__ == '__main__':
#    from bokeh.server.views.static_handler import StaticHandler
    io_loop = IOLoop.current()
    allow_websocket_origin=None
    f_allow_websocket_origin = os.path.join(root_dir, 'allow_websocket_origin.txt')
    if os.path.exists(f_allow_websocket_origin):
        with open(f_allow_websocket_origin) as fd:
            allow_websocket_origin = [line.strip() for line in fd.readlines()]

    bokeh_app = Application(FunctionHandler(modify_doc))
    bokeh_app_2 = Application(DirectoryHandler(filename = path2data))

    server = Server({'/': bokeh_app, '/download':bokeh_app_2}, io_loop=io_loop, 
                    allow_websocket_origin=allow_websocket_origin)#,
#                    extra_patterns=[('/static/.*', StaticHandler,dict(path=path_static))])
    server.start()
    print('Opening Dispath Application on http://localhost:5006/')
    
    try:
        io_loop.start()
    except:
        pass
