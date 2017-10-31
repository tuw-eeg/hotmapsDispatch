# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:52:51 2017

@author: root
"""

import matplotlib.pylab as plt
import numpy as np
import os
import json
import itertools

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))

path2json = path+r"\AD\F16_input\Solution\solution.json"
path2output = path+r"\AD\F16_input\Output_Graphics"

def plot_solutions(path2json=path2json):
    

    tw = range(1,336+1)  #JAN
    ts = range(730*5,730*5+336+1)   # Summer
        
    try:
        with open(path2json) as f:
            dic = json.load(f)
        
        if os.path.isdir(path2output) == False:
            print("Create Dictionary...")
            os.mkdir(path2output)
            print("Created: "+ path2output)
            
            
    except FileNotFoundError:
        print("\n*********\nThere is no JSON File in this path: "+path2json+"\n*********\n")
        dic={}
        
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111)
    fig4, ax4 = plt.subplots()
    fig5, ax5 = plt.subplots()
    prev_val1 = 0
    prev_val2 = 0        
    for decison_var in list(dic):

        leg=[]
        if type(dic[decison_var]) != str and type(dic[decison_var]) != float:
            for i,val_ind in enumerate(list(dic[decison_var])):
                leg.append(val_ind)
#                print(str(val_ind)+"_____")
                if val_ind == "Heat Demand":
                    ax1.plot(np.array(dic[decison_var][val_ind])[ts],"k")
                    ax2.plot(np.array(dic[decison_var][val_ind])[tw],"k")
#Figure 5
                elif val_ind =="Heat Price" :
                    ax5.plot(dic[decison_var][val_ind])
                    ax5.grid()
                    ax5.set_title(decison_var)
                    ax5.set_xlabel("Time in Hours")
                    ax5.set_ylabel("Heat Price in EUR/MWh")
                    ax5.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    fig5.savefig(path2output+r"\\"+decison_var+".png",dpi=300,bbox_inches='tight')
                    
                elif type(dic[decison_var][val_ind]) != str and type(dic[decison_var][val_ind]) != float :
# Figure 1
                    y1 = prev_val1+np.array(dic[decison_var][val_ind])[tw]
                    ax1.fill_between(tw,prev_val1,y1)
                    prev_val1 = y1
                
                    ax1.grid()
                    ax1.set_xlim([tw[0], tw[-1]])     
#                    ax.set_title("Decision Variable: "+decison_var)
                    ax1.set_title(decison_var)

                    ax1.set_xlabel("Time in Hours")
                    ax1.set_ylabel("")
                    ax1.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    fig1.savefig(path2output+r"\\"+decison_var+"_winter.png",dpi=300,bbox_inches='tight')
# Figure 2
                    y2 = prev_val2+np.array(dic[decison_var][val_ind])[ts]
                    ax2.fill_between(ts,prev_val2,y2)
                    prev_val2 = y2
                
                    ax2.grid()
                    ax2.set_xlim([ts[0], ts[-1]])     
#                    ax.set_title("Decision Variable: "+decison_var)
                    ax2.set_title(decison_var)

                    ax2.set_xlabel("Time in Hours")
                    ax2.set_ylabel("")
                    ax2.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    fig2.savefig(path2output+r"\\"+decison_var+"_summer.png",dpi=300,bbox_inches='tight')
            
            
            
                else:
#Figure 3 
                    ax3.set_title(decison_var)
                    ax3.bar(i,round(dic[decison_var][val_ind],2))
                    ax3.legend(leg,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    fig3.savefig(path2output+r"\\"+decison_var+"absolut_bar_chart.png",dpi=300,bbox_inches='tight')
#Figure 4                    
                    labels = list(dic[decison_var])
                    sizes = np.array(list(dic[decison_var].values()))/sum(dic[decison_var].values())
                    mask = sizes>0
                    labels = list(itertools.compress(labels, mask))
                    sizes = sizes[mask]
                    explode = 0.1*np.ones((len(labels),))
                    ax4.pie(sizes, explode = explode,labels=labels, autopct='%1.1f%%',
                    shadow=False, startangle=90)
                    ax4.axis('equal')
                    fig4.savefig(path2output+r"\\"+decison_var+"bar_bar_chart.png",dpi=300,bbox_inches='tight')
        else:
            print("")
#            ax.set_title("Decision Variable: "+decison_var)
#            ax.set_title(decison_var)
#            ax.text(0.5, 0.5, decison_var + ": " + str(dic[decison_var]),
#            verticalalignment='center', horizontalalignment='center',
#            transform=ax.transAxes,
#            color='red', fontsize=22)
#            ax.set_xlim([0,1])
#            ax.set_ylim([0,1])
#            ax.axis('off')
#            fig.savefig(path2output+r"\\"+decison_var+"_"+time+".png",dpi=300,bbox_inches='tight')
            


#%%
plot_solutions()