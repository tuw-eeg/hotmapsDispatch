# -*- coding: utf-8 -*-
"""
# =============================================================================
# Copyright (c) <year> <copyright holders>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

Created on Mon Feb 10 11:24:35 2020

@author: hasani

Description: This scripts create a html with charts for overall scenarios 

"""

# =============================================================================
# IMPORT NEEDED MODULES
# =============================================================================
import numpy as np
import pandas as pd
from pathlib import Path
import pprint as pp
import pickle
import altair as alt
from altair_saver import save
import tempfile
alt.data_transformers.disable_max_rows()
# =============================================================================
# GLOBAL PATHS AND VARIABLES
# =============================================================================
BASE_DIR = Path(__file__).parent.resolve()
tempalte_path = BASE_DIR.joinpath("compare.html")
# =============================================================================
# FUNCTIONS
def prerpare_data(df):
    # print("Prepare Data...")
    df = df.reset_index()
    df["topic2"] = df.topic.str.split("[",expand=True)[0].str.strip() # get rid of units
    sub_sc_df = df["Sub Scenario"].str.split("_",expand=True)
    len_sub_sc = sub_sc_df.shape[1]
    if len_sub_sc>1:
        cols = [f"Sub Scenario {i}" for i in range(1,len_sub_sc+1)]
        df[cols] = sub_sc_df
        
        if len_sub_sc >5:
            df['Sub Scenario 5'] = df[[f"Sub Scenario {i}" for i in range(5,len_sub_sc+1)]].agg('_'.join, axis=1)
            df = df.drop([f"Sub Scenario {i}" for i in range(6,len_sub_sc+1)],axis=1)
    # print("Prepare Data Done")
    return df,len_sub_sc
# =============================================================================
def viz_spec(len_sub_sc):    
    if len_sub_sc >1:
        tooltip = ["Scenario"]+[f"Sub Scenario {i}" for i in range(1,len_sub_sc+1)]+ ['topic', 'value']
    else:
        tooltip = ["Scenario","Sub Scenario",'topic', 'value']
    kwargs_bar = dict(x="Sub Scenario 2",y=alt.Y("value",stack=True,aggregate="mean"),color="topic",tooltip=tooltip)
    kwargs_bar_mark = dict(opacity=0.9)
    kwargs_bar2 = dict(x="Sub Scenario 2",y=alt.Y("value",stack=False,aggregate="mean"),color="topic")
    kwargs_bar_mark2 = dict(fillOpacity=0,stroke='black')            
    kwargs_scatter = dict(x="Sub Scenario 2",y="value",color="Sub Scenario 4",shape="Sub Scenario 5",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)
    kwargs_boxplot = dict(x="Sub Scenario 2",y="value",color="Sub Scenario 2",column='Sub Scenario 1',row="Scenario")
    if len_sub_sc==1:
        kwargs_scatter = dict(x="Sub Scenario",y="value",color="Scenario",tooltip=tooltip,column="Scenario")
        kwargs_boxplot = dict(x="Scenario",y="value",color="Scenario")
        kwargs_bar = dict(x="Sub Scenario",y="value",column="Scenario",color="topic",tooltip=tooltip)
        kwargs_bar_mark = dict(opacity=0.5)
    elif len_sub_sc == 2:
        kwargs_bar = dict(x="Sub Scenario 2",y="value",color="topic",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)
        kwargs_scatter = dict(x="Sub Scenario 2",y="value",column='Sub Scenario 1',row="Scenario",tooltip=tooltip,color="Sub Scenario 2")
        kwargs_boxplot = dict(x="Sub Scenario 1",y="value",color="Sub Scenario 1",row="Scenario")

    elif len_sub_sc == 3:
        kwargs_scatter = dict(x="Sub Scenario 2",y="value",shape="Sub Scenario 3",column='Sub Scenario 1',row="Scenario",tooltip=tooltip,color="Sub Scenario 2")
    elif len_sub_sc == 4:
        kwargs_scatter = dict(x="Sub Scenario 2",y="value",color="Sub Scenario 3",shape="Sub Scenario 4",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)
    return kwargs_scatter,kwargs_bar,kwargs_bar_mark,kwargs_bar2,kwargs_bar_mark2,kwargs_boxplot
