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
import pandas as pd
import matplotlib.pylab as plt
from matplotlib.colors import to_hex
from bokeh.plotting import figure, show, output_file,save
from bokeh.models import ColumnDataSource,Legend, DataTable,TableColumn
from bokeh.layouts import widgetbox, gridplot, layout
from bokeh.models.widgets import Panel, Tabs
from bokeh.core.properties import value
import os
import itertools
from math import pi
import sys

#%%
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

#%%
from CM.CM_TUWdispatch.eng_format import EngNumber,EngUnit

#%%
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
#%%
def colormapping(tec):
    """
    This function returns a dictionary whoes keys are the name of the tec-list
    and its entries are colors specified in HEX format
    Default colors are from matplotlibs "tab20" colormaps.

    Parameters:
        tec:    list
                list entries are keys of colormap
    Returns:
        colormap:   dict
                    This will be the dictionary each tec entry is associated
                    with a HEX-color
    Example:
        colormapping( ["a",1,"b",2] )
        returns:
            {1: '#d62728', 2: '#9edae5', 'a': '#1f77b4', 'b': '#f7b6d2'}
    """
    colors = get_cmap(len(tec))
    color_map = {val:to_hex(colors(i)) for i,val in enumerate(tec)}
    return color_map
#%%
def matrix(dic,decison_var,legend,t):
    """
    This function return a matrix (numpy array) that contains the data from
    the dic[decison_var], each row of the matrix represent the data from a list
    entry of legend (i.e. Technology).

    Parameters:
        dic:            dict
                        Dictionary which contains the solution from the model

        decison_var:    string
                        Decciosn variable that should be analyzed from the
                        solution

        legend:         list  (N)-length
                        contains the list of technologies:

        t:              list (T)-length
                        contains a list of integer, represent a time view
                        matrix show the data of this time interval
    Returns:
        matrix:     numpy_array  (N,T)-shape
    """
    y = np.array(dic[decison_var][legend[0]])[t]
    for val_ind in legend[1:]:
        y=np.row_stack((y,np.array(dic[decison_var][val_ind])[t]))
    if len(y.shape) == 1:
        y=y.reshape((1,y.shape[0]))
    return y
