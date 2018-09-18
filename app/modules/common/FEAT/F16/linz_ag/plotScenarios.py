# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 12:18:11 2018

@author: root
"""
import random as rd
import numpy as np
from bokeh.io import show, output_file,save
from bokeh.plotting import figure
from bokeh.palettes import Category10,Category20,Spectral
from bokeh.transform import dodge
from bokeh.models import Legend,DataTable,TableColumn,ColumnDataSource
from math import pi,radians,degrees,sin,cos
from bokeh.models import HoverTool, LinearAxis, Range1d
from bokeh.layouts import gridplot,layout,widgetbox
from bokeh.models.widgets import Panel, Tabs, Div
from imageHTML import header_html,font_style
import os,sys
#%%
# =============================================================================
# 
# =============================================================================
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__)))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUWdispatch.eng_format import EngNumber,EngUnit
from CM.CM_TUWdispatch.plot_bokeh import stack_chart,matrix,colormapping,costBarStack_chart,plotExtra_table
# =============================================================================
#
# =============================================================================
#%%
def heatElectPrice(**kwargs):
    """
    Params:
        dic     solution dic
        
        t       range
    """
    electricity = np.array(kwargs["dic"]["Electricity Price"])[kwargs["t"]]
    heat_p = np.array(kwargs["dic"]["Heat Price"])[kwargs["t"]]
    
    p = figure(title="Heat Price and electricity Price",
                x_axis_label = "Time in Hours",
                y_axis_label = "€/MWh",
                tools = "pan,wheel_zoom,box_zoom,reset,save",
                y_range=(np.min(heat_p)-1,np.percentile(heat_p, 90)+1))

    p.extra_y_ranges = {"2nd": Range1d(start=min(electricity)-1, 
                                       end=max(electricity)+1)}
    e_line = p.line(kwargs["t"],list(electricity),line_width=0.5, y_range_name="2nd",
                    muted_alpha=0.2,color =Category10[3][1] )
    h_line = p.line(kwargs["t"],list(heat_p),line_width=0.5, muted_alpha=0.2,
                    color =Category10[3][0] )
    p.add_layout(LinearAxis(y_range_name="2nd",axis_label='Electricity price in €/MWh'), 
                 'right')
    p.toolbar.logo = None
    
    items = [("Electricity Price",   [e_line] ), ("Heat Price",   [h_line] )]
    legend = Legend(items=items,location=(10, 10))
    p.add_layout(legend, 'right')   
    p.legend.click_policy = "hide" # "mute"
    
    return p
#%%
def pricePlots(**kwargs):
    """
    Params: 
    solutions       dict
                    dictionary of dictionarys of the Dispatch model
    
    t               range
    
    sc_names        list 
    
    sub_sc_names    list
    """
    p=[]
    column=[[Div(width = 550)]+[Div(text= font_style+"<p>"+sc+"</p>",width = 850) for sc in kwargs["sc_names"]]]
    for sub_sc in kwargs["sub_sc_names"]:
        row=[Div(text= font_style+"<p>"+sub_sc+"</p>")]
        for sc in kwargs["sc_names"]:
            dic = kwargs["solutions"][sc][sub_sc]
            if dic:
                p_i = heatElectPrice(dic=dic, t=kwargs["t"])
                p_i.toolbar.logo = None
                p_i.toolbar_location = "above"
                p_i.plot_width = 850
                p_i.plot_height = 350 
                row.append(p_i)
                p.append(p_i)
            else:
                row.append(Div(width=850))
        column.append(row)            
    for i in range(1,len(p)):
        p[i].x_range = p[0].x_range
            
    l = layout(children=column)
    return l
#%%
def table(**kwargs):
        
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
    
    vals = {sc+"-"+sub_sc: None for sub_sc in kwargs["sub_sc_names"] for sc in kwargs["sc_names"]}
    
    for sub_sc in kwargs["sub_sc_names"]:
        for sc in kwargs["sc_names"]:
            dic = kwargs["solutions"][sc][sub_sc]
            if dic:
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
                vals[sc+"-"+sub_sc]=formatted_val
            else:
                del vals[sc+"-"+sub_sc]
    
    data = {**{"topic": decision_vars},**vals}
            
    source = ColumnDataSource(data)
    cols = [TableColumn(field=key, title="Value of "+key) for key in vals]
    columns = [TableColumn(field="topic", title="Topic")] + cols
            
    data_table = DataTable(source=source, columns=columns, width=1500, height=800)
    
    return widgetbox(data_table)
#%%
def costLineUp(**kwargs):
    """
    Params: 
        solutions       dict
                        dictionary of dictionarys of the Dispatch model
        
        sc_names        list 
        
        sub_sc_names    list
    
    Return:
        layout with same x-Axis
    """
    decision_vars = ["Anual Investment Cost:",
                         "Anual Investment Cost (of existing power plants and heat storages)",
                         "Operational Cost:", "Fuel Costs:", "Revenue From Electricity:"]
    column=[[Div(width = 550)]+[Div(text= font_style+"<p>"+sc+"</p>",width = 850) for sc in kwargs["sc_names"]]]
    for sub_sc in kwargs["sub_sc_names"]:
        row=[Div(text= font_style+"<p>"+sub_sc+"</p>")]
        for sc in kwargs["sc_names"]:
            dic = kwargs["solutions"][sc][sub_sc]
            if dic:
                cmap = colormapping(dic["Technologies:"])
                p_i_1 = costBarStack_chart(dic,decision_vars,"",cmap)
                p_i_2 = plotExtra_table(decision_vars,dic,"")
                p_i_1.plot_width = 850
                p_i_1.plot_height = 250
                p_i_2.height = 250
                p_i_2.width = 850
                row.append([[p_i_1],[p_i_2]])
            else:
                row.append(Div(width=850))
        column.append(row)
                
    l = layout(children=column)
    
    return l
#%%
def stackPlot(**kwargs):
    """
    Params: 
        solutions       dict
                        dictionary of dictionarys of the Dispatch model
        
        t               range
        
        sc_names        list 
        
        sub_sc_names    list
    
    Return:
        layout with same x-Axis
    """
    
    p=[]
    column=[[Div(width = 550)]+[Div(text= font_style+"<p>"+sc+"</p>",width = 850) for sc in kwargs["sc_names"]]]
    for sub_sc in kwargs["sub_sc_names"]:
        row=[Div(text= font_style+"<p>"+sub_sc+"</p>")]
        for sc in kwargs["sc_names"]:
            dic = kwargs["solutions"][sc][sub_sc]
            if dic:
                decison_var="Thermal Power Energymix:"
                legend = list(dic[decison_var].keys())
                y = matrix(dic,decison_var,legend,kwargs["t"])
                cmap = colormapping(dic["Technologies:"])
                dic["Marginal Costs"] = dic["Marginal Costs:"]
                p_i = stack_chart(kwargs["t"],dic,y,legend,decison_var,"_",cmap)[1]
                p_i.toolbar.logo = None
                p_i.toolbar_location = "above"
                p_i.plot_width = 850
                row.append(p_i)
                p.append(p_i)
            else:
                row.append(Div(width=850))
        column.append(row)
                
    for i in range(1,len(p)):
        p[i].x_range = p[0].x_range
    

            
    l = layout(children=column)
    
    return l

#%% Color mapping
def color(i,j):
    if i<=10:
        if i<3:
            i=3
        return Category10[i][j]
    else:
        return Category20[i][j]
# =============================================================================
#
# =============================================================================
#%% Color mapping2
def color2(i,j):
    if i<=11:
        if i<3:
            i=3
        return Spectral[i][j]
    else:
        return color(i,j)
# =============================================================================
#
# =============================================================================
#%% Levelized Cost of Energy (Heating) BAR PLOT
def lcoeHeating(**kwargs):
    """
    Params:
        sc_names:           list
                            Names of Scenarios

        sub_sc_names:       list
                            Names of SubScenarios

        data_LCOE:          dict
                            keys are Names of Scencarios
                            values are lists of LCOE's of Subscenario
    """    
    space=0.13
    width = 0.12
    data_LCOE = { ** {'Sub Scenarios' : kwargs["sub_sc_names"]} ,
                  ** kwargs["data_LCOE"]}

    source_LCOE = ColumnDataSource(data=data_LCOE)
    
    p = figure(x_range=kwargs["sub_sc_names"],
               title="Levelized Cost of Energy (Heating)")
    
    legend_items = [(sc,[p.vbar( x=dodge( 'Sub Scenarios', 
                                         -space*(len(kwargs["sc_names"])-1)/2+i*space,
                                         range=p.x_range),
                                top=sc, width=width, source=source_LCOE,
                                color = color(len(kwargs["sc_names"])+1,i))
                    ]) for i,sc in enumerate(kwargs["sc_names"])]

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    legend = Legend(items=legend_items,location=(10, 10))
    p.add_layout(legend, 'right')
    p.legend.click_policy="hide"
    p.xaxis.axis_label = "Sub Szenarios"
    p.yaxis.axis_label = "LCOE in €/MWh_th"
    p.toolbar.logo = None
    p.toolbar_location = None
    p.plot_width = 850
#    p.plot_height = 850
#    p.sizing_mode = "scale_width"

    return p

# =============================================================================
#
# =============================================================================
#%%
def pieTGM(**kwargs):
    """
    Params:
        sc_name             str
                            Name of scenario

        sub_sc_name         str
                            Name of sub scenario

        tgm                 dict
                            anual Thermal generation of each heat generator
    """
    p = figure(title = "Thermal Generation Mix of " + kwargs["sc_name"] + " - " + kwargs["sub_sc_name"])


    x=0
    y=1
    radius=0.9
    heatgeneartors = list(kwargs["tgm"])
    colors = [color(len(heatgeneartors),i) for i,j in enumerate(heatgeneartors)]
    size = np.array([kwargs["tgm"][hg] for hg in heatgeneartors])/sum(list(kwargs["tgm"].values()))
    size_cumsum = np.cumsum(size*2*pi)
    start_angle = [0]+size_cumsum.tolist()[:-1]
    end_angle = size_cumsum.tolist()
    wedges = [p.wedge(x=x,y=y, radius=radius, start_angle= start_angle[i],
                      end_angle=end_angle[i], color=colors[i],muted_alpha=0.2,
                      alpha=0.9,line_color="black")
                for i in range(len(colors))]
    text=list(np.round(size*100,2))
    items = [(name+": "+str(percentage)+"%",[glyph]) for name,glyph,percentage in zip(heatgeneartors,wedges,text)]
    legend = Legend(items=items,location=(10, 10))
    p.add_layout(legend, 'right')
    p.legend.click_policy = "mute" # "mute"
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.toolbar.logo = None
    p.toolbar_location = None
#    p.plot_width = 850
#    p.plot_height = 850
#    p.sizing_mode = "scale_width"
    return p

# =============================================================================
#
# =============================================================================
#%%
def crazyPlot(x=0,y=0,teta_offset=10,num_of_circular_axes = 6, bar_width=0.4,
              **kwargs):
    """
    Params:
        x,y                     int
                                Middle Point of the Circle
                                (Default:0)

        teta_offset             int
                                Offset in degrees from +- 90°, for the axis labels
                                (Default:10)

        num_of_circular_axes    int
                                Number of subdivision of axes ( # of circles)
                                (Default:6)

        bar_widh                float
                                bar width float in the interval [0-1]
                                (Default: 0.5)

        data                    dict
                                like: {cost_name:
                                                {scenarioname:
                                                         {heatgneartor: float}
                                                }
                                        }


        heatgeneartors          dict
                                a list of names of heatgenerators for each scenario

        sc_names                list
                                a list of scneario names

        cost_line_up_names      list
                                a list of cost parameters

        max_val                 dict
                                maximum value of each sub scenario
        
        title                   str
                                name of figure               
        

    """
    hover = HoverTool(tooltips=[
    ("heat geneartor", "@heat_geneartor"),
    ("scenario", "@scenario"),
    ("value", "@value{(€ 0.00 a)}"),
    ("type", "@type"),
    ], mode='mouse')

    data = kwargs["data"]
    heatgeneartors = kwargs["heatgeneartors"]
    sc_names = kwargs["sc_names"]
    cost_line_up_names = kwargs["cost_line_up_names"]
    max_val = kwargs["max_val"]
    r_i = max_val*0.8
    r_o = max_val + r_i

    pad = (r_o + r_i)*0.8
    plot_range = (-pad , pad)


    p = figure(x_range=plot_range, y_range=plot_range, toolbar_sticky=False,
               tools=[hover,"pan","wheel_zoom","box_zoom","reset,save"],
               title="Cost Line Up - "+ kwargs["title"])

    for r in np.linspace(r_i, r_o, num=num_of_circular_axes,endpoint=True).tolist():
        p.text(x=0, y=int(r)+1, text=[str(EngNumber(float(round(r-r_i,2))))],text_font_size="9pt",
               text_align="center", text_baseline="middle")
        p.circle(x=x, y=y, radius=r,fill_color=None, line_color="black",alpha=0.2)

    teta_step = radians((360-2*teta_offset)/len(sc_names))
    start_angle = radians(90+teta_offset)
    sc_glyphs = {sc:[] for sc in sc_names}
    for i,val in enumerate(sc_names):
        sc_glyphs[val] += [ p.annular_wedge (x=x, y=y, inner_radius=r_i,
                                             outer_radius=r_o, muted_alpha=0.2,
                                             legend = val,
                                             start_angle=start_angle,
                                             end_angle=start_angle+teta_step,
                                             color=color2(len(sc_names),i),
                                             alpha=0.6)]
        start_angle += teta_step

    teta_sub_step = {sc: teta_step/len(heatgeneartors[sc]) for sc in sc_names}
    teta_text = {sc: teta_sub_step[sc] /2 for sc in sc_names}
    start_angle = radians(90+teta_offset)
   
    for sc in sc_names:
        for j,hg in enumerate(heatgeneartors[sc]):
            angle = start_angle+teta_text[sc]
            if angle > 2*pi:
                angle -= 2*pi
            if pi/2< angle <3*pi/2:
                angle += pi
                
            p.text(x=x + r_o*cos(start_angle+teta_text[sc]),
                   y=y + r_o*sin(start_angle+teta_text[sc]),
                   text = [hg], angle=angle,
                   text_font_size="12pt", text_align="center",
                   text_baseline="middle")
            
            p.ray(x=x+cos(start_angle)*r_i, y=y+sin(start_angle)*r_i,
                  length=r_o, angle=start_angle,line_width=2,color = "black")

            start_angle += teta_sub_step[sc]
    # last ray for beauty
    p.ray(x=x+cos(start_angle)*r_i, y=y+sin(start_angle)*r_i,
                  length=r_o, angle=start_angle,line_width=2,color = "black")


    teta_sub_sub_step = {sc: teta_sub_step[sc] / len(cost_line_up_names) for sc in sc_names}
    mid_point_bar = {sc:  teta_sub_sub_step[sc] / 2 for sc in sc_names}
    bar_step = {sc:2*mid_point_bar[sc]*bar_width for sc in sc_names}
    start_angle = radians(90+teta_offset)
    sav_pos = start_angle
    # TODO:extra legend
#    glyphs = {sc:[] for sc in sc_names}
#    glyphs_cost = {cost:[] for cost in cost_line_up_names}

    for sc in sc_names:
        for hg in heatgeneartors[sc]:
            for i,cost in enumerate(cost_line_up_names):
                
                angle = start_angle
                angle += mid_point_bar[sc] - bar_step[sc]/2
                
                glyph = p.annular_wedge(x=x, y=y, inner_radius=r_i,
                                        outer_radius=r_i+data[cost][sc][hg],
                                        start_angle=angle,
                                        end_angle=angle+bar_step[sc],
                                        color=color(len(cost_line_up_names),i),
                                        alpha=1,
                                        legend=cost,
                                        muted_alpha=0.2,
                                        source =  {"heat_geneartor":[hg],
                                                   "scenario":[sc],
                                                   "type":[cost],
                                                   "value":[data[cost][sc][hg]]})
                # make only for this list hover aviable
                hover.renderers += [glyph] 
                
                #TODO:extra legend
#                glyphs_cost[cost] += [glyph]
#                glyphs[sc] += [glyph]
                
                start_angle += teta_sub_sub_step[sc]
                
            sav_pos += teta_sub_step[sc]
            start_angle = sav_pos
            
                


    #TODO: extra legend
    #for i,v in sc_glyphs.items():
    #    glyphs[i] += v
    #items = [(i,v) for i,v in glyphs.items()] + [(i,v) for i,v in glyphs_cost.items()]
    #legend = Legend(items=items,location=(0,0))
    #p.add_layout(legend,"right")
#    p.legend.label_text_font_size = '6.5pt'
    p.legend.border_line_color= None
    p.legend.location = "center"
    p.legend.click_policy = "mute" # "mute"
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.plot_width = 100 * (len(kwargs["cost_line_up_names"]) + len(kwargs["sc_names"] ) +1)
    p.plot_height = 100 * (len(kwargs["cost_line_up_names"]) + len(kwargs["sc_names"] ) +1)
#    p.sizing_mode = "scale_both"
#    p.toolbar.active_inspect  = None
    p.toolbar.logo = None
    p.toolbar_location = None
    return p
#%%
# =============================================================================
#
# =============================================================================
def invertCostData(sc_names,sub_sc_names,heatgeneartors,cost_line_up_names,
                   cost_line_up_vals):
    
    data_2 = {sc:{cost:{sub_sc: {hg:cost_line_up_vals[sc,sub_sc,hg][cost]
                            for hg in heatgeneartors[sc]}
                    for sub_sc in sub_sc_names}
                for cost in cost_line_up_names}
        for sc in sc_names}
    max_val2 = {sc:[] for sc in sc_names}
    for sc in sc_names:
        for sub_sc in sub_sc_names:
            max_val2[sc].append(max([max(cost_line_up_vals[sc,sub_sc,hg].values()) for hg in heatgeneartors[sc]]))
        max_val2[sc] = max(max_val2[sc])

    return data_2,max_val2
#%%
# =============================================================================
#     
# =============================================================================
def compareScnearioPlot(**kwargs):
    """
    Params:
        sc_names            list
        
        sub_sc_names        list
        
        data_LCOE           dict
        
        tgms                dict
        
        data                dict
        
        heatgeneartors      dict
        
        cost_line_up_names  dict
        
        cost_line_up_names  list
        
        max_val             dict
        
        solutions           dict
        
        
    """
        
    data_LCOE = {sc: [] for sc in  kwargs["sc_names"]}
    for sc in  kwargs["sc_names"]:
        for sub_sc in kwargs["sub_sc_names"]:
            data_LCOE[sc].append(kwargs["data_LCOE"][sc].get(sub_sc,0))
   
    lcoe = layout (children = [lcoeHeating(data_LCOE=data_LCOE,
                                sub_sc_names=kwargs["sub_sc_names"],
                                sc_names= kwargs["sc_names"])])         
    data_lcoe_2 = {sub_sc:[kwargs["data_LCOE"][sc][sub_sc] for sc in kwargs["sc_names"]] for sub_sc in kwargs["sub_sc_names"]}
   
    lcoe_2 = layout (children = [lcoeHeating(data_LCOE=data_lcoe_2,
                                sub_sc_names=kwargs["sc_names"],
                                sc_names= kwargs["sub_sc_names"])])
    
    column=[[Div(width = 500)]+[Div(text= font_style+"<p>"+sc+"</p>",width = 650) for sc in kwargs["sc_names"]]]
    for sub_sc in kwargs["sub_sc_names"]:
        row=[Div(text= font_style+"<p>"+sub_sc+"</p>")]
        for sc in kwargs["sc_names"]:
            tgm = kwargs["tgms"][sc,sub_sc]
            if tgm:
                p_i=pieTGM(sc_name = sc, sub_sc_name = sub_sc,
                       tgm =tgm )
                p_i.toolbar.logo = None
                p_i.toolbar_location = None
                p_i.plot_width = 650
                p_i.plot_height = 650
                row.append(p_i)
            else:
                row.append(Div(width = 650))
        column.append(row)
    tgm = layout(children=column)
    
    cost = []
    temp_liste = []
    for i,sub_sc in enumerate(kwargs["sub_sc_names"]):
        temp_liste.append( crazyPlot(data = kwargs["data"][sub_sc],
                                      heatgeneartors=kwargs["heatgeneartors"],
                                      sc_names=kwargs["sc_names"],
                                      cost_line_up_names=kwargs["cost_line_up_names"],
                                      max_val = kwargs["max_val"][sub_sc],
                                      title=sub_sc)
                )
        if i%2:
            cost.append(temp_liste)
            temp_liste = []
    cost.append(temp_liste)
    cost = layout(children = cost)
    
    cost3 = {}
    data_2,max_val2 = invertCostData(kwargs["sc_names"],
                                     kwargs["sub_sc_names"],
                                     kwargs["heatgeneartors"],
                                     kwargs["cost_line_up_names"],
                                     kwargs["cost_line_up_vals"])
    for sc in kwargs["sc_names"]:
        heatgeneartors2 = dict(zip(kwargs["sub_sc_names"],[kwargs["heatgeneartors"][sc]]*len(kwargs["sub_sc_names"])))
        for i,key in enumerate(heatgeneartors2):
            if i%2:
                heatgeneartors2[key] = list(reversed(heatgeneartors2[key]))
                
        cost3[sc] = crazyPlot(data = data_2[sc],heatgeneartors=heatgeneartors2,
                                 sc_names=kwargs["sub_sc_names"],
                                 cost_line_up_names=kwargs["cost_line_up_names"],
                                 max_val = max_val2[sc],title=sc)
    if kwargs["solutions"]:
        cost2 = costLineUp(solutions=kwargs["solutions"],sc_names=kwargs["sc_names"],sub_sc_names=kwargs["sub_sc_names"])
        results = table(solutions=kwargs["solutions"],sc_names=kwargs["sc_names"],sub_sc_names=kwargs["sub_sc_names"])
        stack = stackPlot(solutions=kwargs["solutions"],sc_names=kwargs["sc_names"],sub_sc_names=kwargs["sub_sc_names"],t=kwargs["t"])
        prices = pricePlots(solutions=kwargs["solutions"],sc_names=kwargs["sc_names"],sub_sc_names=kwargs["sub_sc_names"],t=kwargs["t"])
        tab_prices = [Panel(child=prices, title="Prices")]
        tab_cost2 = [Panel(child=cost2, title="Cost Line Up (CLU)")]
        tab_results = [Panel(child=results, title="Results")]
        tab_stack = [Panel(child=stack, title="Thermal Energy Mix")]
    else:
        tab_cost2 = []
        tab_results = []
        tab_stack = []
        tab_prices = []
        
    tab_lcoe = Panel(child=lcoe, title="LCOE -(Scenario VS Portfolio)")
    tab_lcoe_2 = Panel(child=lcoe_2, title="Levelized Cost of Energy (LCOE)")
    tab_tgm = Panel(child=tgm, title="Thermal Geneartion Mix")
    tab_cost = Panel(child=cost, title="CLU - (Szenario VS Portfolios)")
    tab_cost3 = [ Panel(child=glyph, title="CLU - (Portfolio: " + sz+")" ) for sz,glyph in cost3.items()]

    
    div = widgetbox(Div(text= header_html))
    tab = Tabs( tabs=[tab_lcoe_2, tab_lcoe] + [tab_tgm] + tab_results + tab_stack + tab_prices+ tab_cost2 + [tab_cost] + tab_cost3)
    l = layout (children = [[div],[tab]], sizing_mode = "scale_width")

    return l

# =============================================================================
#
# =============================================================================
if __name__ == "__main__":
    
#%% Creating Dummy Data
# =============================================================================
#     Comparing Szenarios
# =============================================================================
    print("Starting PlotScenario Main...")
    sc_names = ["Base Scenario","No Nuclear Low CO2 Scenario"]
    sub_sc_names = ["Moderate Price","Current Price",
                    "High Price","Low Price"]
    hg1 = ["boiler","PV","CHP-BP","CHP-SE","Heat Storage","Heat Pump"]
    hg2 = list(reversed(["boiler","PV","CHP-BP"]))
    heatgeneartors = dict(zip(sc_names,[hg1,hg2]))
    
    for i,key in enumerate(heatgeneartors):
        if i%2:
            heatgeneartors[key] = list(reversed(heatgeneartors[key]))
            
    cost_line_up_names = ["OPEX", "CAPEX", "Fuel costs", "Revenue Eletricity"]
    cost_line_up_vals= {}
    tgms = {}
    data_LCOE = {}
    max_val = {sub_sc:[] for sub_sc in sub_sc_names}
    for sc in sc_names:
        data_LCOE[sc] = {sub_sc:rd.randint(1,20) for sub_sc in sub_sc_names}
        for sub_sc in sub_sc_names:
            _tgm_percentage = (np.random.dirichlet(np.ones(len(heatgeneartors[sc])),size=1)*100).astype(int).tolist()[0]
            _tgm_percentage[-1] +=  100-sum(_tgm_percentage)
            tgms[(sc,sub_sc)] = dict(zip(heatgeneartors[sc],_tgm_percentage))
            for hg in heatgeneartors[sc]:
                cost_line_up_vals[(sc,sub_sc,hg)]=dict(zip(cost_line_up_names,[rd.randint(0,10e4) for _ in range(len(cost_line_up_names))]))
            
    data = {sub_sc:{cost:{sc: {hg:cost_line_up_vals[sc,sub_sc,hg][cost]
                                for hg in heatgeneartors[sc]}
                        for sc in sc_names}
                    for cost in cost_line_up_names}
            for sub_sc in sub_sc_names}

    for sub_sc in sub_sc_names:
        for sc in sc_names:
            max_val[sub_sc].append(max([max(cost_line_up_vals[sc,sub_sc,hg].values()) for hg in heatgeneartors[sc]]))
        max_val[sub_sc] = max(max_val[sub_sc])
#%%    
    
    print("Creating Plot With Dummy Data...")
    t = compareScnearioPlot(data_LCOE= data_LCOE, 
                             sub_sc_names= sub_sc_names,
                             sc_names = sc_names,
                             cost_line_up_names = cost_line_up_names,
                             max_val = max_val,
                             heatgeneartors = heatgeneartors,
                             tgms = tgms,
                             data = data,
                             solutions = None,
                             cost_line_up_vals = cost_line_up_vals
                 )
    print("Done!")
    output_file("output_scenarios_compare.html")
    show(t)