# =============================================================================
def viz_heatgenerator(len_sub_sc):   
    if len_sub_sc >1:
        tooltip = ["Scenario"]+[f"Sub Scenario {i}" for i in range(1,len_sub_sc+1)]+ ["heat generator",'topic', 'value']
    else:
        tooltip = ["Scenario","Sub Scenario",'topic',"heat generator",'value']
    kwargs_scatter = dict(x="heat generator",y="value",color="Sub Scenario 2",shape="Sub Scenario 4",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)
    kwargs_bar = dict(x="heat generator",y=alt.Y("value",stack=False),color="heat generator",tooltip=tooltip)#,column='Sub Scenario 1',row="Scenario")
    kwargs_bar_mark = dict(opacity=0.5)
    kwargs_bar_mark2 = dict(fillOpacity=0,stroke='black') 
    kwargs_bar2 = dict(x="heat generator",y="mean(value)",tooltip=tooltip)#,column='Sub Scenario 1',row="Scenario")
        
    if len_sub_sc == 1:
        kwargs_scatter = dict(x="heat generator",y="value",column='Sub Scenario',row="Scenario",tooltip=tooltip)#,color="heat generator")
        kwargs_bar = dict(x="heat generator",y="mean(value)",color="heat generator",tooltip=tooltip)#,column='Sub Scenario',row="Scenario")
        kwargs_bar_mark = dict()
    elif len_sub_sc == 2:
        kwargs_scatter = dict(x="heat generator",y="value",shape="Sub Scenario 2",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)#,color="heat generator")
    elif len_sub_sc == 3:
        kwargs_scatter = dict(x="heat generator",y="value",color="Sub Scenario 2",shape="Sub Scenario 3",column='Sub Scenario 1',row="Scenario",tooltip=tooltip)
    
    return kwargs_bar,kwargs_scatter,kwargs_bar_mark,kwargs_bar2,kwargs_bar_mark2
# =============================================================================
def stacked_bar(source,len_sub_sc,height=250,width=250,hg=False):
    _,kwargs_bar,kwargs_bar_mark,kwargs_bar2,kwargs_bar_mark2,__ = viz_spec(len_sub_sc)
    if len_sub_sc > 2:
        cols_group_by = [f"Sub Scenario {i}" for i in range(3,len_sub_sc+1)]
        mean_chart = alt.Chart(source,height=height,width=width).mark_bar(**kwargs_bar_mark2).encode(**kwargs_bar2)
        cost_chart = alt.layer(*[alt.Chart(df.copy(),height=height,width=width).mark_bar(**kwargs_bar_mark).encode(**kwargs_bar) for sub_sc,df in source.groupby(cols_group_by)],mean_chart,data=source).facet(column='Sub Scenario 1',row="Scenario")
        cost_chart = alt.layer(alt.Chart(source,height=height,width=width).mark_bar(**kwargs_bar_mark).encode(**kwargs_bar)).facet(column='Sub Scenario 1',row="Scenario")
    else:
        cost_chart = alt.Chart(source,height=height,width=width).mark_bar().encode(**kwargs_bar).interactive()
    return cost_chart.resolve_scale(x='independent',y='independent').interactive()


