# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 15:30:16 2018

@author: root
"""
#%% Check if modules are installed

import bokeh,tornado,xlsxwriter, openpyxl, pyomo.environ, matplotlib, xlrd, numpy, pandas, sys,subprocess

assert not subprocess.call("node -v"), "Please install nodejs (type: <conda install -c bokeh nodejs>)"
#XXX: Downgrade back bokeh version "0.12.10"
assert bokeh.__version__ == '0.12.10', f"Your current bokeh version ist not compatible (Your Version:{bokeh.__version__})\nPlease install version 0.12.10 (type < pip install bokeh==0.12.10 >)"
#XXX: Downgrade to torndado 4.5.3
assert tornado.version == '4.5.3',f"Your current tornado version ist not compatible (Your Version:{tornado.version})\nPlease install version 4.5.3 (type < pip install tornado==4.5.3 >)"

assert pyomo.environ.SolverFactory("gurobi").available(), "No Gurobi Solver Found, Please check your System Path Variable or purchase the GUROBI Solver"

#%% import modules
matplotlib.use('agg',warn=False)
from tornado.ioloop import IOLoop
import pandas as pd
import numpy as np
from zipfile import ZipFile
from bokeh.application.handlers import FunctionHandler,DirectoryHandler
from bokeh.application import Application
from bokeh.layouts import widgetbox,row,column,layout
from bokeh.models import ColumnDataSource,TableColumn,DataTable,CustomJS,TextInput, Slider,NumberFormatter
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs, Button,Div,Toggle,Select,CheckboxGroup
import os,io,base64,pickle,datetime,json#,shutil
from bokeh.plotting import figure,output_file,save
from bokeh.models import PanTool,WheelZoomTool,BoxZoomTool,ResetTool,SaveTool,HoverTool
from functools import partial
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
root_dir = os.path.dirname(os.path.abspath(__file__))

if path not in sys.path:
    sys.path.append(path)
#%%  for bokeh 0.12.10 extent functionality for setting the active tab  and  Implement disabled
#XXX: for bokeh 0.12.10
# =============================================================================
# extent functionality for setting the active tab  and  Implement disabled
# because Zooming performance regression with higher versions of bokeh
# see CHANGELOG (https://github.com/bokeh/bokeh/blob/master/CHANGELOG): #1376 , #6502, #7255  
# Implement #1376 , #6502
# use idea of Zyell : https://github.com/bokeh/bokeh/issues/6502
# =============================================================================
JS_CODE = """
import * as p from "core/properties"
import {Tabs, TabsView} from "models/widgets/tabs"
export class CustomTabsView extends TabsView
    connect_signals: () ->
        super()
        @connect(@model.properties.active.change, () => @render())
export class CustomTabs extends Tabs
  type: "Tabs"
  default_view: CustomTabsView

"""
# =============================================================================
class CustomTabs(Tabs):
    __implementation__ = JS_CODE
# =============================================================================
JS_CODE = """
import {empty, label, select, option, optgroup} from "core/dom"
import {isString, isArray} from "core/util/types"
import {logger} from "core/logging"
import * as p from "core/properties"
import {InputWidget, InputWidgetView} from "models/widgets/input_widget"
import {Select, SelectView} from "models/widgets/selectbox"
export class CustomSelectView extends SelectView
  initialize: (options) ->
    super(options)
    @render()
  connect_signals: () ->
    super()
    @connect(@model.change, () -> @render())
  build_options: (values) ->
     return values.map (el) =>
      if isString(el)
        value = _label  = el
      else
        [value, _label] = el
      selected = @model.value == value
      return option({selected: selected, value: value}, _label)
  render: () ->
    super()
    empty(@el)
    labelEl = label({for: @model.id}, @model.title)
    @el.appendChild(labelEl)
    if isArray(@model.options)
     contents = @build_options( @model.options )
    else
     contents = []
     for key,value of @model.options
      contents.push optgroup({label: key}, @build_options( value ))
    @selectEl = select({
      class: "bk-widget-form-input",
      id: @model.id,
      name: @model.name
      disabled: @model.disabled}, contents)
    @selectEl.addEventListener("change", () => @change_input())
    @el.appendChild(@selectEl)
    return @
  change_input: () ->
    value = @selectEl.value
    logger.debug("selectbox: value = #{value}")
    @model.value = value
    super()
export class CustomSelect extends Select
  type: "Select"
  default_view: CustomSelectView

