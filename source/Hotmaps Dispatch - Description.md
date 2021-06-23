Hotmaps Dispatch - Description
============================

![concept.png](https://raw.githubusercontent.com/HotMaps/hotmaps_wiki/master/Images/dh_supply/concept.png)

The HotMaps Dispatch Model is a web user interface to develop energy system models. It is based on [Pyomo](https://pyomo.readthedocs.io/en/stable/) for modeling and [bokeh](https://docs.bokeh.org/en/0.12.0/index.html) for visualization and interaction. The primary focus is flexible model creation with/and without the web user interface, and a high temporal resolution (hourly based) for the optimization. It has also the ability to execute and create many scenarios.

A model can be fully defined by the web user interaface, with financal and technical details on technologies, demand,electricity,temperature and radiation profiles. You can also define and upload your own data. The Hotmaps Disptach Model takes these inputs and constructs an optimization problem, solves it, and reports back the results. The results are saved as HTML (for visualisation), JSON and EXCEL Files and can be further analyzed.



This documentation will give you detailed information about the usage and technical background of the Dispatch Model. 