def stacked_bar_heat_generators(source,len_sub_sc,height=250,width=250):

    kwargs_bar = dict(x="heat generator:O",y=alt.Y("value",stack=True,aggregate="mean"),color="topic")
    kwargs_bar_mark = dict(opacity=0.9)
    kwargs_bar_mark2 = dict(fillOpacity=0,stroke='black') 
    kwargs_bar2 = dict(x="heat generator:O",y=alt.Y("value",stack=True,aggregate="sum"),color="topic")
 
    if len_sub_sc > 1:
        cols_group_by = [f"Sub Scenario {i}" for i in range(2,len_sub_sc+1)]
        # mean_chart = [alt.Chart(df,height=height,width=width).mark_bar(**kwargs_bar_mark2).encode(**kwargs_bar2) for sub_sc,df in source.groupby(["Sub Scenario 1"])]
        mean_chart = alt.Chart(source,height=height,width=width).mark_bar(**kwargs_bar_mark2).encode(**kwargs_bar2)
        # charts = [alt.Chart(df,height=height,width=width).mark_bar(**kwargs_bar_mark).encode(**kwargs_bar) for sub_sc,df in source.groupby(cols_group_by)]
        charts = [alt.Chart(height=height,width=width).mark_bar(**kwargs_bar_mark).encode(**kwargs_bar)]

        # cost_chart = alt.layer(*charts,mean_chart,data=source).facet(column='Sub Scenario 1',row="Scenario")
        cost_chart = alt.layer(*charts,data=source).facet(column='Sub Scenario 1',row="Scenario")
    else:
        cost_chart = alt.Chart(source,height=height,width=width).mark_bar().encode(**kwargs_bar,column='Sub Scenario',row="Scenario").interactive()
    return cost_chart.resolve_scale(x='independent',y='independent').interactive()

# =============================================================================
def scatter_single(source,len_sub_sc,height=250,width=250):
    kwargs_scatter,*_= viz_spec(len_sub_sc)
    if len_sub_sc >= 5:
        input_dropdown = alt.binding_select(options=source['Sub Scenario 3'].unique().tolist())
        selection = alt.selection_single(fields=['Sub Scenario 3'], bind=input_dropdown, name='Select ')
        chart = alt.Chart(source,height=height,width=width).mark_point().encode(**kwargs_scatter).add_selection(selection).transform_filter(selection).interactive()
    else:
        chart = alt.Chart(source,height=height,width=width).mark_point().encode(**kwargs_scatter).interactive()
    return chart.resolve_scale(x='independent',y='independent')
# =============================================================================
def scatter_heatgenerators(source,len_sub_sc,height=250,width=250):
    _,kwargs_scatter,*__= viz_heatgenerator(len_sub_sc)
    if len_sub_sc >= 4:
        input_dropdown = alt.binding_select(options=source['Sub Scenario 3'].unique().tolist())
        selection = alt.selection_single(fields=['Sub Scenario 3'], bind=input_dropdown, name='Select ')
        chart = alt.Chart(source,height=height,width=width).mark_point().encode(**kwargs_scatter).add_selection(selection).transform_filter(selection).interactive()
    else:
        chart = alt.Chart(source,height=height,width=width).mark_point().encode(**kwargs_scatter).interactive()
    
    return chart.resolve_scale(x='independent',y='independent')
# =============================================================================
def bar_heat_generators(source,len_sub_sc,height=250,width=250):
    kwargs_bar,_,kwargs_bar_mark,kwargs_bar2,kwargs_bar_mark2 = viz_heatgenerator(len_sub_sc)
    mean_chart = alt.Chart(source,height=height,width=width).mark_bar(**kwargs_bar_mark2).encode(**kwargs_bar2).interactive()
    chart = alt.Chart(source,height=height,width=width).mark_bar(**kwargs_bar_mark).encode(**kwargs_bar).interactive()
    comp = alt.layer(chart,mean_chart).facet(column='Sub Scenario 1' if len_sub_sc>1 else 'Sub Scenario 1',row="Scenario")
    return comp.resolve_scale(x='independent',y='independent')

def box_plot(source,len_sub_sc,height=250,width=250):
    chart = alt.Chart(source,width=width,height=height).mark_boxplot().encode(
                x="heat generator",
                color = "heat generator",
                y=alt.Y("value"),#title="LCOH [EUR/MWhth]"),
                row="Scenario",
                column= "Sub Scenario 1" if len_sub_sc > 1 else "Sub Scenario"
                ).resolve_scale(x='independent').interactive()
    return chart.resolve_scale(x='independent',y='independent')

