# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 18:51:21 2018

@author: root
"""
demand_f = 1
#%%
import pickle
import numpy as np
import json
import matplotlib.pylab as plt
from matplotlib.colors import to_hex
from bokeh.plotting import figure, show, output_file,save
from bokeh.models import ColumnDataSource,Legend,LinearAxis, Range1d,Label,LabelSet, DataTable, DateFormatter, TableColumn,CustomJS
from bokeh.layouts import widgetbox, gridplot,column,row
from bokeh.models.widgets import Panel, Tabs, Button
import os
import itertools
from math import pi
#%%
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
#%%
def colormapping(tec):
    colors = get_cmap(len(tec))
    color_map = {val:to_hex(colors(i)) for i,val in enumerate(tec)}
    return color_map
#%%
def matrix(dic,decison_var,legend,t):
    y = np.array(dic[decison_var][legend[0]])[t]
    for val_ind in legend[1:]:
        y=np.row_stack((y,np.array(dic[decison_var][val_ind])[t]))
    if len(y.shape) == 1:
        y=y.reshape((1,y.shape[0]))
    return y 
#%%
def create_patch_coordinates(sorted_values,t):
    area = np.zeros(sorted_values.shape)
    for i,y in enumerate(sorted_values):
        if i!=0:
            area[i]=area[i-1,:]+y
        else:
            area[i]=y
    
    front = np.append(np.array([0]),area[:-1,0]).reshape(area.shape[0],1)
    back = np.append(np.array([0]),area[:-1,-1]).reshape(area.shape[0],1)
    area = np.hstack((front,area,back))
    t = list(t)
    t.insert(0,t[0])
    t.append(t[-1])
    
    x = [t for _ in range(area.shape[0])]
    y = [list(y) for y in area]
    
    y_extended = y[:]
    x_extended = x[:]
    for i in range(len(y)):
        if  i!=0:
            y_extended[i] = y[i] + list(reversed(y[i-1]))[2:-1]
            x_extended[i] = x[i] + list(reversed(x[i-1]))[2:-1]
        else:
            y_extended[i] = y[i]
            x_extended[i] = x[i]
            
    return x_extended,y_extended
#%%
def stack_chart(t,dic,y,legend,decison_var,path2output,cmap,flag=0):
    name = "_over_year.html"
    if flag =="s":
        name= "_summer.html"
    if flag == "w":
        name= "_winter.html"
    p = figure(title = decison_var+" ".join(name.split(".")[0].split("_")), 
               x_axis_label = "Time in Hours",
               y_axis_label = "MWh_th",
               tools = "pan,wheel_zoom,box_zoom,hover,reset,save",
               toolbar_sticky = False)
    p.grid.minor_grid_line_color = '#eeeeee'
    
    line = p.line(t,list(demand_f*np.array(dic["Heat Demand"])[t]),color="black",line_width=0.5,muted_alpha=0.2)
    null = [i for i,x in enumerate(range(y.shape[0])) if np.sum(y[x,:]) !=0]
    mc_mask=np.argsort(np.array(dic["Marginal Costs"])[null])
    legend = np.array(legend)[null][mc_mask].tolist()
    colors = [cmap[i] for i in legend]
    sorted_values = y[null][mc_mask]
    
    x,y = create_patch_coordinates(sorted_values,t)
    
    areas = [p.patch(xy[0],xy[1],color=colors[i], alpha=0.8, line_color=None,muted_alpha=0.2) for i,xy in enumerate(zip(x,y)) ]
    
    electricity = np.array(dic["Electricity Price"])[t]
    
    heat_p = np.array(dic["Heat Price"])[t]
#    p.extra_y_ranges = {"2nd": Range1d(start=min(electricity)-1, end=max(electricity)+1)}
#    line2 = p.line(t,list(electricity),color="blue",line_width=0.5,y_range_name="2nd",muted_alpha=0.2)
#    line3 = p.line(t,list(heat_p),color="green",line_width=0.5,y_range_name="2nd",muted_alpha=0.2)
#    p.add_layout(LinearAxis(y_range_name="2nd",axis_label='price in €/MWh'), 'right')
    items = [("Heat Demand",   [line] )]
#             ("Electricity Price",   [line2] ),
#             ("Heat Price",   [line3] )]
    for label,glyph in zip(legend,areas):
        items.append((label,[glyph]))
    legend = Legend(items=items,location=(10, 10))
    
    p.add_layout(legend, 'right')   
    p.legend.click_policy = "hide" # "mute"
    output_file(path2output+r"\\"+decison_var+name)
    p.toolbar.logo = None
#    save(p)
    
    p2 = figure(x_range=p.x_range,title="Electricity Price",
                x_axis_label = "Time in Hours",
                y_axis_label = "€/MWh",)
    line2 = p2.line(t,list(electricity),color="blue",line_width=0.5,muted_alpha=0.2)
    p2.toolbar.logo = None
    p2.grid.minor_grid_line_color = '#eeeeee'
    p3 = figure(x_range=p.x_range,y_range=(np.min(heat_p)-1,np.percentile(heat_p, 90)+1),title="Heat Price",
                x_axis_label = "Time in Hours",
                y_axis_label = "€/MWh_th",)
    line3 = p3.line(t,list(heat_p),color="red",line_width=0.5,muted_alpha=0.2)
    p3.toolbar.logo = None
    p3.grid.minor_grid_line_color = '#eeeeee'
#    s = column(p, p2, p3)
    s = gridplot([[p],[p2],[p3]],plot_width=1000, plot_height=300,
                 toolbar_options=dict(logo=None))
#    s.toolbar.logo = None
#    save(s)
    return s
#%%
def load_duration_curve(t,dic,y,legend,decison_var,path2output,cmap):
    p = figure(title = "Load Duration Curve", 
           x_axis_label = "Time in Hours",
           y_axis_label = "MWh_th",
           tools = "pan,wheel_zoom,box_zoom,reset,save",
           toolbar_sticky = False,
           plot_width=1000, 
           plot_height=500)
    p.grid.minor_grid_line_color = '#eeeeee'
    summe = np.sum(y,0)
    idx = np.argsort(-summe)
    dauerkurve = y[:,idx]
    line = p.line(t,summe[idx],color="black",line_width=0.5,muted_alpha=0.2)
    null = [i for i,x in enumerate(range(y.shape[0])) if np.sum(y[x,:]) !=0]
    mc_mask=np.argsort(np.array(dic["Marginal Costs"])[null])
    legend = np.array(legend)[null][mc_mask].tolist()
    colors = [cmap[i] for i in legend]
    x,y = create_patch_coordinates(dauerkurve[null][mc_mask],t)
    areas = [p.patch(xy[0],xy[1],color=colors[i], alpha=0.8, line_color=None,muted_alpha=0.2) for i,xy in enumerate(zip(x,y)) ]
    items = [("Load Duration Curve",   [line] )]
    for name,glyph in zip(legend,areas):
        items.append((name,[glyph]))
        
    legend = Legend(items=items,location=(10, 10))
    
    p.add_layout(legend, 'right')
    p.legend.click_policy = "hide" # "mute"
#    p.legend.location = "top_left"
    output_file(path2output+r"\\load_duration_curve.html")
    p.toolbar.logo = None
#    save(p)
    return p
#%%
def pie_chart(dic,path2output,decison_var,cmap): 
    p = figure(title = decison_var,
       plot_width=700, 
       plot_height=400)
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.toolbar.logo = None
    p.toolbar_location = None
    
    labels = list(dic)
    sizes = np.array(list(dic.values()))/sum(dic.values())
    mask = sizes>0
    labels = list(itertools.compress(labels, mask))
    sizes_cum = np.cumsum(sizes[mask]*2*pi)
    explode = 0/180*pi
    x=300
    y=300 
    radius=150
    colors = [cmap[i] for i in labels]   
    start_angle= [0]+list(sizes_cum)[0:-1]   
    end_angle=list(sizes_cum-explode)
    wedges = [ p.wedge(x=x,y=y, radius=radius, start_angle= start_angle[i],
               end_angle=end_angle[i], radius_units="screen", color=colors[i],muted_alpha=0.2) 
            for i in range(len(colors))]
    text=list(np.round(sizes[mask]*100,2))
    items = []
    for name,glyph,percentage in zip(labels,wedges,text):
        items.append((name+": "+str(percentage)+"%",[glyph]))
    legend = Legend(items=items,location=(10, 10))    
    p.add_layout(legend, 'right')
    p.legend.click_policy = "hide" # "mute"
    output_file(path2output+r"\\"+decison_var+"_pie_chart.html")
#    save(p)
    return p
#%%
def bar_chart(dic,path2output,decison_var,cmap):
    p = figure(title = decison_var,
           plot_width=700, 
           plot_height=400,
           tools = "pan,wheel_zoom,box_zoom,reset,save")
    p.xaxis.visible = False
    p.xgrid.visible = False
    p.grid.minor_grid_line_color = '#eeeeee'
    p.toolbar.logo = None
    p.toolbar_location = None
    legend = list(dic)
    val = list(dic.values())
    k = [i for i,x in enumerate(val) if x!=0]
    legend= [legend[i] for i in k]
    val= [val[i] for i in k]
    colors = [cmap[i] for i in legend]
    bars = [p.rect(x=5+i*15, y=val[i]/2, width=10, height=val[i], color=colors[i],muted_alpha=0.2) for i in range(len(val))]
    text=list(np.round(val,2))
    items = []
    for name,glyph,label in zip(legend,bars,text):
        items.append((name+": "+str(label)+"",[glyph]))
    legend = Legend(items=items,location=(10, 10))    
    p.add_layout(legend, 'right')
    p.legend.click_policy = "mute" # "mute"
    output_file(path2output+r"\\"+decison_var+"_absolut_bar_chart.html")
#    save(p)
    return p
#%%
def plot_table (decision_vars,dic,path2output):   
    val = [str(round(dic[decison_var],2)) for decison_var in decision_vars]
    data = dict(
            topic = decision_vars,
            value = val,
        )
    source = ColumnDataSource(data)
    columns = [
            TableColumn(field="topic", title="Topic"),
            TableColumn(field="value", title="Value"),
        ]
    data_table = DataTable(source=source, columns=columns, width=800, height=800)
    output_file(path2output+"\data_table.html") 
#    save(widgetbox(data_table))
    return widgetbox(data_table)
#%%
def tab_panes(path2output,**kwargs):
    output_file(path2output+"\output.html",title="Dispatch output")
    tabs = [Panel(child=p, title=name) for name, p in kwargs.items()]
    tabs = Tabs(tabs=tabs)
    save(tabs)
#%%
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
path2json = path+r"\AD\F16_input\Solution\solution.json"
path2output = path+r"\AD\F16_input\Output_Graphics"
#%%
def plot_solutions(path2json=path2json):
    
    try:
        with open(path2json) as f:
            dic = json.load(f)
        
        if os.path.isdir(path2output) == False:
            print("Create Dictionary...")
            cmap = colormapping(dic["Technologies"])
            os.mkdir(path2output)
            print("Created: "+ path2output)
            pickle.dump(cmap, 
                        open(path2output+r'\cmap.spec', 'wb'))

            
            
    except FileNotFoundError:
        print("\n*********\nThere is no JSON File in this path: "+
              path2json+"\n*********\n")
        return True
    
    decison_var="Thermal Power Energymix" 
    legend = list(dic["Thermal Power Energymix"].keys())
    tw = range(0,350)  
    ts = range(730*5,730*5+336+1)   
    t = range(0,8760)
    y1 = matrix(dic,decison_var,legend,tw)
    y2 = matrix(dic,decison_var,legend,ts)
    y3 = matrix(dic,decison_var,legend,t)
#    cmap = colormapping(dic["Technologies"])
    cmap = pickle.load(open(path2output+r"\cmap.spec", "rb"))
    p1 = stack_chart(tw,dic,y1,legend,decison_var,path2output,cmap,"w")
    p2 = stack_chart(ts,dic,y2,legend,decison_var,path2output,cmap,"s")
    p3 = stack_chart(t,dic,y3,legend,decison_var,path2output,cmap)    
    p4 = load_duration_curve(t,dic,y3,legend,decison_var,path2output,cmap)    
    decison_var = "Thermal Generation Mix"
    p5 = pie_chart(dic[decison_var],path2output,decison_var,cmap)
    decison_var = "Installed Capacities"
    p6 = pie_chart(dic[decison_var],path2output,decison_var,cmap)
    p7 = bar_chart(dic[decison_var],path2output,decison_var,cmap)
    decison_var = "Specific Capital Costs of installed Capacities"
    p8 = bar_chart(dic[decison_var],path2output,decison_var,cmap)
    decision_vars = ["Electricity Production by CHP",
                     "Thermal Production by CHP",
                     "Mean Value Heat Price",
                     "Median Value Heat Price",
                     "Electrical Consumption of Heatpumps and Power to Heat devices",
                     "Maximum Electrical Load of Heatpumps and Power to Heat devices",
                     "Revenue From Electricity",
                     "Ramping Costs",
                     "Operational Cost",
                     "Invesment Cost",
                     "Electrical Peak Load Costs",
                     "Variable Cost CHP's",
                     "Total Variable Cost",
                     "Total Costs"]
    p9 = plot_table(decision_vars,dic,path2output)
    
    kwargs = {"Thermal Power Energymix (TPE)": p3,
              "TPE Winter": p1,
              "TPE Summer": p2,
              "Load Duration Curve": p4,
              "TPE percentage":p5,
              "Installed Capacities (IC) percentage": p6,
              "IC absolute": p7,
              "Specific Capital Costs of IC":p8,
              "Results":p9}
    tab_panes(path2output,**kwargs)
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
#plot_solutions()            
import pandas as pd
data = pd.read_excel(r"C:\Users\Nesa\Desktop\input.xlsx")
col = [TableColumn(field=name, title=name) for name in list(data) if name in input_list]
source = ColumnDataSource(data)
data_table = DataTable(source=source,columns=col,width=1150, height=800,editable=True)
output_file(r"C:\Users\Nesa\Desktop\data_table.html") 

code=open(r"C:\Users\Nesa\Desktop\Arbeit EEG\Hotmaps\Dispatch\app\modules\common\CM\CM_TUWdispatch\download.js").read()
callback = CustomJS(args=dict(source=source), code=code)
button = Button(label='Download', button_type='success', callback=callback)
save (widgetbox(button,data_table))      
#data = pd.read_csv(r"C:\Users\Nesa\Downloads\input.csv")