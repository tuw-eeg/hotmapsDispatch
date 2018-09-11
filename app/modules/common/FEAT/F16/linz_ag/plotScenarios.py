# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 12:18:11 2018

@author: root
"""


import random as rd
import numpy as np
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.palettes import Category10,Category20
from bokeh.transform import dodge
from bokeh.models import Legend
from math import pi,radians,degrees,sin,cos
from bokeh.models import HoverTool
from bokeh.layouts import gridplot,layout,widgetbox
from bokeh.models.widgets import Panel, Tabs, Div
from imageHTML import header_html
# =============================================================================
#
# =============================================================================
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
    data_LCOE = { ** {'Sub Scenarios' : kwargs["sub_sc_names"]} ,
                  ** kwargs["data_LCOE"]}

    source_LCOE = ColumnDataSource(data=data_LCOE)

    p = figure(x_range=kwargs["sub_sc_names"],
               title="Levelized Cost of Energy (Heating)",
               toolbar_location=None, tools="")

    legend_items = [(sc,[p.vbar( x=dodge( 'Sub Scenarios', -0.25+i*0.25,
                                         range=p.x_range),
                                top=sc, width=0.2, source=source_LCOE,
                                color = color(len(kwargs["sc_names"])+1,i))
                    ]) for i,sc in enumerate(kwargs["sc_names"])]

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    legend = Legend(items=legend_items,location=(10, 10))
    p.add_layout(legend, 'right')
    p.legend.click_policy="hide"
    p.xaxis.axis_label = "Sub Szenarios"
    p.yaxis.axis_label = "LCOE in €/MWh_th"
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
def crazyPlot(x=0,y=0,teta_offset=10,num_of_circular_axes = 6, bar_width=0.5,
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
                                a list of parameters from the

        max_val                 float
                                maximum value of the data

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
        p.text(x=0, y=int(r)+1, text=[round(r-r_i,2)],text_font_size="9pt",
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
                                             color=color(len(sc_names),i),
                                             alpha=0.6)]
        start_angle += teta_step

    teta_sub_step = {sc: teta_step/len(heatgeneartors[sc]) for sc in sc_names}
    teta_text = {sc: teta_sub_step[sc] /2 for sc in sc_names}
    start_angle = radians(90+teta_offset)
    i=0
    text = heatgeneartors.copy()
    for sc in sc_names:
        for j in range(len(heatgeneartors[sc])):
            angle = start_angle+teta_text[sc]
            if angle > 2*pi:
                angle -= 2*pi
            if pi/2< angle <3*pi/2:
                angle += pi
            if j < len(heatgeneartors)*len(sc_names):
                p.text(x=x + r_o*cos(start_angle+teta_text[sc]),
                       y=y + r_o*sin(start_angle+teta_text[sc]),
                       text = [text[sc][i]], angle=angle,
                       text_font_size="12pt", text_align="center",
                       text_baseline="middle")

            p.ray(x=x+cos(start_angle)*r_i, y=y+sin(start_angle)*r_i,
                  length=r_o, angle=start_angle,line_width=2,color = "black")

            start_angle += teta_sub_step[sc]
            i +=1


    teta_sub_sub_step = {sc: teta_sub_step[sc] / len(cost_line_up_names) for sc in sc_names}
    mid_point_bar = {sc:  teta_sub_sub_step[sc] / 2 for sc in sc_names}
    bar_step = {sc:2*mid_point_bar[sc]*bar_width for sc in sc_names}


    start_angle = radians(90+teta_offset)
    sav_pos = start_angle
    glyphs = {sc:[] for sc in sc_names}
    glyphs_cost = {cost:[] for cost in cost_line_up_names}
    for sc in sc_names:
        for i,cost in enumerate(cost_line_up_names):
            for hg in heatgeneartors[sc]:
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
                glyphs_cost[cost] += [glyph]
                glyphs[sc] += [glyph]
                hover.renderers += [glyph]
                start_angle += teta_sub_step[sc]
        sav_pos += teta_sub_sub_step[sc]
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
#p = lcoeHeating(data_LCOE=data_LCOE, sub_sc_names=sub_sc_names, sc_names= sc_names)
#output_file("LCOE (Heating).html")
#show(p)
#
#p = pieTGM(sc_name = sc_names[0], sub_sc_name = sub_sc_names[0],
#           heatgeneartors=heatgeneartors,
#           tgm = tgms[sc_names[0],sub_sc_names[0]])
#output_file("Pie Chart Theraml Generattion Mix.html")
#show(p)
#
#
#p = crazyPlot(data = data[sub_sc], heatgeneartors=heatgeneartors, sc_names=sc_names,
#          cost_line_up_names=cost_line_up_names,max_val = max_val,title=sub_sc)
#output_file("a.html")
#show(p)

#%%
# =============================================================================
#
# =============================================================================
def genPlot(**kwargs):
    lcoe = layout (children = [lcoeHeating(data_LCOE=kwargs["data_LCOE"],
                                sub_sc_names=kwargs["sub_sc_names"],
                                sc_names= kwargs["sc_names"])])


    tgm = layout(children = [[pieTGM(sc_name = sc, sub_sc_name = sub_sc,
                   heatgeneartors= kwargs["heatgeneartors"],
                   tgm = kwargs["tgms"][sc,sub_sc]) for sc in kwargs["sc_names"]] for sub_sc in kwargs["sub_sc_names"]])

    cost = []
    temp_liste = []
    for i,sub_sc in enumerate(kwargs["sub_sc_names"]):
        temp_liste.append( crazyPlot(data = kwargs["data"][sub_sc],
                                      heatgeneartors=kwargs["heatgeneartors"],
                                      sc_names=kwargs["sc_names"],
                                      cost_line_up_names=kwargs["cost_line_up_names"],
                                      max_val = kwargs["max_val"],
                                      title=sub_sc)
                )
        if (i+1) % 2 == 0:
            cost.append(temp_liste)
            temp_liste = []
    cost.append(temp_liste)
    cost = layout(children = cost)

    tab_lcoe = Panel(child=lcoe, title="Levelized Cost of Energy")
    tab_tgm = Panel(child=tgm, title="Thermal Geneartion Mix")
    tab_cost = Panel(child=cost, title="Cost Line Up")
    div = widgetbox(Div(text= header_html))
    tab = Tabs( tabs=[ tab_lcoe, tab_tgm, tab_cost ])
    l = layout (children = [[div],[tab]], sizing_mode = "scale_width")

    return l

# =============================================================================
#
# =============================================================================
if __name__ == "__main__":
    #%% Creating Dummy Data
    sc_names = ["Base Scenario","No Nuclear Low CO2 Scenario"]
    sub_sc_names = ["Moderate Price","Current Price",
                    "High Price","Low Price"]
    heatgeneartors = ["boiler","PV","CHP-BP","CHP-SE","Heat Storage","Heat Pump"]
    cost_line_up_names = ["OPEX", "CAPEX", "Fuel costs", "Revenue Eletricity"]
    cost_line_up_vals= {}
    tgms = {}
    data_LCOE = {}
    for sc in sc_names:
        data_LCOE[sc] = [rd.randint(1,20) for _ in range(len(sub_sc_names))]
        for sub_sc in sub_sc_names:
            _tgm_percentage = (np.random.dirichlet(np.ones(len(heatgeneartors)),size=1)*100).astype(int).tolist()[0]
            _tgm_percentage[-1] +=  100-sum(_tgm_percentage)
            tgms[(sc,sub_sc)] = _tgm_percentage
            for hg in heatgeneartors:
                cost_line_up_vals[(sc,sub_sc,hg)]=dict(zip(cost_line_up_names,[rd.randint(0,10e4) for _ in range(len(cost_line_up_names))]))

    data = {sub_sc:{cost:{sc: {hg:cost_line_up_vals[sc,sub_sc,hg][cost]
                                for hg in heatgeneartors}
                        for sc in sc_names}
                    for cost in cost_line_up_names}
            for sub_sc in sub_sc_names}
    max_val = int(max([max(v.values()) for _,v in cost_line_up_vals.items()]))

    if False:
        t = genPlot(data_LCOE= data_LCOE,
                     sub_sc_names= sub_sc_names,
                     sc_names = sc_names,
                     cost_line_up_names = cost_line_up_names,
                     max_val = max_val,
                     heatgeneartors = heatgeneartors,
                     tgms = tgms,
                     data = data
                     )

        output_file("output_scenarios_compare.html")
        show(t)