"""
# =============================================================================
class CustomSelect(Select):
    __implementation__ = JS_CODE
# =============================================================================
Tabs = CustomTabs
Select = CustomSelect
# =============================================================================

#%% Import internal modules
from AD.F16_input.main import extract,find_FiT
from CM.CM_TUWdispatch.plot_bokeh import plot_solutions
import CM.CM_TUWdispatch.run_cm as dispatch
from CM.CM_TUWdispatch.save_sol_to_json import json2xlsx

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
path_snackbar_html = os.path.join(root_dir, "snackbar.html")
#%% RUN MODEL
# =============================================================================
# RUN MODEL
# =============================================================================
def execute(data,inv_flag,selection=[[],[]],demand_f=1):
    val = dispatch.main(data,inv_flag,selection,demand_f)
    return val
#%% Global Functions
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
    fig = figure(tools=TOOLS,min_border_left = 55 , min_border_bottom = 55,
                 x_axis_label='Time in hours',)
    fig.line('x', 'y', source=source, line_alpha=0.6)
    fig.toolbar.logo = None

    return select,source,fig
# ===========================================================================
def generate_tables(columns,name="",):
    if name == "":
        data = pd.read_excel(path_parameter,skiprows=[0])[columns]
        data["type"] = data.index
    else:
        data = pd.read_excel(path_parameter,name,skiprows=[0])[columns]
    if name in ["","Heat Storage"]:
        data = data.drop(data.index)


    col = [TableColumn(field=name, title=name) for name in columns]
    source = ColumnDataSource(data)
    #,width=1550,height=700
    table = DataTable(source=source,columns=col,width=1550,
                           editable=True,height=250)
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
            Select(title=kwargs.setdefault("tec","Add to"), value="Default", options=[]),
            Button(label='✓', button_type='success',width=60)
            ]
    return args
# ===========================================================================
def generate_widgets(data):
    select,source,figure = genearte_selection(data["data"],data["dic"])
    figure.yaxis.axis_label = data["unit"]
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
def disable_widgets(widget_list,flag):
    for w in widget_list:
        try: 
            w.disabled = flag
        except:
            continue
# =============================================================================
def scenario_tools():    
    sc_select = Select(title="Scenario", value="default", options=["default"], disabled=True)
    sc_text = TextInput(value="", placeholder="default scenario", title="Scenario Name", disabled=True)
    sc_add = Button(label='add',  button_type="success", width=50, disabled=True)
    sc_del= Button(label="del", button_type="danger", width=50, disabled=True)
    sc_apply = Button(label='apply', button_type='primary', width=50, disabled=True)
    
    sub_sc_select = Select(title="Sub Scenario", value="default_sub", options=["default_sub"], disabled=True)
    sub_sc_text = TextInput(value="", placeholder="default sub scenario", title="Sub Scenario Name", disabled=True)   
    sub_sc_del= Button(label="del", button_type="danger", width=50, disabled=True)
    sub_sc_add = Button(label='add',  button_type="success", width=50, disabled=True)
    sub_sc_apply = Button(label='apply', button_type='primary', width=50, disabled=True)
    
    tools = dict(sc_select = sc_select, sc_text = sc_text, sc_add = sc_add,
                 sc_del = sc_del, sc_apply = sc_apply,
                 sub_sc_select = sub_sc_select, sub_sc_text = sub_sc_text,
                 sub_sc_del = sub_sc_del, sub_sc_add = sub_sc_add, 
                 sub_sc_apply = sub_sc_apply)
    
    layout = column(children=[row(  column(sc_select, sc_text, 
                                         row([sc_add, sc_del, sc_apply])), 
                                    column(sub_sc_select, sub_sc_text,
                                           row([sub_sc_add, sub_sc_del, sub_sc_apply]))
                                    )
                              ],width=200,css_classes=["scenario_tools"])
    
    return dict(tools=tools,layout=layout)
# =============================================================================
def sub_scenario_tools():
    sc_select = Select(title="Scenario", value="default", options=["default"], disabled=True)    
    sub_sc_select = Select(title="Sub Scenario", value="default_sub", options=["default_sub"], disabled=True)
    sub_sc_text = TextInput(value="", placeholder="default sub scenario", title="Sub Scenario Name", disabled=True)
    sub_sc_del= Button(label="del", button_type="danger", width=50, disabled=True)
    sub_sc_add = Button(label='add',  button_type="success", width=50, disabled=True)
    sub_sc_apply = Button(label='apply', button_type='primary', width=50, disabled=True)

    tools = dict(sc_select = sc_select, sub_sc_select = sub_sc_select,
                 sub_sc_text = sub_sc_text, sub_sc_del = sub_sc_del,
                 sub_sc_add = sub_sc_add, sub_sc_apply = sub_sc_apply)
    
    layout = column(children=[sc_select, sub_sc_select, sub_sc_text, 
                          row([sub_sc_add, sub_sc_del, sub_sc_apply ])
                          ],width=200,height=270,css_classes=["sub_scenario_tools"])
    
    return dict(tools=tools,layout=layout)
# =============================================================================
def pop_sc(table):
    for sc in list(table):
        if sc != "default":
            table.pop(sc, None)
# =============================================================================            
def pop_sub_sc(table):
    for sc in list(table):
        if sc != "default":
            table.pop(sc, None)
        else:
            for sub_sc in list(table[sc]):
                if sub_sc != "default_sub":
                    table[sc].pop(sub_sc, None)          
# =============================================================================
def df2data (df):
    return {key:list(dic.values()) for key,dic in df.to_dict().items()}
# =============================================================================     
def pop_table(table):
    for sc in list(table):
        table.pop(sc, None)
# ============================================================================= 
with open(path_snackbar_html) as file:
    snackbar=file.read()
    
def notify(text1,color1,text2=False,color2=False,snackbar=snackbar):
    text2 = text2 if text2 else text1
    color2 = color2 if color2 else color1
    html_code = snackbar.replace("###color1",color1).replace("###color2",color2).replace("###text1",text1).replace("###text2",text2)
    return html_code        
#%% Global Data
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

input_price_list = ["energy carrier","prices(EUR/MWh)","emission factor [tCO2/MWh]"]

parameter_list = ['CO2 Price [EUR/tC02]',
 'Interest Rate [0-1]',
 'Minimum Renewable Factor [0-1]',
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
select_hs_options = pd.read_excel(path_parameter,sheets[3],skiprows=[0])["name"].values.tolist()

#%%  BOKEH MAIN: Function Handler
# =============================================================================
# Function Handler
# =============================================================================
def modify_doc(doc):
#%% Main Functionality:  Widgets, callbacks, layouts etc.
    # Load External Data from .dat files
    price_name_map,price_name_map_inv,prices = load_extern_data("price")
    load_name_map,load_name_map_inv,load_profiles = load_extern_data("load")
    radiation_name_map, radiation_name_map_inv,radiation = load_extern_data("radiation")
    temperature_name_map, temperature_name_map_inv, temperature = load_extern_data("temperature")
    # Database for the external data manipulation,
    widgets_data = [ dict(data=radiation,
                          dic=radiation_name_map,
                          dic_inv = invert_dict(radiation_name_map),
                          labels=lab,
                          unit="W/m²"),
                    dict(data=temperature,
                          dic=temperature_name_map,
                          dic_inv = invert_dict(temperature_name_map),
                          labels=lab,
                          unit="°C"),
                    dict(data=prices,
                          dic=price_name_map,
                          dic_inv = invert_dict(price_name_map),
                          labels=dict(),
                          unit="€/MWh"),
                    dict(data=prices,
                          dic=price_name_map,
                          dic_inv = invert_dict(price_name_map),
                          labels=dict(),
                          unit="€/MWh"),
                    dict(data=load_profiles,
                          dic=load_name_map,
                          dic_inv = invert_dict(load_name_map),
                          labels=lab,
                          unit="MW"),
                    ]
    # Create Data structure for better code handling
    widget_to_model_keys_dict = dict(zip(widgets_keys,model_keys))
    data_kwargs = dict(zip(widgets_keys,widgets_data))
    #external_data = dict(zip(widgets_keys,[{}]*len(widgets_keys))) #XXX only copy
    carrier_dict = {}
    _nth = dict()
    external_data = dict(zip(widgets_keys,[{} for _ in range(len(widgets_keys))]))
    external_data_map = dict(zip(widgets_keys,[{} for _ in range(len(widgets_keys))]))

    add_to_tec = Select(title="Add To Heatgenerator", value="", 
                            options=[],disabled=True)
# =============================================================================
#   MAIN GUI Elements
# =============================================================================
    data_table = generate_tables(input_list)
    data_table_prices = generate_tables(input_price_list,sheets[1])
    data_table_data = generate_tables(parameter_list,sheets[2])
    data_table_heat_storage = generate_tables(list(heat_storage_list_mapper),sheets[3])
    widgets= { i : generate_widgets(data_kwargs[i]) for i in data_kwargs}
    dummy = Div(text="""<strong style=" display: none;">1</strong>""")
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
    button1= Button(label='🞧',  button_type="success", width=50)
    button1_1= Button(label="x",button_type="danger",width=30)
    label2 = Div(text="""<h1 style=" font-size: 20px; text-align: center; text-transform: uppercase; ">Heat Storages </h1>  """, width=180, height=10)
    button2= Button(label='🞧',  button_type="success", width=50)
    button2_1= Button(label="x",button_type="danger",width=30)    
# =============================================================================
#   Layout for Main GUI
# =============================================================================
    col_hp_hs = column([row(label1,button1,button1_1),data_table,row(label2,button2,button2_1),data_table_heat_storage])
    lay = { i : generate_layout(widgets[i]) for i in data_kwargs}
    # Change layout of Heat Demand Tab -> Add Total Demand
    widgets[_hd]["total"].title = "Set Total Demand (MWh)"
    widgets[_hd]["total"].disabled=False
    lay[_hd].children[1].children = [widgetbox(widgets[_hd]["total"])]
    # Change layout of Electricity Tabs -> Select technologies to add external data
    for i in _elec:
        lay[i].children.append(column(widgetbox(widgets[i]["tec"]), widgetbox(widgets[i]["ok"])))
#    lay = {name: column(scenario_dict[name]["layout"],layout) for name,layout in lay.items()}
    grid = Tabs(tabs=[],css_classes=["adding_hg_hs"])
    div2 = Div(text=""" <style>
              .adding_hg_hs {
                      display: none;
                      } """)
    profiles_tabs = Tabs(tabs=[Panel(child=p, title=name) for name, p in lay.items()])
    tabs_dic = {"Heat Producers and Heat Storage":col_hp_hs,
           "Parameters":data_table_data,
           "Prices & Emission factors":data_table_prices,
           "Profiles": profiles_tabs,}
    tabs_liste = [Panel(child=p, title=name) for name, p in tabs_dic.items()]
    tabs = Tabs(tabs=tabs_liste)
# =============================================================================
#   Callbacks for Main GUI
# ============================================================================= 
    def download_callback():
        try:
            div_spinner.text = load_text
            print("Download...")
            time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
            if scenario_button.active:
                _hgs = [f"{sc}-{sub_sc}"  for sc in list(scenario_mapper) for sub_sc in scenario_mapper[sc]  if heat_generator_table[sc][sub_sc].empty]
                if _hgs != []:
                    div_spinner.text = notify(f"Nothing to download for {_hgs}","red") 
                    return
                filename = "scenario_inputs.zip"
                path_download = create_folder(time_id)
                print("Downloading Scenarios...")
                try:
                    for sc in list(scenario_mapper):
                        _path = os.path.join(path_download,sc)
                        if not os.path.exists(_path):
                            os.makedirs(_path)
                        for sub_sc in scenario_mapper[sc]:
                             _path = os.path.join(path_download,sc,f"{sub_sc}.xlsx")
                             ok = get_input_data(sc,sub_sc,_path)
                             if not ok:
                                 div_spinner.text = notify(f"Error @ Downloading Data for {sc}-{sub_sc} ","red") 
                                 return
                    ok,message = zip_all_scenarios(path_download,filename,downlad_flag=True)
                    if ok:
                        print("Download done.\nSaved to <"+path_download+">")
                        trigger_download(time_id,filename)
                        div_spinner.text = notify("Download done","green")
                    else:
                        text = f"Error @ Downloading : {message}"
                        div_spinner.text = notify(text,"red")                
                except Exception as e:
                    print(str(e))
                    div_spinner.text = notify("Fatal Error @ Downloading in Scenario Mode","red")                    

            else:
                df= pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore')
                if df.shape[0] == 0:
                    del df
                    for k in list(carrier_dict):
                        carrier_dict.pop(k,None)
                    div_spinner.text = notify("Nothing to download","red") 
                    return
        #        df = df.fillna(0)
                filename = "download_input.xlsx"
                path_download = os.path.join(create_folder(time_id),filename)
                writer = pd.ExcelWriter(path_download)           
                df = df.set_index(df.name)
                data = pd.DataFrame(external_data_map).drop("Default")[_elec]
                df = df.join(data)
                df = df.reset_index(drop=True)
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
                
                df_default_external_data = pd.DataFrame(external_data_map).loc["Default"].to_frame().T.reset_index(drop= True)
                df_default_external_data.to_excel(writer,"Default - External Data")
                
                writer.save()
                trigger_download(time_id,filename)
                print("Download done.\nSaved to <"+path_download+">")
        #TODO wait untill download has finished and delete folder
        #       or extra script that delete te content of the static folder after 2 hours or something else
        #        shutil.rmtree(path_download_dir, ignore_errors=True)
                div_spinner.text = notify("Download done","green") 
        except Exception as e:
            print(str(e))
            div_spinner.text = notify("Fatal Error @ Download","red")
# =============================================================================

    def check_scenarios(scenario_mapper):
        no_hg  = [(sc,sub_sc)  for sc in list(scenario_mapper) for sub_sc in scenario_mapper[sc]  if heat_generator_table[sc][sub_sc].empty]
        no_cap = [(sc,sub_sc)  for sc in list(scenario_mapper) for sub_sc in scenario_mapper[sc] if (max(profiles_table[_hd][sc][sub_sc].values()) - sum(heat_generator_table[sc][sub_sc][input_list[1]])) > 0]
        if no_hg != []:
            sc,sub_sc = zip(*no_cap)
            return f"""No Heat Generators available for for the scenarios {sc} in sub scenarios {sub_sc}"""
        elif no_cap != []:
            sc,sub_sc = zip(*no_cap)
            return f"""The installed capacities are not enough to cover the load for the scenarios {sc} in sub scenarios {sub_sc} """
        else: 
            return  True
        
    def scenario_calculation(sc,sub_sc):
        data = {}
        data["energy_carrier_prices"] = {}
        data["energy_carrier"] = {}
        data["threshold_heatpump"] = 0
        data1 = heat_generator_table[sc][sub_sc]
        data_prices = price_emmission_factor_table[sc][sub_sc]
        data_data = paramters_table[sc][sub_sc]
        data_heat_storages = heat_storage_table[sc][sub_sc]
        
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
               data["energy_carrier_prices"][mk]=  profiles_table[wk][sc][sub_sc]
            else:
                data[mk]= profiles_table[wk][sc][sub_sc]
        data["tec_hs"] = list(data_heat_storages["name"].values)
        data["tec"] = list(data1["name"].values)

        data["all_heat_geneartors"] = data["tec"] + data["tec_hs"]

        data["energy_carrier"] = {**data["energy_carrier"],**carrier_table[sc][sub_sc]}
       ##
        for i in _elec:
            mk = widget_to_model_keys_dict[i]
            ext=[]
            for j in data["tec"] :
                jt = list(zip([j]*8760,range(1,8760+1)))
                if j in list(external_data_table[sc][sub_sc][i]):
                    ext.append(dict(zip(jt,external_data_table[sc][sub_sc][i][j])))
                else:
                    ext.append(dict(zip(jt,external_data_table[sc][sub_sc][i]["Default"])))
            ext = {k: v for d in ext for k, v in d.items()}
            if  mk == "electricity":
                data["energy_carrier_prices"][mk] = ext
            else:
                data[mk] = ext
        ## Categorize
        data["categorize"] = {}
        _dataframe= heat_generator_table[sc][sub_sc][input_list+["type"]].apply(pd.to_numeric, errors='ignore')
        for j in select_tec_options_model:
            data["categorize"][j] = _dataframe["name"][_dataframe["type"] == j].values.tolist()
        ## thermal efficiencc
        _n_th = {}
        data["n_th"] = {**data["n_th"],**_nth_table[sc][sub_sc]}
        for k,v in data["n_th"].items():
            if type(v)==list:
                _n_th = {**_n_th,**dict(zip(zip([k]*8760,range(1,8760+1)),v))}
            else:
                _n_th = {**_n_th,**dict(zip(zip([k]*8760,range(1,8760+1)),[v]*8760))}
        data["n_th"] = _n_th
#        for k in list(_nth):
#            _nth.pop(k,None)
        ## 
        solutions,_message,_ = execute(data,False,[[],[]])
        ok = False
        output_data = None
        if solutions == "Error1":
            message = "Error: No Capacities are installed !!!"
        elif solutions == "Error2":
            message = "Error: The installed capacities are not enough to cover the load !!!"
        elif solutions == "Error3#":
            message = "Error in Saving Solution to JSON !!!"     
        elif solutions == "Error3":
            message = "Error: Infeasible or unbounded model !!! !!!" 
        elif solutions == None:
            message = "Error: "+_message
        else:
            ok = True
            message = _message
            output_data = solutions
        
        return ok,output_data,message
    
    def get_folder_structure(path,downlad_flag=False):
        """ Returns a path with the last 3 parts of <path>"""
        path,file = os.path.split(path)
        path,sub_sc = os.path.split(path)
        sc = os.path.split(path)[1]
        if downlad_flag:
            return os.path.join(sub_sc,file)
        else:
            return os.path.join(sc,sub_sc,file)
    
    def zip_all_scenarios(path_scenarios_root,filename = "output.zip",downlad_flag=False):
        try:
            print("Create Zip File for all scenarios...")
            path_download_zip = os.path.join(path_scenarios_root,filename)
            for root, dirs, files in os.walk(path_scenarios_root):
                for file in files:
                    with ZipFile(path_download_zip,"a") as zip_file:
                        file_path = os.path.join(root, file)
                        file_folder_structure = get_folder_structure(file_path,downlad_flag)
                        zip_file.write(file_path,file_folder_structure)
            print("Create Zip File done")       
            return True,os.path.join("download",get_folder_structure(path_download_zip,downlad_flag))
        except Exception as e:
            message = f"Error @ Ziping Scenario Output : {e}"
            print(message)
            return False,message
        
    def save_scenario(path_scenarios_root,sc,sub_sc,output_data):
        print(f"Ploting {sc}#{sub_sc}...")
        output_tabs = plot_solutions(solution=output_data)
        ok,message,path_download_zip = False,None,None
        if output_tabs == "Error4":
            message = "Error @ Ploting  in {sc}#{sub_sc}!!!"
        else:
            path_scenarios = os.path.join(path_scenarios_root,sc,sub_sc)
            if not os.path.exists(path_scenarios):
                os.makedirs(path_scenarios)
            ok = True
            output_sc = Tabs(tabs = output_tabs) 
            print("Ploting done")
            print("Download output_graphics started...")
            filename = f"output_{sc}_{sub_sc}.html"                    
            path_download_html = os.path.join(path_scenarios,filename)
            output_file(path_download_html,title=f"Dispatch output: {sc} # {sub_sc}")
            save(output_sc)
            print("Graphics Download done")
            print("Download output data started...")
            # -- Download JSON
            filename = f"output_{sc}_{sub_sc}.json"  
            path_download_json = os.path.join(path_scenarios,filename)
            with open(path_download_json, "w") as f:
                json.dump(output_data, f)
            # -- output XLSX
            filename = f"output_{sc}_{sub_sc}.xlsx"              
            path_download_xlsx = os.path.join(path_scenarios,filename)
            json2xlsx(output_data,path_download_xlsx) #XXX: change function with return values
            # -- input XLSX
            filename = f"input_{sc}_{sub_sc}.xlsx"              
            path_download_xlsx = os.path.join(path_scenarios,filename)
            ok = get_input_data(sc,sub_sc,path_download_xlsx)
            print("Download output data done")         
        return ok,message,path_download_zip
    
    def get_input_data(sc,sub_sc,path):
        print("Save Input as Excel File...")
        ok = True
        try:       
            writer = pd.ExcelWriter(path)
            df = heat_generator_table[sc][sub_sc]
            df = df.set_index(df.name)
            
            data = pd.DataFrame(external_data_map_table[sc][sub_sc]).drop("Default")[_elec]
            df = df.join(data)
            df = df.reset_index(drop=True)
            df.to_excel(writer,sheets[0])
            
            data_prices_df = price_emmission_factor_table[sc][sub_sc]
            data_prices_df.to_excel(writer,sheets[1])
            
            data_data_df = paramters_table[sc][sub_sc]
            data_data_df.to_excel(writer,"Data")
            
            data_hs_df = heat_storage_table[sc][sub_sc]
            data_hs_df.to_excel(writer,sheets[3])
            
            df_carrier = pd.DataFrame.from_dict(carrier_table[sc][sub_sc],orient="index")
            df_carrier["name"]=df_carrier.index
            df_carrier["carrier"] = df_carrier[0]
            del df_carrier[0]
            df_carrier.index = range(df_carrier.shape[0])
            df_carrier.to_excel(writer,'Energy Carrier')
            
            df_default_external_data = pd.DataFrame(external_data_map_table[sc][sub_sc]).loc["Default"].to_frame().T.reset_index(drop= True)           
            df_default_external_data.to_excel(writer,"Default - External Data")
            writer.save()
            print("Input saved !")
        except Exception as e :
            print(str(e))
            ok = False     
        return ok
        
    
    def compare_plot(dict_of_solutions):
        output_tabs = None
        return output_tabs
# =============================================================================
    def run_callback():
        try:
# =============================================================================            
            if scenario_button.active:
                div_spinner.text = spinner_text.replace("###text","Dispatch in progress, please be patient ...")
                time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")               
                path_scenarios = create_folder(time_id)
                
                print("Running Calculation in Scenario Mode...")
                print("Checking Scenarios...")
                text = check_scenarios(scenario_mapper)
                if type(text) == str:
                    div_spinner.text = notify(text,"red") 
                    return
                print("Checking Passed")
                dict_of_solutions = dict()
                dict_of_solutions_paths = dict()
                print('Scenario Calculation Started...')
                k = sum([len(liste) for _,liste in scenario_mapper.items()])
                j=0
                ok,message = True,""
                for sc in list(scenario_mapper):
                    dict_of_solutions[sc] = dict()
                    dict_of_solutions_paths[sc] = dict()
                    for sub_sc in scenario_mapper[sc]:
                        j = j + 1
                        text = f"({j}/{k})... Calculating  scenario ({sc}) with sub scenario ({sub_sc})"
                        print(text)
                        if ok:
                            div_spinner.text = spinner_text.replace("###text",text)
                        else:
                            div_spinner.text = spinner_text.replace("###text",text).replace("###text2",message).replace("none","true")                            
                        
                        ok,output_data,message = scenario_calculation(sc,sub_sc)
                        dict_of_solutions[sc][sub_sc] = output_data 
                        
                        if ok:
                            ok2,message2,path_download_zip = save_scenario(path_scenarios,sc,sub_sc,output_data)
                            if ok2:
                                message = f"Done: {sc} # {sub_sc} : {message}"
                            else:
                                message = message2
                        else:
                            message = f"Error @  {sc} # {sub_sc} : {message}"
                        print(message)
                        
                print('Scenario Calculation Done')
                ok,message = zip_all_scenarios(path_scenarios)
                if ok:
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
                                        <p><a href="""+"'"+message+"'"""" download="output.zip">Download ZIP File </a>  <p>                   
                                        </strong>
                                        </div>
                                        """
                else:
                    notify(message,"red") 
                    