def box_plot_overall(source,len_sub_sc,height=250,width=250):
    *_,kwargs_boxplot = viz_spec(len_sub_sc)
    chart = alt.Chart(source,width=width,height=height).mark_boxplot().encode(
                **kwargs_boxplot
                ).resolve_scale(x='independent').interactive()
    return chart.resolve_scale(x='independent',y='independent')
# =============================================================================
def scenario_chart(chart_definions,path,template = Path(tempalte_path).read_text()):
    for i,(flag,func,func_args) in enumerate(chart_definions):
        # print(flag)
        html_code = func(*func_args).to_html(embed_options={'renderer':'svg'},output_div=f"vis_{i}")
        template = template.replace(flag,html_code)
    
    Path(path).joinpath("output_scenario_charts.html").write_text(template)
    return template    
# =============================================================================

def create_random_data(len_sz=2,len_sub_sc=4,vals=3,hg=False,more_val=True,topic="A"):
    
    import string
    szs=string.ascii_lowercase
    
    dfs_sc =[]
    for k in range(len_sz):
        topic = [topic]
        if more_val:
            topic= ['Total Coldstart Costs', 'Total Ramping Costs', 'Total Operational Costs', 'Total Fuel Costs', 'Total CO2 Costs', 'Total Investment Costs (of new build plants and heat storages)', 'Total Investment Costs of (of existing power plants and heat storages)',"Revenues"]
        l=4*k
        heat_generator = f"HG{1+l},HG{2+l},HG{3+l},HG{4+l}".split(",") if hg else [""]
        df = pd.DataFrame(data=np.random.randint(100+k*500,size=(len(topic)*len(heat_generator),)),columns=["value"])
        df["Scenario"] = f"Portfolio {szs[k]}"
        df["topic"] = topic*len(heat_generator)
        if hg:
            df["heat generator"] = len(topic)*heat_generator
        
        cols = ["Sub Scenario"]
        if len_sub_sc>1:
            cols = [f"Sub Scenario {i}" for i in range(1,len_sub_sc+1)]
        
        
        
        for i,col in enumerate(cols):
            dfs = []
            for j in range(vals):
                _df = df.copy()
                _df[col] = f"{col}/{j+1}"
                _df["value"] = np.random.randint(100+k*500,size=(_df.shape[0]))
                dfs.append(_df)
            df = pd.concat(dfs).reset_index(drop=True)
        
        df[df.topic=="Revenues"] *=1
        # if len_sub_sc >5:
        #     df['Sub Scenario 5'] = df[[f"Sub Scenario {i}" for i in range(5,len_sub_sc+1)]].agg('_'.join, axis=1)
        #     df = df.drop([f"Sub Scenario {i}" for i in range(6,len_sub_sc+1)],axis=1)
        
        dfs_sc += [df]
    
    df = pd.concat(dfs_sc)
    return df,len_sub_sc

# =============================================================================
# Global Variable
# =============================================================================
function_mapper={
   '###tot_lcoh1':scatter_single,
   '###tot_cost1':scatter_single,
   '###tot_rev1':scatter_single, 
   '###tot_ue1':scatter_single,
   '###tot_fe1':scatter_single,
   '###tot_co21':scatter_single,
   '###tot_cost_mix1':stacked_bar,
   '###tot_lcoh4':box_plot_overall,
   '###tot_cost4':box_plot_overall,
   '###tot_rev4':box_plot_overall, 
   '###tot_ue4':box_plot_overall,
   '###tot_fe4':box_plot_overall,
   '###tot_co24':box_plot_overall,
   '###tot_lcoh2':scatter_heatgenerators,
   '###tot_cost2':scatter_heatgenerators,
   '###tot_rev2':scatter_heatgenerators, 
   '###tot_ue2':scatter_heatgenerators,
   '###tot_fe2':scatter_heatgenerators,
   '###tot_co22':scatter_heatgenerators,
   '###tot_cost_mix2':stacked_bar_heat_generators,
   '###full_load_hours2': scatter_heatgenerators,
   '###capacities2':scatter_heatgenerators,
   '###tot_lcoh3':box_plot,
   '###tot_cost3':box_plot,
   '###tot_rev3':box_plot, 
   '###tot_ue3':box_plot,
   '###tot_fe3':box_plot,
   '###tot_co23':box_plot,
   '###full_load_hours3': box_plot,
   '###capacities3':box_plot,
   '###efficience1':scatter_heatgenerators,
   '###efficience2':box_plot,
   '###fembyec1':scatter_heatgenerators,
   '###fembyec2':box_plot,
   '###co2embec1':scatter_heatgenerators,
   '###co2embec2':box_plot,
   }