#%%
def create_patch_coordinates(sorted_values,t):
    """
    This function returns two lists (x and y).
    The lists contain the coordinates for the polygons to draw the stackplot.

    Parameters:
        sorted_values:      numpy_array (N,T)-shape
                            sorted matrix by marginal costs of the technologies


        t:                  range (T)-legth
                            This represent the time w

    Results:
        x_extended:         list (N,t)-legth
                            This contains a list of N-lists ,
                            each list represent the x coordinates of N-th polygon
                            and has T-entries



        y_extended:         list (N,t)-legth
                            This contains a list of N-lists ,
                            each list represent the y coordinates of N-th polygon
                            and has T-entries
    """
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
    """
    This function returns a bokeh gridplot, with three collumns.

    -   The first column contains a bokeh figure of the Thermal Generation Mix
        It is represented by a stackplot, that is sorted by the marginal costs
        of the technologies
        This figure has also an interactive legend.
        i.e: by clicking you can hide or show the lines and areas

    -   The second column contains a bokeh figure of the electricity price
        represented by a line

    -   The third column contains a bokeh figure of the heat price
        represented by a line

    All figures share the same x-axes, i.e: zooming the x-axes of one figure
                                            effects also the other figures

    Parameters:
        t:              range
                        change this paramter to change the time view that the
                        figure show
                        i.e.: slices in the interval [0,8760] can be selected

        dic:            dict
                        Dictionary that contains the solution of the model

        y:              numpy_array  (N,T)-shape
                        This contain the data that will represented by the first
                        collumn as a stackplot

        legend:         list
                        This contains a list of the names of the technologies

        decison_var:    string
                        Decciosn variable that should be analyzed from the
                        solution

        path2output:    string
                        path where the gridplot should be saved (obsolete)

        cmap:           dict
                        colormaping table to assign each techology (entry of legend)
                        to a color

        flag:           string
                        a file name for the output plot (obsolete)
                        "s"..."_summer.html"
                        "w"..."_winter.html"
                        else "_over_year.html"
    Returns:
        gridplot:       bokeh.layouts.gridplot
    """
    name = "_over_year.html"
    if flag =="s":
        name= "_summer.html"
    if flag == "w":
        name= "_winter.html"
    p = figure(title = decison_var+" ".join(name.split(".")[0].split("_")),
               x_axis_label = "Time in Hours",
               y_axis_label = "MWh_th",
               tools = "pan,wheel_zoom,box_zoom,reset,save",
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
    items = [("Heat Demand",   [line] )]
    for label,glyph in zip(legend,areas):
        items.append((label,[glyph]))


    flag = False
    try:
        for hs in dic["Heat Storage Technologies"]:
            if sum(np.array(dic["Loading Heat Storage"][hs])[t]) != 0:
                flag = True
                loading = p.patch( [t[0]] + list(t) + [t[-1]],
                              [0] + (np.array(dic["Loading Heat Storage"][hs])*-1)[t].tolist() + [0]
                              ,color="#EF7B7B",line_color=None,muted_alpha=0.2)
                items.append(("Loading-"+hs,[loading]))

                p4 = figure(x_range=p.x_range,title="Heat Storages",
                x_axis_label = "Time in Hours",
                y_axis_label = "MWh_th")
                p4.toolbar.logo = None
                p4.grid.minor_grid_line_color = '#eeeeee'
                items4 = []

                level = p4.line( list(t),np.array(dic["State of Charge"][hs])[t].tolist(),color=cmap[hs],muted_alpha=0.2)
                items4.append(("Level-"+hs,[level]))

                load = p4.line( list(t),np.array(dic["Loading Heat Storage"][hs])[t].tolist(),color="green",muted_alpha=0.2)
                items4.append(("Load-"+hs,[load]))

                unload = p4.line( list(t),np.array(dic["Unloading Heat Storage"][hs])[t].tolist(),color="blue",muted_alpha=0.2)
                items4.append(("Unload-"+hs,[unload]))

                level.visible  = True
                load.visible = False
                unload.visible = False
                legend4 = Legend(items=items4,location=(10, 10))

                p4.add_layout(legend4, 'right')
                p4.legend.click_policy = "hide" # "mute"
    except:
        pass

    legend = Legend(items=items,location=(10, 10))

    p.add_layout(legend, 'right')
    p.legend.click_policy = "hide" # "mute"
#    output_file(path2output+r"\\"+decison_var+name)
    p.toolbar.logo = None

    p2 = figure(x_range=p.x_range,title="Electricity Price",
                x_axis_label = "Time in Hours",
                y_axis_label = "€/MWh",)
    line2 = p2.line(t,list(electricity),color="#2171b5",line_width=0.5,muted_alpha=0.2)
    p2.toolbar.logo = None
    p2.grid.minor_grid_line_color = '#eeeeee'
    p3 = figure(x_range=p.x_range,y_range=(np.min(heat_p)-1,np.percentile(heat_p, 90)+1),title="Heat Price",
                x_axis_label = "Time in Hours",
                y_axis_label = "€/MWh_th",)
    line3 = p3.line(t,list(heat_p),color="#cb181d",line_width=0.5,muted_alpha=0.2)
    p3.toolbar.logo = None
    p3.grid.minor_grid_line_color = '#eeeeee'
    if flag:
        s = gridplot([[p],[p2],[p3],[p4]],plot_width=1000, plot_height=300,
                 toolbar_options=dict(logo=None))
    else:
        s = gridplot([[p],[p2],[p3]],plot_width=1000, plot_height=300,
                 toolbar_options=dict(logo=None))
    return s,p
#%%
def load_duration_curve(t,dic,y,legend,decison_var,path2output,cmap):
    """
    This function returns a bokeh figure with the load duration curve
    (areas are sorted by marginal costs).
    This figure has also an interactive legend.
    i.e: by clicking you can hide or show the areas of the clicked technologies

    Parameters:
        t:              range
                        change this paramter to change the time view that the
                        figure show
                        i.e.: slices in the interval [0,8760] can be selected

        dic:            dict
                        Dictionary that contains the solution of the model

        y:              numpy_array  (N,T)-shape
                        This contain the data that will represented by the first
                        collumn as a stackplot

        legend:         list
                        This contains a list of the names of the technologies

        decison_var:    string
                        Decciosn variable that should be analyzed from the
                        solution

        path2output:    string
                        path where the figure should be saved (obsolete)

        cmap:           dict
                        colormaping table to assign each techology (entry of legend)
                        to a color
    Returns:
        figure:       bokeh.plotting.figure
    """
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
    p.toolbar.logo = None
    return p
#%%
def pie_chart(dic,path2output,decison_var,cmap):
    """
    This function returns a bokeh figure that shows the data from dic as a pie
    chart.This figure has also an interactive legend.
    i.e: by clicking you can hide or show the bars of the clicked technologies

    Parameters:
        dic:            dict
                        Dictionary that contains data that should be analyzed
                        from the solution of the model

        path2output:    string
                        path where the figure should be saved (obsolete)

        decison_var:    string
                        Title of the Plot
    Returns:
        pie_chart:      bokeh.plotting.figure
    """
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
#    output_file(path2output+r"\\"+decison_var+"_pie_chart.html")
    return p
#%%
def bar_chart(dic,path2output,decison_var,cmap):
    """
    This function returns a bokeh figure that shows the data from dic as a bar
    chart.This figure has also an interactive legend.
    i.e: by clicking you can hide or show the bars of the clicked technologies

    Parameters:
        dic:            dict
                        Dictionary that contains data that should be analyzed
                        from the solution of the model

        path2output:    string
                        path where the figure should be saved (obsolete)

        decison_var:    string
                        Title of the Plot

        cmap:           dict
                        colormaping table to assign each technology to a color
    Returns:
        bar_chart:      bokeh.plotting.figure
    """
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
#        items.append((name+": "+str(("%.3e"%float(label)))+"",[glyph]))
        items.append((name+": "+str(EngNumber(float(label)))+"",[glyph]))


    legend = Legend(items=items,location=(10, 10))
    p.add_layout(legend, 'right')
    p.legend.click_policy = "mute" # "mute"
    return p


def costBarStack_chart(dic,decison_vars,path2output,cmap):
    """
    This function returns a bokeh figure that shows the costs as a bar chart.
    Follwing costs are shown:
        - Anual Investment Cost
        - Anual Investment Cost (of existing power plants)
        - Operational Cost
        - Fuel Costs
        - Revenue From Electricity

    Parameters:
        dic:            dict
                        Dictionary that contains the solution of the model

        path2output:    string
                        path where the figure should be saved (obsolete)

        decison_var:    list
                        Each list entry is a decison variable that should be
                        analyzed from the solution

        cmap:           dict
                        colormaping table to assign each technology to a color
    Returns:
        bar chart:      bokeh.plotting.figure
    """
    data = {x: [dic["Anual Investment Cost:"][x]+dic["Anual Investment Cost (of existing power plants and heat storages)"][x],
                dic["Operational Cost:"][x],
                 dic["Fuel Costs:"][x],
                 -dic["Revenue From Electricity:"][x]] for x in dic["Technologies:"]}
    bars = decison_vars.copy()
    bars.pop(1)
    data["bars"] = bars

    p = figure(x_range=bars, plot_height=400, plot_width=900,
            tools = "pan,wheel_zoom,box_zoom,reset,save")
    p.xgrid.visible = False
    p.grid.minor_grid_line_color = '#eeeeee'
    p.toolbar.logo = None
    p.toolbar_location = None

    source = ColumnDataSource(data=data)

    p.vbar_stack(dic["Technologies:"], x='bars', width=0.9, color=[cmap[x] for x in dic["Technologies:"]],
                 source=source, legend=[value(x) for x in dic["Technologies:"]])

    p.legend.location = "top_right"
    p.legend.orientation = "vertical"

    new_legend = p.legend[0]
    p.legend[0].plot = None
    p.add_layout(new_legend, 'right')

    return p


#%%
def plot_table (decision_vars,dic,path2output):
    """
    This function returns a widgetbox that contains a table with some results
    defined in decision_vars

    Parameters:
        decison_var:        list
                            Each list entry is a decison variable that should
                            be analyzed from the solution

        dic:                dict
                            Dictionary that contains the solution of the model

        path2output:        string
                            path where the widgetbox should be saved (obsolete)

    Results:
        table:              bokeh.layouts.widgetbox
    """
    val = []
    for decision_var in decision_vars:
        if type(dic[decision_var]) == dict:
            val.append(sum(dic[decision_var].values()))
        elif type(dic[decision_var]) == list:
            val.append(sum(dic[decision_var]))
        else:
            val.append(dic[decision_var])
    try:
        formatted_val = [str(EngNumber(item)) for item in val]
    except:
        formatted_val = []
        for item in val:
            formatted_val.append("%.3e"%item)

    data = dict(
            topic = decision_vars,
            value = formatted_val,
        )
    source = ColumnDataSource(data)
    columns = [
            TableColumn(field="topic", title="Topic"),
            TableColumn(field="value", title="Value"),
        ]
    data_table = DataTable(source=source, columns=columns, width=800, height=800)
    return widgetbox(data_table)

def plotExtra_table (decision_vars,dic,path2output):
    """
    This function returns a widgetbox that contains a table with the costs of
    each technology

    Parameters:
        decison_var:        list
                            Each list entry is a decison variable that should
                            be analyzed from the solution

        dic:                dict
                            Dictionary that contains the solution of the model

        path2output:        string
                            path where the widgetbox should be saved (obsolete)

    Results:
        table:              bokeh.layouts.widgetbox
    """
    data = []
    line =[]
    for decision_var in decision_vars:
        if type(dic[decision_var]) == dict:
            formatted_val = []
            for item in list(dic[decision_var].values()):
#                formatted_val.append("%.3e"%item)
                formatted_val.append(str(EngNumber(item)))

            line = [[decision_var] + formatted_val]
            data = data + line
    source = ColumnDataSource(pd.DataFrame(data, columns=["topic"]+list(dic["Technologies:"])))

    column0 = [TableColumn(field="topic", title="Topic")]
    columns = [TableColumn(field=x, title=x) for x in dic["Technologies:"]]
    columns = column0+columns

    data_table = DataTable(source=source, columns=columns, width=800, height=200)
#    output_file(path2output+"\data_table.html")
    return widgetbox(data_table)

#%%
def tab_panes(path2output,**kwargs):
    """
    This function returns a Tabs-Panel that collects bokeh widgets,figures etc.

    Parameters:
        kwargs:             dict
                            {name of tab: content of tab}
                            This is a dictionary: each key is the name of
                            the tab that is shown and the value is a bokeh figure
                            bokeh widget or bokeh layout.

        path2output:        string
                            path where the tabs should be saved (obsolete)
    Results:
        Tabs:               bokeh.models.widgets.panels.Tabs
    """
    tabs = [Panel(child=p, title=name) for name, p in kwargs.items()]
    tabs = Tabs(tabs=tabs)
    return tabs

#%% Setting Global default paramters and default paths
path2json = os.path.join(path, "AD", "F16_input", "Solution", "solution.json")
path2output = os.path.join(path, "AD", "F16_input", "Output_Graphics")
path_parameter = os.path.join(path, "AD", "F16_input", "DH_technology_cost.xlsx")
#%%
def plot_solutions(show_plot=False,path2json=path2json,solution=-1):
    """
    This function geneartes a HTML file representeing the results of the model
    and saves it in "\AD\F16_input\Output_Graphics" as "output.html".

    If <show_plot> is True then the function shows the output in the browser.
    If <show_plot> is False then the function returns the tabs with the output.

    The output contains seven tabs:
        - Tab1:
            Name:       Thermal Power Energymix (TPE)
            Content:    Three rows with three bokeh glyphs. All figures share
                        the same x-axes, i.e: zooming the x-axes of one figure
                        effects also the other figures

                            - row1: a stackplot of the geneartion mix of the
                                    whole year t=[0 8760)
                                    This figure has also an interactive legend.
                                    i.e: by clicking you can hide or show the
                                          areas of the clicked technologies

                            - row2: a lineplot of the electricity price over
                                    a whole year t=[0 8760)

                            - row3: a lineplot of the heat price over
                                    a whole year t=[0 8760)
        - Tab2:
            Name:       TPE Winter
            Content:    Three rows with three bokeh glyphs. All figures share
                        the same x-axes, i.e: zooming the x-axes of one figure
                        effects also the other figures

                            - row1: a stackplot of the geneartion mix over a
                                    slected time horizon t=[0 350)
                                    This figure has also an interactive legend.
                                    i.e: by clicking you can hide or show the
                                          areas of the clicked technologies

                            - row2: a lineplot of the electricity price over
                                    slected time horizont=[0 350)

                            - row3: a lineplot of the heat price over
                                    slected time horizonr t=[0 350)
        - Tab3:
            Name:       TPE Summer
            Content:    Three rows with three bokeh glyphs. All figures share
                        the same x-axes, i.e: zooming the x-axes of one figure
                        effects also the other figures

                            - row1: a stackplot of the geneartion mix over a
                                    slected time horizon t=[3750 3987)
                                    This figure has also an interactive legend.
                                    i.e: by clicking you can hide or show the
                                          areas of the clicked technologies

                            - row2: a lineplot of the electricity price over
                                    slected time horizon t=[3750 3987)

                            - row3: a lineplot of the heat price over
                                    slected time horizonr t=[3750 3987)
        - Tab4:
            Name:       Load Duration Curve
            Content:    Shows the Load Duration Curve as a sorted (by marginal
                        costs) stackplot with an interactive legend
        - Tab5:
            Name:       TPE and Plant Capatcities
            Content:    shows the Thermal Generation Mix as a pie chart and bar
                        chart (first column) and  shows also the installed
                        capacities as a pie chart and bar chart (second column)
                        All figures have an interactive legend
        - Tab6:
            Name:       Specific Capital Costs of IC
            Content:    Shows a bar chart and an table of the costs for each
                        technology.Follwing costs are shown:
                            - Anual Investment Cost
                            - Anual Investment Cost (of existing power plants)
                            - Operational Cost
                            - Fuel Costs
                            - Revenue From Electricity
        - Tab7:
            Name:       Results
            Content:    Shows a table with specific results:
                            - Anual Total Costs
                            - Anual Total Costs (with costs of existing power
                                                   plants)
                            - Electricity Production by CHP
                            - Thermal Production by CHP
                            - Mean Value Heat Price
                            - Mean Value Heat Price (with costs of existing
                                                      power plants)
                            - Median Value Heat Price
                            - Electrical Consumption of Heatpumps and Power to
                              Heat devices
                            - Maximum Electrical Load of Heatpumps and Power to
                              Heat devices
                            - Revenue From Electricity
                            - Ramping Costs
                            - Operational Cost
                            - Anual Investment Cost
                            - Anual Investment Cost (of existing power plants)
                            - Electrical Peak Load Costs
                            - Variable Cost CHP's
                            - Fuel Costs

    Parameters:
        show_plot:      bool
                        determines if the function should show the output in
                        the broswer.
                            True... function returns nothing but shows the
                                    results(Tabs) in the browser
                            False...function returns the results(Tabs)

                        default:    False

        path2json:      string
                        Path to JSON-File that contain the solution of the model
                        default:    "\AD\F16_input\Solution\solution.json"
    Returns:
        results:       bokeh.models.widgets.panels.Tabs  if show_plot=False
                       < nothing  if show_plot=True >
                       < Error4 > if an error occure >
    """
    try:
        if solution == -1:
            try:
                with open(path2json) as f:
                    dic = json.load(f)
    
#                if os.path.isdir(path2output) == False:
#                    print("Create Dictionary...")
#                    cmap = colormapping(dic["all_heat_geneartors"])
#                    os.mkdir(path2output)
#                    print("Created: "+ path2output)
#                    with open(os.path.join(path2output,"cmap.spec"),"wb") as file:
#                        pickle.dump(cmap,file)
    
            except FileNotFoundError:
                print("\n*********\nThere is no JSON File in this path: "+
                      path2json+"\n*********\n")
                return True
        else:
            dic = solution

        decison_var="Thermal Power Energymix:"
        legend = list(dic[decison_var].keys())
        tw = range(730*1,730*1+336+1)
        ts = range(730*6,730*6+336+1)
        t = range(0,8760)
        y1 = matrix(dic,decison_var,legend,tw)
        y2 = matrix(dic,decison_var,legend,ts)
        y3 = matrix(dic,decison_var,legend,t)
        
#        try:
#            with open(os.path.join(path2output,"cmap.spec"),"rb") as file:
#                cmap = pickle.load(file)
#        except:
#            print("Create Dictionary...")
#            cmap = colormapping(dic["all_heat_geneartors"])
#            os.mkdir(path2output)
#            print("Created: "+ path2output)
#            with open(os.path.join(path2output,"cmap.spec"),"wb") as file:
#                pickle.dump(cmap,file)
#                
#    
#        cmap2 = colormapping(dic["Technologies:"])
#        if cmap != cmap2:
#            cmap = cmap2
#            with open(os.path.join(path2output,"cmap.spec"),"wb") as file:
#                pickle.dump(cmap,file)
        
        cmap = colormapping(dic["Technologies:"])
        dic["Marginal Costs"] = dic["Marginal Costs:"]

        p1,_ = stack_chart(tw,dic,y1,legend,decison_var,path2output,cmap,"w")
        p2,_ = stack_chart(ts,dic,y2,legend,decison_var,path2output,cmap,"s")
        p3,_ = stack_chart(t,dic,y3,legend,decison_var,path2output,cmap)
        p4 = load_duration_curve(t,dic,y3,legend,decison_var,path2output,cmap)
        decison_var = "Thermal Generation Mix:"
        p5 = pie_chart(dic[decison_var],path2output,decison_var,cmap)
        p10 = bar_chart(dic[decison_var],path2output,decison_var,cmap)
        decison_var = "Installed Capacities:"
        p6 = pie_chart(dic[decison_var],path2output,decison_var,cmap)
        p7 = bar_chart(dic[decison_var],path2output,decison_var,cmap)
        decison_var = "Specific Capital Costs of installed Capacities:"

        decision_vars = ["Anual Total Costs",
                         "Anual Total Costs (with costs of existing power plants and heat storages)",
                         "Electricity Production by CHP",
                         "Thermal Production by CHP",
                         "Mean Value Heat Price",
                         "Mean Value Heat Price (with costs of existing power plants and heat storages)",
                         "Median Value Heat Price",
                         "Electrical Consumption of Heatpumps and Power to Heat devices",
                         "Maximum Electrical Load of Heatpumps and Power to Heat devices",
                         "Revenue From Electricity:",
                         "Ramping Costs",
                         "Operational Cost:",
                         "Anual Investment Cost",
                         "Anual Investment Cost (of existing power plants)",
                         "Electrical Peak Load Costs",
                         "Variable Cost CHP's",
                         "Fuel Costs",
                         ]
        p9 = plot_table(decision_vars,dic,path2output)

        l1 = layout([[p5,p10],[p6,p7]])

        decision_vars = ["Anual Investment Cost:",
                         "Anual Investment Cost (of existing power plants and heat storages)",
                         "Operational Cost:", "Fuel Costs:", "Revenue From Electricity:"]
        p8 = costBarStack_chart(dic,decision_vars,path2output,cmap)

        p11 = plotExtra_table(decision_vars,dic,path2output)
        l2 = layout([[p8],[p11]])

        kwargs = {"Thermal Power Energymix (TPE)": p3,
                  "TPE Winter": p1,
                  "TPE Summer": p2,
                  "Load Duration Curve": p4,
                  "TPE and Plant Capatcities": l1,
                  "Specific Capital Costs of IC":l2,
                  "Results":p9}
        tabs = tab_panes(path2output,**kwargs)
        
        if solution == -1:
            output_file(os.path.join(path2output,"output.html"),title="Dispatch output")
            save(tabs)
            
        if show_plot:
            show(tabs)
        return tabs.tabs

    except Exception as e:
        print(str(e))
        return "Error4"
#%%
if __name__ == "__main__":
    print('Plot Results...')
    plot_solutions(show_plot=True)
    print('Plot Results done')