#                output_tabs = compare_plot(dict_of_solutions)
#                output.tabs  = output_tabs        
                return None# XXX
# =============================================================================
            else:
                df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
                if df.shape[0] == 0:
                    del df
                    for k in list(carrier_dict):
                        carrier_dict.pop(k,None)
                    div_spinner.text = notify("No Heat Generators available","red") 
                    return
    
                if float(to_install.value) > 0 and not invest_button.active:
                    div_spinner.text = notify("The installed capacities are not enough to cover the load","red") 
                    return
    
                div_spinner.text = load_text
                output.tabs = []
    #            if type(grid.children[0]) != type(Div()):
    #                grid.children = [Div()]
                div_spinner.text = ""
    
    
                div_spinner.text = spinner_text.replace("###text","Dispatch in progress, please be patient ...")
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
                ## Categorize
                data["categorize"] = {}
                _dataframe= pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore')
                select_tec_options = [x.replace("CHP Steam Extraction","CHP-SE").replace("CHP Back Pressure","CHP-BP") for x in select_tec_options_model]
                for j in select_tec_options:
                    data["categorize"][j] = _dataframe["name"][_dataframe["type"] == j].values.tolist()
                ## thermal efficiencc
                _n_th = {}
                data["n_th"] = {**data["n_th"],**_nth}
                for k,v in data["n_th"].items():
                    if type(v)==list:
                        _n_th = {**_n_th,**dict(zip(zip([k]*8760,range(1,8760+1)),v))}
                    else:
                        _n_th = {**_n_th,**dict(zip(zip([k]*8760,range(1,8760+1)),[v]*8760))}
                data["n_th"] = _n_th
                for k in list(_nth):
                    _nth.pop(k,None)
                ## 
                solutions = None
                selection = [[],[]]
                inv_flag = False
                if invest_button.active:
                    inv_flag = True
                    selection0 = data_table.source.selected["1d"]["indices"] #XXX: 0.12.10
                    selection1 = data_table_heat_storage.source.selected["1d"]["indices"] #XXX: 0.12.10
    #                selection0 = data_table.source.selected.indices #XXX:  > 0.12.10
    #                selection1 = data_table_heat_storage.source.selected.indices #XXX:  > 0.12.10
                    selection = [selection0,selection1]
                    if selection[0] == []:
                        div_spinner.text = notify("""<p>Error: Please specify the technologies for the invesment model !!!<p><p>Mark Heat Generators by pressing "CTRL" + "left mouse"<p><p>Selection is marked yellow <p>""","red","Please specify the technologies for the invesment model !!!","red") 
                        return
                solutions,_message,_ = execute(data,inv_flag,selection)
    
                print('calculation done')
                print ("Ploting started..")
                if solutions == "Error1":
                    div_spinner.text = notify("Error: No Capacities are installed !!!","red")
                elif solutions == "Error2":
                    div_spinner.text = notify("Error: The installed capacities are not enough to cover the load !!!","red") 
                elif solutions == "Error3#":
                    print("Error in Saving Solution to JSON !!!")
                    div_spinner.text = notify("Error @ Generating JSON!!!","red")          
                elif solutions == "Error3":
                    print("Cause: Infeasible or unbounded model !!!")
                    div_spinner.text = notify("Error: Infeasible or unbounded model !!!","red")  
                elif solutions == None:
                    print("Error: Something get Wrong")
                    print(_message)
                    div_spinner.text = notify("Error: "+_message,"red")
                else:
                    output_tabs = plot_solutions(solution=solutions)
    
                    if output_tabs == "Error4":
                        print("Error @ Ploting  !!!")
                        div_spinner.text = notify("Error: @ Ploting !!!","red") 
                    else:
                        output.tabs = output_tabs #TODO: render only when a toggle button is active
                        print("Ploting done")
                        print("Download output_graphics started...")
                        time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                        filename = "output_graphs.html"                    
                        path_download_html = os.path.join(create_folder(time_id),filename)
                        output_file(path_download_html,title="Dispatch output", mode='inline')
#                        save(output) #XXX: not working , dont know why, need to create new objecs !!
                        save(Tabs(tabs=plot_solutions(solution=solutions)))
                        path_download_html_ = os.path.join("download","static",time_id,filename)
    #                    trigger_download(time_id,filename)
                        print("Graphics Download done")
                        print("Download output data started...")
                        # -- Download JSON
#                        time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                        filename = "output_data.json"
                        path_download_json = os.path.join(create_folder(time_id),filename)
                        with open(path_download_json, "w") as f:
                            json.dump(solutions, f)
                        path_download_json_ = os.path.join("download","static",time_id,filename)
    #                    trigger_download(time_id,filename)
                        # -- Download XLSX
#                        time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                        filename = "output_data.xlsx"
                        path_download_xlsx = os.path.join(create_folder(time_id),filename)
                        json2xlsx(solutions,path_download_xlsx)
                        path_download_xlsx_ = os.path.join("download","static",time_id,filename)
                        print("Download output data done")
                         # -- Download ZIP
                        print("Create Zip File...")