def create_chart_definitions(topic2flag,source,len_sub_sc,function_mapper=function_mapper):
    chart_definition = []
    for topic,flag in topic2flag:
        func = function_mapper[flag]
        df = source[source.topic2.isin(topic)].copy().reset_index()
        chart_definition += [(flag,func,(df,len_sub_sc))]
    return chart_definition
# =============================================================================

# =============================================================================
def main(*args,**kwargs):
    
    len_sub_sc=kwargs["len_sub_sc"]
    vals= kwargs["vals"]
    out_path = kwargs["out_path"]
    chart_definions1=[
       ('###tot_lcoh1',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total LCOH")),
       ('###tot_cost1',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Costs")), 
       ('###tot_rev1',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Revenues")),  
       ('###tot_ue1',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Useful Energy")),  
       ('###tot_fe1',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Final Energy")),
       ('###tot_co21',scatter_single,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions")),  
       ('###tot_cost_mix1',stacked_bar,create_random_data(len_sub_sc=len_sub_sc,vals=vals,hg=False,more_val=True)),
       ]

    chart_definions2=[
        ('###tot_lcoh2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total LCOH",hg=True)),
        ('###tot_cost2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Costs",hg=True)), 
        ('###tot_rev2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Revenues",hg=True)),  
        ('###tot_ue2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Useful Energy",hg=True)),  
        ('###tot_fe2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Final Energy",hg=True)),
        ('###tot_co22',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        ('###tot_cost_mix2',stacked_bar_heat_generators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,hg=True,more_val=True)),
        ('###full_load_hours2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        ('###capacities2',scatter_heatgenerators,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        ]

    chart_definions3=[
        ('###tot_lcoh3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total LCOH",hg=True)),
        ('###tot_cost3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Costs",hg=True)), 
        ('###tot_rev3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Revenues",hg=True)),  
        ('###tot_ue3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Useful Energy",hg=True)),  
        ('###tot_fe3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Final Energy",hg=True)),
        ('###tot_co23',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        # ('###tot_cost_mix2',stacked_bar,create_random_data(len_sub_sc=len_sub_sc,vals=vals,hg=False,more_val=True)),
        ('###full_load_hours3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        ('###capacities3',box_plot,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions",hg=True)),  
        ]
 
    chart_definions4=[
       ('###tot_lcoh4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total LCOH")),
       ('###tot_cost4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Costs")), 
       ('###tot_rev4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Revenues")),  
       ('###tot_ue4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Useful Energy")),  
       ('###tot_fe4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total Final Energy")),
       ('###tot_co24',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,more_val=False,topic="Total CO2 Emissions")),  
       # ('###tot_cost_mix4',box_plot_overall,create_random_data(len_sub_sc=len_sub_sc,vals=vals,hg=False,more_val=True)),
       ]
    chart_definions = chart_definions1 + chart_definions2 + chart_definions3 + chart_definions4
    
    
    scenario_chart(chart_definions,out_path)
    return None


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("Enter Main...")
    main(len_sub_sc=5,
    vals=2,
    out_path = BASE_DIR)