#                        time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                        filename = "output_data.zip"
                        path_download_zip = os.path.join(create_folder(time_id),filename)
                        with ZipFile(path_download_zip,"w") as zip_file:
                            for file in [path_download_html,path_download_json,
                                         path_download_xlsx]:
                                zip_file.write(file,os.path.basename(file))
                        path_download_zip_ = os.path.join("download","static",time_id,filename)
                        print("Create Zip File done")
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
                        <p><a href="""+"'"+path_download_html_+"'"""" download="output.html">Download HTML File </a> <p>
                        <p><a href="""+"'"+path_download_xlsx_+"'"""" download="output.xlsx">Download XLSX File </a>  <p>
                        <p><a href="""+"'"+path_download_zip_+"'"""" download="output.zip">Download ZIP File </a>  <p>                   
                        </strong>
                        </div>
                        """
                        print("Calculation is Done !")
                        print("Render in Browser...")
        except Exception as e:
            print(str(e))
            print(e)
            print(type(e))
            div_spinner.text = notify("Fatal Error @ Running","red") 
# =============================================================================
    def upload_callback(attr, old, new):
        try:
            div_spinner.text = load_text
            print('Upload started')
            file_type = file_source.data['file_name'][0].split(".")[1]
            raw_contents = file_source.data['file_contents'][0]
            prefix, b64_contents = raw_contents.split(",", 1)
            time_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") 
            file_contents = base64.b64decode(b64_contents)
            path_scenarios = create_folder(time_id)
            zip_file_path = os.path.join(path_scenarios,"upload.zip")
            if  file_type in ["zip"] and scenario_button.active:
                print("Uploading Scenarios")
                try:
                    with open(zip_file_path, 'wb') as zf:
                        zf.write(file_contents)   
                    with ZipFile(zip_file_path,"r") as zip_ref:
                        zip_ref.extractall(path_scenarios)
                        sc_sub_sc = zip_ref.namelist()
                    
                    _scenario_mapper = dict()
                    for x in sc_sub_sc:
                        sc,sub_sc = os.path.split(x)
                        _path = os.path.join(path_scenarios,x)
                        sub_sc = [] if os.path.isdir(_path) else [sub_sc.split(".")[0]]
                        _scenario_mapper[sc] = _scenario_mapper.get(sc,[]) + sub_sc
                    ###    
                    pop_table(heat_generator_table)
                    pop_table(heat_storage_table)
                    pop_table(paramters_table)
                    pop_table(price_emmission_factor_table)
                    for wk in widgets_keys:
                        pop_table(profiles_table[wk])
                    pop_table(carrier_table)           
                    pop_table(external_data_table)
                    pop_table(external_data_map_table)
                    pop_table(scenario_mapper)
                    pop_table(_nth_table)                    
                    ##
                    
                    for x in list(_scenario_mapper):
                        scenario_mapper[x] = _scenario_mapper[x]
                    for sc_name,sub_sc_list in scenario_mapper.items():                
                        heat_generator_table[sc_name] = dict()
                        heat_storage_table[sc_name] = dict()
                        paramters_table[sc_name] = dict()
                        price_emmission_factor_table[sc_name] = dict()
                        for wk in widgets_keys:
                            profiles_table[wk][sc_name] = dict()
                        carrier_table[sc_name] = dict()
                        external_data_table[sc_name] = dict()
                        external_data_map_table[sc_name] = dict()
                        _nth_table[sc_name] = dict()
                        for sub_sc_name in sub_sc_list:
                            _path = os.path.join(path_scenarios,sc_name,sub_sc_name+".xlsx")
                            heat_generator_table[sc_name][sub_sc_name] = pd.read_excel(_path,sheet_name = sheets[0], index_col = 0)[input_list+["type"]].apply(pd.to_numeric, errors='ignore').fillna(0)
                            heat_storage_table[sc_name][sub_sc_name] = pd.read_excel(_path,sheet_name = sheets[3], index_col = 0)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore').fillna(0)
                            paramters_table[sc_name][sub_sc_name] = pd.read_excel(_path,sheet_name = "Data", index_col = 0)[parameter_list].apply(pd.to_numeric, errors='ignore').fillna(0)
                            price_emmission_factor_table[sc_name][sub_sc_name] = pd.read_excel(_path,sheet_name = sheets[1], index_col = 0)[input_price_list].apply(pd.to_numeric, errors='ignore').fillna(0)
                            carrier_table[sc_name][sub_sc_name] = pd.read_excel(_path,sheet_name = "Energy Carrier", index_col = 0).set_index("name")["carrier"].to_dict()
                            data2 =  pd.read_excel(_path,sheet_name = "Default - External Data", index_col = 0)
                            external_data_map_table[sc_name][sub_sc_name] = {i:dict(Default = data2[i][0]) for i in external_data_map}
                            data3 = pd.read_excel(_path,sheet_name = sheets[0], index_col = 0)
                            data3 = data3[_elec].set_index(data3.name)
                            for i in _elec:
                                external_data_map_table[sc_name][sub_sc_name][i]= data3[i][~data3[i].isna()].to_dict()
                                external_data_map_table[sc_name][sub_sc_name][i]["Default"] = data2[i][0]            
                            external_data_table[sc_name][sub_sc_name] = dict()
                            for i,_dict in external_data_map_table[sc_name][sub_sc_name].items():
                                external_data_table[sc_name][sub_sc_name][i] = dict()
                                for j,string in _dict.items():
                                    (c,y),fit_string = extract(string)
                                    if (c,y) == (0,0):
                                        string = external_data_map_table[sc_name][sub_sc_name][i]["Default"]
                                        (c,y),fit_string = extract(string)
                                    offset,constant = find_FiT(fit_string)
                                    if type(constant) == str:
                                        profile = data_kwargs[i]["data"][c,y] + offset
                                    else:
                                        profile = np.ones(8760)*constant + offset
                                    
                                    profile = profile.tolist()
                                    if j == "Default":
                                        profiles_table[i][sc_name][sub_sc_name] = dict(zip(range(1,len(profile)+1),profile))
                                    external_data_table[sc_name][sub_sc_name][i][j] = profile                              
                            _nth_table[sc_name][sub_sc_name] = dict()

#                    # fires load_scenario_callback
                    for _,dictt in scenario_dict.items():
                        dictt["tools"]["sc_select"].options = list(scenario_mapper)
                        dictt["tools"]["sc_select"].value = sc_name
                    
                    div_spinner.text = notify(f"""Scenario Upload Done""", "green") 
                                
                    #os.remove(zip_file_path)
                    
                except Exception as e:
                    print(str(e))
                    div_spinner.text = notify("Fatal Error @ Upload in Scenario Mode ", "red")
            
            elif  file_type in ["xlsx","xls"]:
                print(file_type)
                file_io = io.BytesIO(file_contents)
                excel_object = pd.ExcelFile(file_io, engine='xlrd')
#                data2 = excel_object.parse(sheet_name = sheets[0], index_col = 0,skiprows = range(22,50)).apply(pd.to_numeric, errors='ignore')
                data = excel_object.parse(sheet_name = sheets[0], index_col = 0)
                data2 = data[input_list+["type"]].apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
                data2["index"] = data2.index
                data_table.source.data.update(data2)

#                data2 = excel_object.parse(sheet_name = sheets[1], index_col = 0,skiprows = range(14,50)).apply(pd.to_numeric, errors='ignore')
                data2 = excel_object.parse(sheet_name = sheets[1], index_col = 0).apply(pd.to_numeric, errors='ignore')

                data2 = data2.fillna(0)
                data_table_prices.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = 'Data', index_col = 0).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0)
#                r = data2.shape[0]
#                data2 = excel_object.parse(sheet_name = 'Data', index_col = 0,skiprows = range(2,r+1)).apply(pd.to_numeric, errors='ignore')
#                data2 = data2.fillna(0)
                data_table_data.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = sheets[3]).apply(pd.to_numeric, errors='ignore')
                data2 = data2.fillna(0).reset_index()
#                print(f"Shape is {data2.shape}")
#                print(data2)
                data_table_heat_storage.source.data.update(data2)

                data2 = excel_object.parse(sheet_name = 'Energy Carrier', index_col = 0)
                data2 = data2.set_index(data2["name"])
                del data2["name"]
                for k in list(carrier_dict):
                    carrier_dict.pop(k,None)
                for k,v in data2.to_dict()["carrier"].items():
                    carrier_dict[k]=v
                
                data3 = data[_elec].set_index(data.name)
                for i in _elec:
                    external_data_map[i]= data3[i][~data3[i].isna()].to_dict()
                    
                data2 = excel_object.parse(sheet_name = 'Default - External Data',index_col=0)
                for i in external_data_map:
                    external_data_map[i]["Default"] = data2[i][0]
                    ## XXX: callbacks take very long
                    (c,y),fit_string = extract(data2[i][0])
                    offset,constant = find_FiT(fit_string)
                    constant = "" if type(constant) == str else constant
                    widgets[i]["select"].value = data_kwargs[i]["dic"][c]+"_"+str(y)
                    widgets[i]["offset"].value = str(offset)
                    widgets[i]["constant"].value = str(constant)
                    
                div_spinner.text = notify("Upload Done","green")
            else:
                print("Not a valid file to upload")
                div_spinner.text = notify("Error: Not a valid file to upload","red")
            print('Upload done')

        except Exception as e:
            print(str(e))
            div_spinner.text = notify("Fatal Error @ Update ", "red")
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
        add_to_tec.options = _opt
        if _opt:
            add_to_tec.value = _opt[0]
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
        
        add_external_data_to_heat_producers()
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
        print(scenario_mapper)
        output.tabs = []
        div_spinner.text = ""
#        grid.children = [Div()] # XXX
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
#        data_table_data.source.data[parameter_list[3]] = [new]  #XXX: this throws FutureWarning 
        df = pd.DataFrame(data_table_data.source.data) 
        df.loc[0,parameter_list[3]] = new 
        data_table_data.source.data.update(df) 
# =============================================================================
    def ivest_callback(active):
        if active:
            div_spinner.text = notify("""Mark Technologies by pressing "CTRL" +  "left mouse", Rows are marked yellow ""","red")
        else:
            div_spinner.text = ""
# =============================================================================
    def add_external_data_to_heat_producers():
        for i in data_kwargs:
            ###
            _name,_jahr = widgets[i]["select"].value.split("_")
            _name = data_kwargs[i]["dic_inv"][_name]
            try:
                _off = float(widgets[i]["offset"].value)
                _off = f"{_off}f" if _off != 0 else ""
            except:
                _off = ""
            try:
                _const = float(widgets[i]["constant"].value)
                _const = f"{_const}h"
            except:
                _const = ""
                
            if _const != "" and _off != "":
                _str = f", {_const} + {_off}" 
            elif _const != "" and _off == "":
                _str = f", {_const}"
            elif _const == "" and _off != "":
                _str = f", {_off}"
            else:
                _str = ""
        
            external_data_map[i][widgets[i]["tec"].value] = f" {_name} # {_jahr} {_str}"
            ###
            if widgets[i]["ok"].clicks > 0 :
                _y = widgets[i]["source"].data["y"]
                external_data[i][widgets[i]["tec"].value]= _y if type(_y) == list else list(_y)

                if widgets[i]["tec"].value == "Default":
                    div_spinner.text = notify(i+" Data is set as "+widgets[i]["tec"].value,"green")
                else:
                    div_spinner.text = notify(i+" Data For "+widgets[i]["tec"].value+" is added", "green")
                widgets[i]["ok"].clicks = 0 # this calls again this function
# =============================================================================
    def delete_hg():
        df = pd.DataFrame(data_table.source.data)
        for hg in df.iloc[data_table.source.selected["1d"]["indices"]].name.tolist():
            _nth.pop(hg,None)
#        df = df.drop(data_table.source.selected.indices).reset_index(drop=True)  #XXX: >0.12.10
        df = df.drop(data_table.source.selected["1d"]["indices"]).reset_index(drop=True)  #XXX: 0.12.10       
        data_table.source.data = {key:list(dic.values()) for key,dic in df.to_dict().items()}
        
    def delete_hs():
        df = pd.DataFrame(data_table_heat_storage.source.data)
#        df = df.drop(data_table_heat_storage.source.selected.indices).reset_index(drop=True) #XXX: >0.12.10
        df = df.drop(data_table_heat_storage.source.selected["1d"]["indices"]).reset_index(drop=True)  #XXX: 0.12.10

        data_table_heat_storage.source.data = {key:list(dic.values()) for key,dic in df.to_dict().items()}       
           
# =============================================================================
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
    button1_1.on_click(delete_hg)
    button2_1.on_click(delete_hs)

# =============================================================================
#   Initilizing GUI with Default Values
# =============================================================================
    # Pmax Initilizing
    update_pmax(None,None,None)
    # Total Demand initilize with input
    args_callback(None,None,None) 
    
#%% Adding Heat Generators: Widgets callbacks, layouts etc.
# =============================================================================
#  GUI Elements for adding Technologies
# =============================================================================
    ok_button = Button(label='✓ ADD', button_type='success',width=60)
    cancel_button = Button(label='	🞮 CANCEL', button_type='danger',width=60)
    select_tec = Select(title="Add Heat Generator:", options = select_tec_options )
    select_tec2 = Select(value="",disabled=True)

    cop_label = TextInput(placeholder="-", title="COP",disabled= True)
    flow_temp = Select(title="Inlet Temperature")
    return_temp = Select(title="Return Temperature")
    energy_carrier_select = Select(options = energy_carrier_options, 
                                   title="Energy Carrier",value = energy_carrier_options[0])

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
    cop_widget_list = [return_temp, flow_temp, cop_label]
    hg_widget_list = [select_tec,select_tec2, installed_cap, n_th_label, n_el_label,
            ik_label, opex_fix_label, opex_var_label,lt_label,
            renewable_factor, must_run_box,energy_carrier_select,name_label,
            ok_button,cancel_button
            ]
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
    layout1 = [tec_param_panel, cop_panel, finance_param_panel , model_param_panel]
#    layout2 = [tec_param_panel, finance_param_panel , model_param_panel]
    tabs_geneator = Tabs(tabs=layout1 ,width = 800)
    tec_buttons = widgetbox(children = [select_tec,select_tec2])
    hg_layout = column(children = [tec_buttons,widgetbox(tabs_geneator),
                                   row(children = [ok_button,cancel_button])])
    disable_widgets(hg_widget_list+cop_widget_list,True)
# =============================================================================
#  Callbacks for adding Technologies
# =============================================================================
    def add_heat_generator():
        div_spinner.text = load_text
        div2.text = div2.text.replace("none","true")
#        tabs.active = 1
        grid.active = 0
        disable_widgets(hg_widget_list,False)
        output.tabs = []
        select_tec.value = select_tec.options[0]
        installed_cap.end=int(float(pmax.value))+1
        energy_carrier_select.options =  data_table_prices.source.data["energy carrier"]
        div_spinner.text = ""
# =============================================================================
    def cancel():
        div_spinner.text = load_text
        div2.text = div2.text.replace("true","none")
        tabs.active = 0
        disable_widgets(hg_widget_list+cop_widget_list,True)
        div_spinner.text = ""
# =============================================================================
    def add_to_cds():
        # if user refreshes site, create new dict
        _df= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        if _df.shape[0] == 0:
            for k in list(carrier_dict):
                carrier_dict.pop(k,None)
        div_spinner.text = load_text
        df2 = pd.DataFrame(data_table.source.data)
        df2["index"] = df2.index
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
        div_spinner.text = notify("Heat Generator added","green")
# =============================================================================
    def add_heat_pump():
        disable_widgets(cop_widget_list,False)
        cop_label.disabled = True
        flow_temp.options = flow_temp_dic[tec_mapper_inv[select_tec2.value]]
        flow_temp.value = flow_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback, thus need of try block
        return_temp.options = return_temp_dic[tec_mapper_inv[select_tec2.value]]
        return_temp.value = return_temp_dic[tec_mapper_inv[select_tec2.value]][0] # Caution: this calls the cop_callback,
        cop_label.value = str(heat_pumps[tec_mapper_inv[select_tec2.value]].loc[return_temp.value,flow_temp.value])
        n_th_label.value = cop_label.value
        n_th_label.disabled = True
#        tabs_geneator.tabs = layout1
# =============================================================================
    def add_tec(name,old,new):
        div_spinner.text = load_text
        n_th_label.disabled = False
        disable_widgets(cop_widget_list,True)
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
            if select_tec.value == "heat pump": 
                disable_widgets(cop_widget_list,False)   
                cop_label.disabled = True
            select_tec2.disabled = False
        else:
            select_tec2.disabled = True

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
            disable_widgets(cop_widget_list,True)
            
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
    
#%% Adding Heat Storages: Widgets callbacks, layouts etc.
# =============================================================================
#   Gui Elements for adding heat storages   
# =============================================================================
    ok_button_hs = Button(label='✓ ADD', button_type='success',width=60)
    cancel_button_s = Button(label='	🞮 CANCEL', button_type='danger',width=60)
    select_hs = Select(title="Select a Heat Storage:", options = select_hs_options, 
                       value=select_hs_options[0])
    tabs_geneator_hs = Tabs(tabs=[] ,width = 800)
    name_hs = TextInput(placeholder="-", title="name")
    capacity_hs = TextInput(placeholder="-", title="Storage Capacity [MWh]")
    losses_hs =  Slider(start=0, end=100, value=1, step=1, title="Hourly Stoarge Losses [%]")
    unloding_power = TextInput(placeholder="-", title="maximum unloading power  [MW]")
    uloading_efficiency = Slider(start=0, end=1, value=.980, step=.001, title="unloading efficiency")
    loading_power = TextInput(placeholder="-", title="maximum loading power  [MW]")
    loading_efficiency = Slider(start=0, end=1, value=.980, step=.001, title="loading efficiency")
    inv_cost_hs = TextInput(placeholder="-", title="Invesment costs for additional storage capacity  [€/MWh]")
    opex_fix_hs = TextInput(placeholder="-", title="OPEX fix [€/MWh]")
    lt_hs = TextInput(placeholder="-", title="Life Time [a]")
    
    widget_hs = [name_hs, capacity_hs, losses_hs, unloding_power,
                 loading_power, loading_efficiency, uloading_efficiency, 
                 inv_cost_hs, opex_fix_hs, lt_hs]
    widgets_dict_hs = dict(zip((list(heat_storage_list_mapper)),widget_hs))
    
    widget_list_hs = [ok_button_hs, cancel_button_s, select_hs, ] + widget_hs
# =============================================================================
#   Layout for adding heat storages
# =============================================================================
    tec_param_layout_hs = column(children=[row(children=[name_hs,capacity_hs]),
                                            row(children=[loading_power,
                                                          unloding_power]),
                                           row(children=[loading_efficiency,
                                                          uloading_efficiency])])
    finance_param_layout_hs = column(children=[inv_cost_hs,opex_fix_hs,lt_hs])
    model_param_layout_hs = widgetbox(losses_hs)
    
    tec_param_panel_hs = Panel(child=tec_param_layout_hs, title="Technical Parameters")
    finance_param_panel = Panel(child=finance_param_layout_hs, title="Finance Parameters")
    model_param_panel = Panel(child=model_param_layout_hs, title="Model Parameters")

    layout_hs = [tec_param_panel_hs, finance_param_panel , model_param_panel]
    tabs_geneator_hs.tabs = layout_hs
    
    children_hs = [widgetbox(select_hs),widgetbox(tabs_geneator_hs),row(children = [ok_button_hs,cancel_button_s])]
    hs_layout = column(children_hs)
# =============================================================================
#     Callback for adding heat storages
# =============================================================================
    def autoload_hs(name,old,new):
        df = pd.read_excel(path_parameter,sheets[3],skiprows=[0])
        df.index = df.name
        for key,element in widgets_dict_hs.items():
            try:
                element.value = float(df.loc[select_hs.value][key])
            except:
                element.value = str(df.loc[select_hs.value][key])   
# =============================================================================
    def add_heat_storage():
        div_spinner.text = load_text
        div2.text = div2.text.replace("none","true")
#        tabs.active = 1  
        output.tabs = []
        div_spinner.text = load_text   
        grid.active = 1  
        disable_widgets(widget_list_hs,False)
        autoload_hs("","","") 
        div_spinner.text = ""
# =============================================================================
    def add_data_table():
        div_spinner.text = load_text
        df2 = pd.DataFrame(data_table_heat_storage.source.data)
        df2["index"] = df2.index
        df2.set_index(df2["index"])
        del df2["index"]
        new_data={}
        for x in heat_storage_list_mapper:
            if x == "name":
                try:
                    new_data[x] = new_name(str(name_hs.value),data_table_heat_storage.source.data["name"].tolist())
                except:
                    new_data[x] = new_name(str(name_hs.value),data_table_heat_storage.source.data["name"])
            else:
                new_data[x] = str(widgets_dict_hs[x].value)
        df2 = df2.append(new_data,ignore_index=True)
        df2 = df2.apply(pd.to_numeric, errors='ignore')
        df2["index"] = df2.index
        data_table_heat_storage.source.data.update(df2)
        del df2
        div_spinner.text = notify("Heat Storage added","green")
# =============================================================================
    def cancel_hs():
        div_spinner.text = load_text
        div2.text = div2.text.replace("true","none")
        disable_widgets(widget_list_hs,True) 
        tabs.active = 0
        div_spinner.text = ""
# =============================================================================
#   Signal Emitting / Coupling for adding heat_storages
# =============================================================================
    button2.on_click(add_heat_storage)
    cancel_button_s.on_click(cancel_hs)
    ok_button_hs.on_click(add_data_table)
    select_hs.on_change('value', autoload_hs) 
# =============================================================================
#  Initializing with default values
# =============================================================================
    disable_widgets(widget_list_hs,True) 

#%% Loading Individual Data: Widgets callbacks, layouts etc.
# =============================================================================
#  GUI Elements for Loading External Data
# =============================================================================
    distribution_options = ["Dirichlet Distribution","Normal Distribution",
                                     "Linear Distribution","None"]
    individual_data_upload_button = Button(label="Upload External Data", button_type="danger")
    create_individual_data = Select(title="Create Data", value="None", 
                            options=distribution_options)
    create_widgets = [TextInput(title="", value="", placeholder= "",
                                disabled=True),
                      TextInput(title="", value="", placeholder= "",
                                disabled=True)]             
    modtools = modification_tools(offset="Set a Offset", 
                                       constant="Set to a Constant Value", 
                                       scale ="Scale", 
                                       mean = "Use mean value", 
                                       total = "Set Sum of all values", 
                                       tec = "Add to")
    individual_data_name = TextInput(title="Set a name for your Data", 
                                     value="individual", placeholder= "-")
    individual_data_data_table = DataTable(source= ColumnDataSource(dict(x=[],
                                                                         y=[])),
                           columns=[TableColumn(field="y", title="Value",
                                                width=200)],
                           width=200, height=650,fit_columns=True,
                           editable=True)    
    individual_data_fig = figure(plot_height=650,plot_width=750,
                                 x_axis_label='Time in hours', y_axis_label='Value',
                                 min_border_left = 55 , min_border_bottom = 55,
                                 tools=["pan,wheel_zoom,box_zoom,reset,save"],)
    individual_data_fig.line('x', 'y', source=individual_data_data_table.source, line_alpha=0.6)
    individual_data_fig.toolbar.logo = None

# =============================================================================
# 
# =============================================================================
    modtools += [individual_data_name,add_to_tec]
    dic_modtools = dict(zip(["offset","constant","scale","mean","total","add",
                            "save","name","tec"],
                            modtools))          
    def setLabel(widgets,**kwargs):
        for i in range(2):
            widgets[i].title = kwargs["title"][i]
            widgets[i].value = kwargs["value"][i]
            widgets[i].placeholder = kwargs["placeholder"][i]
            widgets[i].disabled = kwargs["disabled"][i]

    dirichlet_options = dict(title=["sum Σ",""], value=["100",""], 
                             placeholder=[">0","-"],disabled=[False,True])
    normal_options = dict(title=["my µ","sigma σ"], value=["100","100"], 
                          placeholder=["-","-"], disabled=[False,False])
    linear_options = dict(title=["start","stop"], value=["-10","100"], 
                          placeholder=["-","-"], disabled=[False,False])
    none_options = dict(title=["",""], value=["",""], 
                          placeholder=["-","-"], disabled=[True,True])
    def dirichlet(summe,_):
        x = np.random.dirichlet(np.ones(8760)/5)*summe
        x[-1] += summe - sum(x)
        return x
    def normal(my,sigma):
        return np.random.normal(my,sigma,8760)
    def linear(start,stop):
        return np.linspace(start,stop,8760,endpoint=True)
    def noneFunc(__,_):
        return ""
    
    def plotDistribution(a1,a2,function):
        try:
            a1= float(a1)
        except:
            a1 = 0
        try:
            a2 = float(a2)
        except:
            a2 = 0
        
        y = function(a1,a2)
        x = np.arange(8760)
        if type(y) == str:
            x=[]
            y=[]
        else:
            y = np.round(y,3)
        individual_data_data_table.source.data = dict(x=x,y=y)
    
        
    create_options = dict(zip(distribution_options,
                              zip([dirichlet_options,normal_options,
                                   linear_options,none_options],
                                  [dirichlet,normal,linear,noneFunc])))
    
    dic_modtools["add"].value = widgets_keys[0]
    dic_modtools["add"].options = widgets_keys + ["n_th/COP"]
    dic_modtools["save"].label = '✓ Save'
    dic_modtools["total"].disabled=False
    for i in ["total","offset"]:
        dic_modtools[i].value=""
        dic_modtools[i].placeholder="-"
# =============================================================================
#  Widget Layout for Loading External Data
# =============================================================================    
    r1 = row(children=[column([individual_data_upload_button,
                               create_individual_data]),
                        column(create_widgets)])
    
    r2 = row(children=[widgetbox(individual_data_data_table),individual_data_fig,
     column([modtools[i] for i in [4,0,1,2,3,5,8,7,6]])])
    
    individual_data_layout = column(children=[r1,r2])
    tabs.tabs += [Panel(child=individual_data_layout,title="Load Individual Data")]
# =============================================================================
#   CALLBACKS FOR Loading External Data
# =============================================================================
    def modCallback(name,old,new):
        div_spinner.text = load_text       
        y = individual_data_data_table.source.data["y"]
        y_profil,s = profil(y)
        dic_modtools["total"].value  = str(round(s,3))
        if dic_modtools["mean"].active != [] and individual_data_data_table.source.data["y"] != []:
            individual_data_data_table.source.data["y"] = np.mean(y)*np.ones(8760)
            dic_modtools["total"].value = str(round(sum(individual_data_data_table.source.data["y"]),3))
        else:
            if dic_modtools["offset"].value =="":
                dic_modtools["offset"].value = "0"
            if dic_modtools["constant"].value =="":
                dic_modtools["constant"].value = "-"
            if dic_modtools["constant"].value == "-" :
                y_new = y_profil * float(dic_modtools["total"].value) * \
                dic_modtools["scale"].value + \
                float(dic_modtools["offset"].value)
                individual_data_data_table.source.data["y"] = np.round(y_new,3)
                dic_modtools["total"].value = str(round(sum(individual_data_data_table.source.data["y"]),3))
            else:
                y_new = (float(dic_modtools["constant"].value) + \
                         float(dic_modtools["offset"].value) )*\
                         np.ones(8760) * dic_modtools["scale"].value 
                individual_data_data_table.source.data["y"]= np.round(y_new,3)
                dic_modtools["total"].value = str(round(sum(individual_data_data_table.source.data["y"]),3))
        div_spinner.text = ""
                
    def totalCallback(name,old,new):
        div_spinner.text = load_text
        y = individual_data_data_table.source.data["y"] 
        y_profil,s = profil(y)
        
        try:
            s2 = float(dic_modtools["total"].value)
        except:
            s2 = 0
        if s2 == 0:
            s2 = s
            dic_modtools["total"].value = str(round(s2,3))
        individual_data_data_table.source.data["y"] = np.round(y_profil*s2,3)
        div_spinner.text = ""
        
    def setLayout(name,old,new):
        div_spinner.text = load_text
        opt,function = create_options[create_individual_data.value]
        setLabel(create_widgets,**opt)
        plotDistribution(create_widgets[0].value, create_widgets[1].value,
                         function)
        dic_modtools["total"].value = str(round(sum(individual_data_data_table.source.data["y"]),3))
        modCallback("","","")
        div_spinner.text = ""
    
    def createCallback(name,old,new):
        div_spinner.text = load_text
        opt,function = create_options[create_individual_data.value]
        plotDistribution(create_widgets[0].value, create_widgets[1].value,
                         function)
        dic_modtools["total"].value = str(round(sum(individual_data_data_table.source.data["y"]),3))
        modCallback("","","")
        div_spinner.text = ""
    
    def saveCallback():
        if len(individual_data_data_table.source.data["y"]) == 8760:
            div_spinner.text = load_text
            if dic_modtools["add"].value != "n_th/COP":
                widget_data = data_kwargs[dic_modtools["add"].value]
        #        print(list(widget_data))
                widget_data["data"][dic_modtools["name"].value,1] = individual_data_data_table.source.data["y"]
                widget_data["dic"][dic_modtools["name"].value] = dic_modtools["name"].value
                widget_data["dic_inv"] = invert_dict(widget_data["dic"])
                widgets[dic_modtools["add"].value]["select"].options += [dic_modtools["name"].value+"_1"]
                div_spinner.text = notify("External Data "+dic_modtools["name"].value+" added to "+dic_modtools["add"].value + " as "+dic_modtools["name"].value+"_1", "green")
            else:
                if dic_modtools["tec"].value != "None":
                    _nth[dic_modtools["tec"].value] = list(individual_data_data_table.source.data["y"])
                    print(f"""COP/ n_th added to {dic_modtools["tec"].value}""")
                    div_spinner.text = notify(f"""n_th - External Data added to {dic_modtools["tec"].value}""", "green")
                else:
                    div_spinner.text = notify("Nothing to save","red")
        else:
            div_spinner.text = notify("Nothing to save","red")

    def loadCallback(name,old,new):
        try:
            div_spinner.text = load_text
            create_individual_data.value = "None"
            file_type = file_source2.data['file_name'][0].split(".")[1]
            raw_contents = file_source2.data['file_contents'][0]
            prefix, b64_contents = raw_contents.split(",", 1)
            file_contents = base64.b64decode(b64_contents)
            file_io = io.BytesIO(file_contents)
            if  file_type.lower() in ["xlsx","xls"]:
                excel_object = pd.ExcelFile(file_io, engine='xlrd')
                y = excel_object.parse().fillna(method='ffill', limit=50).values[:8760,0]
            elif file_type.lower() in ["csv"]:
                y = pd.read_csv(file_io).fillna(method='ffill', limit=50).values[:8760,0]
            else:
#                print("Invalid Filetype to load")
                div_spinner.text = notify("Error: Invalid Filetype to load @ Loading External Data ", "red") 
                return
            if len(y) == 8760:
                x = np.arange(8760)
                individual_data_data_table.source.data = dict(x=x,y=np.round(y,3))
                modCallback("","","")
#                print("External Data Loaded")
                div_spinner.text = notify("External Data Loaded", "green") 
                
            else:
#                print("There are not enought data <"+str(len(y))+"/8760>")
                div_spinner.text = notify("Your File has not enought values (please specify 8760 values)", "red") 

        except Exception as e:
            print(str(e))
            div_spinner.text = notify("Fatal Error @ Loading External Data", "red") 

    def setCOP(name,old,new):
        _heat_generators= pd.DataFrame(data_table.source.data)[input_list].apply(pd.to_numeric, errors='ignore')
        _heat_generators = _heat_generators.fillna(0)
        _opt = list(_heat_generators["name"].values)
        _opt = _opt
        
        if dic_modtools["add"].value == "n_th/COP":
            dic_modtools["name"].disabled=True
            dic_modtools["tec"].options = _opt
            if _opt != []:
                dic_modtools["tec"].disabled = False
                dic_modtools["save"].disabled = False
            else:
                dic_modtools["save"].disabled = True
            
        else:
            dic_modtools["name"].disabled=False
            dic_modtools["tec"].options = ["None"]
            dic_modtools["tec"].disabled = True
            dic_modtools["save"].disabled = False
        
        
# =============================================================================
#   Signal Emitting / Coupling for Loading External Data
# =============================================================================
    create_individual_data.on_change('value', setLayout)
    
    for widget in create_widgets:
        widget.on_change('value', createCallback)
        
    for i in [0,1,2]:
        modtools[i].on_change('value', modCallback)    
        
    dic_modtools["mean"].on_change('active', modCallback)
    dic_modtools["total"].on_change('value', totalCallback)
    dic_modtools["save"].on_click(saveCallback)
    
    file_source2 = ColumnDataSource({'file_contents':[], 'file_name':[]})
    file_source2.on_change('data', loadCallback)
    individual_data_upload_button.callback = CustomJS(args=dict(file_source=file_source2), code =upload_code)
    dic_modtools["add"].on_change('value', setCOP)
    dic_modtools["tec"].on_change('value', setCOP)
    
#%% Scenario Mode: Widgets callbacks, layouts etc.
# =============================================================================
#   Data, GUI Elelements and Layout for Scenario Mode
# =============================================================================
    heat_generator_table = dict()
    heat_storage_table = dict()
    paramters_table = dict()
    price_emmission_factor_table = dict()
    profiles_table = {wk:dict() for wk in widgets_keys}
    carrier_table = dict()           
    external_data_table = dict()
    external_data_map_table = dict()
    scenario_mapper = dict()
    _nth_table = dict()
    
    scenario_button = Toggle(label="Scenario Mode", button_type="danger")
    scenario_paramters = ["Heat Producers and Heat Storage","Parameters", "Prices & Emission factors"] + widgets_keys  
    scenario_dict = {name: sub_scenario_tools() if name !="Heat Producers and Heat Storage" else scenario_tools() for name in scenario_paramters}
    
    # CSS snippet for (showwing)hide scneario widgets
    div = Div(text = """ <style>
              .scenario_tools {
                      display: none;
                      } 
              .sub_scenario_tools {
                      display: none;
                      }
                        """)
    
    # Prerenders the Scenario Widgets, 
    for panel in profiles_tabs.tabs:
        panel.child = column(scenario_dict[panel.title]["layout"],lay[panel.title])
        
    for panel in tabs.tabs:
        if panel.title in scenario_paramters:
            panel.child = column(scenario_dict[panel.title]["layout"],tabs_dic[panel.title] )
# =============================================================================
#   Callbacks for Scenario Mode
# =============================================================================
       
    def add_new_scenario(sc_name,sub_sc_name="default_sub"):
        heat_generator_table[sc_name] = { sub_sc_name : pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore').fillna(0)}
        heat_storage_table[sc_name] = { sub_sc_name : pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore').fillna(0)}
        paramters_table[sc_name] = { sub_sc_name : pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore').fillna(0)}
        price_emmission_factor_table[sc_name] = { sub_sc_name : pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore').fillna(0)}
        for wk in widgets_keys:
            profiles_table[wk][sc_name] = { sub_sc_name : dict(zip(range(1,len(widgets[wk]["source"].data["y"])+1),widgets[wk]["source"].data["y"]))}                
        carrier_table[sc_name] = { sub_sc_name : pd.DataFrame(carrier_dict,index=[0]).T.to_dict()[0]}
        external_data_table[sc_name] = { sub_sc_name : pd.DataFrame(external_data).to_dict()}
        external_data_map_table[sc_name] = { sub_sc_name : pd.DataFrame(external_data_map).to_dict()}
        scenario_mapper[sc_name] = [sub_sc_name]
        _nth_table[sc_name] = { sub_sc_name : _nth }
# =============================================================================
    def replace_name_of_scenario(sc_name_old,sc_name_new):       
        heat_generator_table[sc_name_new] = heat_generator_table.pop(sc_name_old)
        heat_storage_table[sc_name_new] = heat_storage_table.pop(sc_name_old)
        paramters_table[sc_name_new] = paramters_table.pop(sc_name_old)
        price_emmission_factor_table[sc_name_new] = price_emmission_factor_table.pop(sc_name_old)
        for wk in widgets_keys:
            profiles_table[wk][sc_name_new] = profiles_table[wk].pop(sc_name_old)
        
        carrier_table[sc_name_new] = carrier_table.pop(sc_name_old)
        external_data_table[sc_name_new] = external_data_table.pop(sc_name_old)
        external_data_map_table[sc_name_new] = external_data_map_table.pop(sc_name_old)
        scenario_mapper[sc_name_new] = scenario_mapper.pop(sc_name_old)
        _nth_table[sc_name_new] = _nth_table.pop(sc_name_old)
# =============================================================================        
    def scenario_mode_callback(active):
        if active:
            div.text = div.text.replace("none","true")
        else:
            div.text = div.text.replace("true","none")
            
        div_spinner.text = load_text
              
        for _name,sc_dict in scenario_dict.items(): 
            for __name,tool in sc_dict["tools"].items():
                tool.disabled = not active
        if active:
            # init with default values when scneario mode is enabled (for the first time after page refresh or when all scenarios are deleted)
            if not bool(heat_generator_table):
                add_new_scenario("default")
            else:
                sc = scenario_dict[scenario_paramters[0]]["tools"]["sc_select"].value
                sub_sc = scenario_dict[scenario_paramters[0]]["tools"]["sub_sc_select"].value
                
                data_table.source.data = df2data(heat_generator_table[sc][sub_sc])
                data_table_heat_storage.source.data = df2data(heat_storage_table[sc][sub_sc])
                data_table_prices.source.data = df2data(price_emmission_factor_table[sc][sub_sc])
                data_table_data.source.data = df2data(paramters_table[sc][sub_sc])

#                pop_table(external_data_map)
                for i, dict_ in external_data_map_table[sc][sub_sc].items():
                    external_data_map[i] = {k:v for k,v in dict_.items()} 
                    ## XXX: callbacks take very long
                    (c,y),fit_string = extract(dict_["Default"])
                    offset,constant = find_FiT(fit_string)
                    constant = "" if type(constant) == str else constant
                    widgets[i]["select"].value = data_kwargs[i]["dic"][c]+"_"+str(y)
                    widgets[i]["offset"].value = str(offset)
                    widgets[i]["constant"].value = str(constant)    
           
                
            div_spinner.text = notify("Scenario Mode is enabled","green")
        else:
            #TODO: Define what should happen when scenario mode is disabled, 
            # 1. delete all scenario except the default scenario
            # 2. only show current scenario and sub scenario, and so one can test/run one scenario manually
            # 3. ??
            option = 2
            if option == 1:
                pop_sub_sc(heat_generator_table)
                pop_sub_sc(heat_storage_table)
                pop_sub_sc(carrier_table)   
                pop_sub_sc(paramters_table)
                pop_sub_sc(price_emmission_factor_table) 
                for wk in widgets_keys:
                    pop_sub_sc(profiles_table[wk])   
                pop_sub_sc(external_data_table)   
                pop_sub_sc(external_data_map_table)   
            
            div_spinner.text = notify("Scenario Mode is disabled", "red")          
# =============================================================================
            
    def add_scenario_callback():
        div_spinner.text = load_text
        sc_name = scenario_dict[scenario_paramters[0]]["tools"]["sc_text"].value.strip()
        sub_sc_name = scenario_dict[scenario_paramters[0]]["tools"]["sub_sc_text"].value.strip()  

        if sc_name == "":
            div_spinner.text = notify(f"Error: Please define a name for your scenario !", "red") 
        elif sc_name in list(scenario_mapper):
            div_spinner.text = notify(f""" Error: The name "{sc_name}" is already given please define another""", "red") 
        elif sub_sc_name == "":
            div_spinner.text = notify(f"Error: Please define a name for your sub scenario !", "red") 
        else:
            add_new_scenario(sc_name,sub_sc_name)
            # fires load_scenario_callback
            for _,dictt in scenario_dict.items():
                dictt["tools"]["sc_select"].options = list(scenario_mapper)
                dictt["tools"]["sc_select"].value = sc_name
                try:
                    dictt["tools"]["sub_sc_select"].value = sub_sc_name
                except:
                    pass
            div_spinner.text = notify(f""" Scenario "{sc_name}" with sub scenario "{sub_sc_name}" successfully added """, "green") 
# =============================================================================
            
    def  apply_scenario_callback():
        div_spinner.text = load_text
        sc_name_new = scenario_dict[scenario_paramters[0]]["tools"]["sc_text"].value.strip()
        sc_name_old = scenario_dict[scenario_paramters[0]]["tools"]["sc_select"].value
        ### Check if new name is alradey given
        if sc_name_new in list(scenario_mapper) and sc_name_new !=sc_name_old :
            div_spinner.text = notify(f""" Can not change name of scenario "{sc_name_old}" to  "{sc_name_new}" because it is already taken, please choose another name """, "red")         
            return None
        
        ### Change name of Scenario
        if sc_name_new != "" and sc_name_new !=sc_name_old :
            replace_name_of_scenario(sc_name_old,sc_name_new)
        else:
            sc_name_new = sc_name_old
            
        # fires load_scenario_callback
        for _,dictt in scenario_dict.items():
            dictt["tools"]["sc_select"].options = list(scenario_mapper)
            dictt["tools"]["sc_select"].value = sc_name_new

        div_spinner.text = notify(f""" Successfully changed name in {scenario_paramters[0]} from "{sc_name_old}" to "{sc_name_new}" """, "blue") 
# =============================================================================

    def del_scenario(sc_name):
        heat_generator_table.pop(sc_name)
        heat_storage_table.pop(sc_name)
        paramters_table.pop(sc_name)
        price_emmission_factor_table.pop(sc_name)
        for wk in widgets_keys:
            profiles_table[wk].pop(sc_name)
        carrier_table.pop(sc_name)
        external_data_table.pop(sc_name)
        external_data_map_table.pop(sc_name)
        scenario_mapper.pop(sc_name)
        _nth_table.pop(sc_name)
# =============================================================================

    def del_scenario_callback():
        div_spinner.text = load_text
        sc_name = scenario_dict[scenario_paramters[0]]["tools"]["sc_select"].value
        
        del_scenario(sc_name)
        
        options = list(scenario_mapper)
        if not options:
            scenario_button.active = False
            div_spinner.text = notify("All scenarios deleted", "red") 
        else:
            sc_new = options[0]
            # fires load_scenario_callback
            for _,dictt in scenario_dict.items():
                dictt["tools"]["sc_select"].options = options
                dictt["tools"]["sc_select"].value = sc_new
            div_spinner.text =  notify(f"""Scenario "{sc_name}" was delted""", "red") 
# =============================================================================
            
    def add_sub_scenarios(sc_name,sub_sc_name):
        heat_generator_table[sc_name][sub_sc_name] = pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore').fillna(0)
        heat_storage_table[sc_name][sub_sc_name] = pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore').fillna(0)
        carrier_table[sc_name][sub_sc_name] = pd.DataFrame(carrier_dict,index=[0]).T.to_dict()[0]
        paramters_table[sc_name][sub_sc_name] = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore').fillna(0)
        price_emmission_factor_table[sc_name][sub_sc_name] = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore').fillna(0)
        for wk in widgets_keys:
            profiles_table[wk][sc_name][sub_sc_name] = dict(zip(range(1,len(widgets[wk]["source"].data["y"])+1),widgets[wk]["source"].data["y"]))               
        external_data_table[sc_name][sub_sc_name] = pd.DataFrame(external_data).to_dict()
        external_data_map_table[sc_name][sub_sc_name] = pd.DataFrame(external_data_map).to_dict()   
        if scenario_mapper[sc_name]:
            scenario_mapper[sc_name].append(sub_sc_name)
        else:
            scenario_mapper[sc_name] = [sub_sc_name]
        _nth_table[sc_name][sub_sc_name]  = _nth
# =============================================================================
        
    def repace_name_of_sub_scenario(sc_name,sub_sc_name_old,sub_sc_name_new):
        heat_generator_table[sc_name][sub_sc_name_new] = heat_generator_table[sc_name].pop(sub_sc_name_old)
        heat_storage_table[sc_name][sub_sc_name_new] = heat_storage_table[sc_name].pop(sub_sc_name_old)
        carrier_table[sc_name][sub_sc_name_new] = carrier_table[sc_name].pop(sub_sc_name_old)
        paramters_table[sc_name][sub_sc_name_new] = paramters_table[sc_name].pop(sub_sc_name_old)
        price_emmission_factor_table[sc_name][sub_sc_name_new] = price_emmission_factor_table[sc_name].pop(sub_sc_name_old)
        for wk in widgets_keys:
            profiles_table[wk][sc_name][sub_sc_name_new] = profiles_table[wk][sc_name].pop(sub_sc_name_old)
        external_data_table[sc_name][sub_sc_name_new] = external_data_table[sc_name].pop(sub_sc_name_old)
        external_data_map_table[sc_name][sub_sc_name_new] = external_data_map_table[sc_name].pop(sub_sc_name_old) 
        scenario_mapper[sc_name] = [sub_sc_name_new if x==sub_sc_name_old else x for x in scenario_mapper[sc_name]]
        _nth_table[sc_name][sub_sc_name_new] = _nth_table[sc_name].pop(sub_sc_name_old)
# =============================================================================
        
    def add_sub_scenario_callback(sc_param):
        div_spinner.text = load_text
        sc_name = scenario_dict[sc_param]["tools"]["sc_select"].value
        sub_sc_name = scenario_dict[sc_param]["tools"]["sub_sc_text"].value.strip()  
        ### Check if name is alradey given
        if sub_sc_name in scenario_mapper[sc_name]:
            div_spinner.text = notify(f""" The sub scenario name "{sub_sc_name}" is already taken in scenario {sc_name}, please choose another name """, "red")         
            return None
        
        if sub_sc_name == "":
            div_spinner.text = notify(f"Error: Please define a name for your sub scenario !", "red") 
        elif sub_sc_name in scenario_mapper[sc_name]:
            div_spinner.text = notify(f""" Error: The name "{sub_sc_name}" is already given please define another""", "red") 
        else:
            add_sub_scenarios(sc_name,sub_sc_name)
            # fires load_scenario_callback
            for sc_p in scenario_paramters[:]:
                scenario_dict[sc_p]["tools"]["sub_sc_select"].options = scenario_mapper[sc_name] 
                scenario_dict[sc_p]["tools"]["sub_sc_select"].value = sub_sc_name
            
            div_spinner.text = notify(f""" In scenario "{sc_name}" the sub scenario "{sub_sc_name}" was successfully added """, "green")         
# =============================================================================
            
    def apply_sub_scenario_callback(sc_param):
        div_spinner.text = load_text
        sc_name = scenario_dict[sc_param]["tools"]["sc_select"].value
        sub_sc_name_new = scenario_dict[sc_param]["tools"]["sub_sc_text"].value.strip()
        sub_sc_name_old = scenario_dict[sc_param]["tools"]["sub_sc_select"].value
        ### Check if new name is alradey given
        if sub_sc_name_new in scenario_mapper[sc_name]:
            div_spinner.text = notify(f""" Can not rename sub scenario "{sub_sc_name_old}" to  "{sub_sc_name_new}" because it is already taken in scenario {sc_name}, please choose another name """, "red")         
            return None
        ### Change name of sub scenario
        if sub_sc_name_new != "" and sub_sc_name_new != sub_sc_name_old :
            repace_name_of_sub_scenario(sc_name,sub_sc_name_old,sub_sc_name_new)
        else:
            sub_sc_name_new = sub_sc_name_old
            
        if sc_param == scenario_paramters[0]:
            heat_generator_table[sc_name][sub_sc_name_new] = pd.DataFrame(data_table.source.data)[input_list+["type"]].apply(pd.to_numeric, errors='ignore').fillna(0)
            heat_storage_table[sc_name][sub_sc_name_new] = pd.DataFrame(data_table_heat_storage.source.data)[list(heat_storage_list_mapper)].apply(pd.to_numeric, errors='ignore').fillna(0)
            carrier_table[sc_name][sub_sc_name_new] = pd.DataFrame(carrier_dict,index=[0]).T.to_dict()[0]
        elif sc_param == scenario_paramters[1]:
            paramters_table[sc_name][sub_sc_name_new] = pd.DataFrame(data_table_data.source.data)[parameter_list].apply(pd.to_numeric, errors='ignore').fillna(0)
        elif sc_param == scenario_paramters[2]:
            price_emmission_factor_table[sc_name][sub_sc_name_new] = pd.DataFrame(data_table_prices.source.data)[input_price_list].apply(pd.to_numeric, errors='ignore').fillna(0)
        elif sc_param in widgets_keys:
            profiles_table[sc_param][sc_name][sub_sc_name_new] = dict(zip(range(1,len(widgets[sc_param]["source"].data["y"])+1),widgets[sc_param]["source"].data["y"]))               
            external_data_table[sc_name][sub_sc_name_new] = pd.DataFrame(external_data).to_dict()
            external_data_map_table[sc_name][sub_sc_name_new] = pd.DataFrame(external_data_map).to_dict()             
        #XXX: need extra apply button for custom _nth
        _nth_table[sc_name][sub_sc_name_new] = _nth
        
        # fires load_scenario_callback
        for sc_p in scenario_paramters[:]:
            scenario_dict[sc_p]["tools"]["sub_sc_select"].options = scenario_mapper[sc_name] 
            scenario_dict[sc_p]["tools"]["sub_sc_select"].value = sub_sc_name_new    

        div_spinner.text = notify(f""" Successfully applied changes to "{sc_param}" in scenario "{sc_name}" for sub scenario "{sub_sc_name_new}" """, "blue")         
# =============================================================================

    def del_sub_scenario(sc_name,sub_sc_name):
        heat_generator_table[sc_name].pop(sub_sc_name)
        heat_storage_table[sc_name].pop(sub_sc_name)
        carrier_table[sc_name].pop(sub_sc_name)       
        paramters_table[sc_name].pop(sub_sc_name)
        price_emmission_factor_table[sc_name].pop(sub_sc_name)
        for wk in widgets_keys:
            profiles_table[wk][sc_name].pop(sub_sc_name)
        external_data_table[sc_name].pop(sub_sc_name)
        external_data_map_table[sc_name].pop(sub_sc_name)           
        scenario_mapper[sc_name] = [x for x in scenario_mapper[sc_name] if x !=sub_sc_name]
        _nth_table[sc_name].pop(sub_sc_name)
# =============================================================================
        
    def del_sub_scenario_callback(sc_param):
        div_spinner.text = load_text
        sc_name = scenario_dict[sc_param]["tools"]["sc_select"].value
        sub_sc_name= scenario_dict[sc_param]["tools"]["sub_sc_select"].value
        
        del_sub_scenario(sc_name,sub_sc_name)
        
        notify_text = f"""In scenario "{sc_name}"  the sub scenario "{sub_sc_name}" was delted"""
        if not scenario_mapper[sc_name]:
            notify_text = f"""All sub scenarios in scenario "{sc_name}" deleted"""
            add_sub_scenarios(sc_name,"default_sub")
            
        sub_sc_new = scenario_mapper[sc_name][0]
        # fires load_scenario_callback
        for sc_p in scenario_paramters[:]:
            scenario_dict[sc_p]["tools"]["sub_sc_select"].options = scenario_mapper[sc_name]
            scenario_dict[sc_p]["tools"]["sub_sc_select"].value = sub_sc_new
        if scenario_button.active:
            div_spinner.text =  notify(notify_text, "red")   
# =============================================================================
            
    def load_scenario_callback(name,old,new,sc_param):
        sc = scenario_dict[sc_param]["tools"]["sc_select"].value
        sub_sc = scenario_dict[sc_param]["tools"]["sub_sc_select"].value 

        scenario_dict[sc_param]["tools"]["sub_sc_select"].options = scenario_mapper[sc]
        if sub_sc not in scenario_mapper[sc]:
            scenario_dict[sc_param]["tools"]["sub_sc_select"].value = scenario_mapper[sc][0]           
            sub_sc = scenario_dict[sc_param]["tools"]["sub_sc_select"].value      
        if sc_param in [scenario_paramters[0]] + _elec:
            scenario_dict[scenario_paramters[0]]["tools"]["sc_select"].value = sc
            data_table.source.data = df2data(heat_generator_table[sc][sub_sc])
            data_table_heat_storage.source.data = df2data(heat_storage_table[sc][sub_sc])
          
        if sc_param == scenario_paramters[1]:
            data_table_data.source.data = df2data(paramters_table[sc][sub_sc])

        if sc_param == scenario_paramters[2]:
            data_table_prices.source.data = df2data(price_emmission_factor_table[sc][sub_sc])

        if sc_param in widgets_keys:
            ## XXX: callbacks take very long
            (c,y),fit_string = extract(external_data_map_table[sc][sub_sc][sc_param]["Default"])
            offset,constant = find_FiT(fit_string)
            constant = "" if type(constant) == str else constant
            widgets[sc_param]["select"].value = data_kwargs[sc_param]["dic"][c]+"_"+str(y)
            widgets[sc_param]["offset"].value = str(offset)
            widgets[sc_param]["constant"].value = str(constant)  
        

# =============================================================================
#   Signal Emitting / Coupling for Scenario Mode
# =============================================================================
    scenario_button.on_click(scenario_mode_callback)
    scenario_dict[scenario_paramters[0]]["tools"]["sc_add"].on_click(add_scenario_callback)
    scenario_dict[scenario_paramters[0]]["tools"]["sc_apply"].on_click(apply_scenario_callback)
    scenario_dict[scenario_paramters[0]]["tools"]["sc_del"].on_click(del_scenario_callback)

    for sc_p in scenario_paramters[:]:
        scenario_dict[sc_p]["tools"]["sub_sc_add"].on_click(partial(add_sub_scenario_callback, sc_param = sc_p))
        scenario_dict[sc_p]["tools"]["sub_sc_apply"].on_click(partial(apply_sub_scenario_callback, sc_param = sc_p))
        scenario_dict[sc_p]["tools"]["sub_sc_del"].on_click(partial(del_sub_scenario_callback, sc_param = sc_p))
        scenario_dict[sc_p]["tools"]["sub_sc_select"].on_change("value",partial(load_scenario_callback,sc_param=sc_p))
        scenario_dict[sc_p]["tools"]["sc_select"].on_change("value",partial(load_scenario_callback,sc_param=sc_p))
    
    
#%%  Global Layout
# =============================================================================
#   Set Global Layout
# =============================================================================
    from imageHTML import header_html
    header = widgetbox(Div(text= header_html))
    grid.tabs = [Panel(child=hg_layout, title="Add Heat Generators"),
                 Panel(child=hs_layout, title="Add Heat Storages")]
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
                    [row([column([download_button,upload_button,run_button,
                               reset_button,invest_button,scenario_button]),
                     widgetbox(div_spinner,width=500),column([pmax,to_install])])],
                   [widgetbox(dummy,div,div2)],
                   [widgetbox(output,width=1500)],
                   [grid],
                   [widgetbox(tabs,width=1500)],
            ],sizing_mode='scale_width')
    
    doc.title="Dispatch Model"
    doc.add_root(l)
    
    
    return doc
#%% PYTHON MAIN
if __name__ == '__main__':

    
    allow_websocket_origin=None
    f_allow_websocket_origin = os.path.join(root_dir, 'allow_websocket_origin.txt')
    if os.path.exists(f_allow_websocket_origin):
        with open(f_allow_websocket_origin) as fd:
            allow_websocket_origin = [line.strip() for line in fd.readlines()]
            
    bokeh_app = Application(FunctionHandler(modify_doc))
    bokeh_app_2 = Application(DirectoryHandler(filename = path2data)) #FIXME: for downloading files
    
# =============================================================================
#     tornado multi process  #FIXME: only for Linux
# =============================================================================
    try:
        # 0: auto, chooses number of cpu cores
        # 4: starts 4 processes
        num_procs = 0
        server = Server({'/': bokeh_app, '/download':bokeh_app_2}, 
                        num_procs=num_procs, 
                        allow_websocket_origin=allow_websocket_origin)
        server.start()
        server.io_loop.start()
# =============================================================================
#     
# =============================================================================
    except:
        print("Start single Thread...")
        io_loop = IOLoop.current()
        server = Server({'/': bokeh_app, '/download':bokeh_app_2}, io_loop=io_loop, 
                        allow_websocket_origin=allow_websocket_origin)
        server.start() 
# =============================================================================
# 
# =============================================================================
    print('Open Dispath Application on http://localhost:5006/')
    
    #FIXME:  Error while starting server via sypder-ide
    try:
        io_loop.start()
    except:
        pass

