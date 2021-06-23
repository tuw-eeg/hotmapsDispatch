Scenario Generation
============================

If you want to calculate many sensitivities or create a scenario tree with more than 2 levels, it is better to use the Scenario Management Tool instead of the WebUser Interface. The advantage of the Scenario Management Tool is that you can create many scenarios at once.

With this tool you can create a multi level scenario tree, that has always the same number of sensitivities for each sub-scenario. You can decide how many sensitivities you want to have per sub-scenario.

In {numref}`smt_example`  you can see an example. Shown is a two-level-scenario-tree with 2 scenarios,  2 sensitivities for sub-scenario-one and 4 sensitivities for sub-scenario-two, it also shows how the files are named.

```{figure} images/SMT_example.svg
:height: 800px
:name: smt_example

Example of a 2 level scenario tree 
```

In principle can the hotmpasDIspatch Application also calculate with different numbers of sensitivities per sub-scenario (see {doc}`Scenario Mode`), but mostly you want to calculate the same sensitivities over a sub-scenario.


## Scenario Generation - steps for manual process

if you don't use the the Scenario Management Tool you can create your own multi level scenario tree manually with excel files.

```{note}
   To generate scenarios through this way, the folder structure has to look like this:
   + scenario folders, named by the scenario itself
   + sub-scenario files, named by the sub-scenarios; inside the scenario folder 
```

When you want to create multi level scenario tree manually you make the following steps:

1. Copy the already existing excel files of the current sub-scenarios (e.g. when downloading the calculation in {doc}`Scenario Mode`, you already get the first sub-scenarios)

2. Rename the new excel files with an underline symbol. 

    ```{tip}
       The specialized structure of the sub-scenario file names helps you define the level of the scenario tree and also helps you visualize the plots for the output (See {numref}`file_name_convention`) . 
    ```
    
3. Inside each excel file for each sub-scenario, the particular sensitivities have to be changed in value.

4. If you have defined and created all necessary coupled sub-scenarios and main scenarios, and you want to calculate your model, then you have to create a *zip-file* out of all the main scenario folders (e.g. Portfolio a,Portfolio b,... all have to be put into a *zip-file*)

5. Then, go to the WebUser Interface again and upload this *zip-file*

    ```{tip}
       Before uploading your created *zip-file*, do the following steps:
       + Refresh the page, so all scenarios which were created before are deleted and no collision can cause problems
       + Enable the scenario mode
       + Then push the button *Upload Power Plant Parameters* and choose your *zip-file*
    ```
    
6. Before running the calculation, you can check the values which you have adapted in the WebUser Interface, if they were changed properly.

7. Push the button *Run Dispatch Model* for calculation

(file_name_convention)=

## File name convention and its effect

The naming of the files describe the **s**cenario **t**ree **l**evels (**STL**)  and also how the output chart will look. The file starts with the scenario name, followed by the sub-scenario name separated by an underscore. (see {numref}`smt`).  

```{figure} images/SMT.svg
:height: 800px
:name: smt

A general 2 level scenario tree (**STL2**) and the file names of the different runs
```

In the next chapters some examples of scenario trees  are shown , and the effect of the file naming to the output charts  is explained. 

```{note}
Each data point in the charts represents a dispatch run and the input is described by an Excel file. The filename of the Excel file follows a naming convention that is specified in the heading and described in the tables 
```



### STL1 (`a_b.xlsx`)

```{figure} images/SUB1.svg
:width: 1000px
:name: graph_sub1

Example of an one level scenario tree 
```

```{table} Naming and meaning of the structure for excel files for a 1 level scenario tree
:name: 2SZ1SUB

| name | position in naming | Number of sensitivities  and possible meaning         | meaning for the plot(for system wide indicators) | meaning  for the plot (for indicators by technologies)[^footnote2] |
| ---- | ------------------ | -------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------ |
| a    | Scenario           | 2 technology portfolio (Portfolio a,  Portfolio b) | columns[^footnote1]                              | rows[^footnote1]                                             |
| b    | Sub Scenario 1     | 2 $CO_2$ Prices (Sub Scenario/1 ;Sub Scenario/2 )  | x-axis and color of the data point                                           | columns[^footnote1]                                          |

[^footnote2]: (The x-axis is always reserved for the heat generators, therefore the scenarios and sub-scenarios must be adjusted accordingly)
[^footnote1]: (for each row and column a figure is created)
```

```{figure} images/2SZ_1SUB.svg
:height: 400px
:name: 2SZ1SUB_system_inidicator

Plot example of a one level scenario tree ({numref}`graph_sub1`) for a system indicator
```

```{figure} images/2SZ_1SUB_HG.svg
:height: 640px
:name: 2SZ1SUB_hg_inidicator

Plot example of a one level scenario tree ({numref}`graph_sub1`) for an indicator by technologies
```



### STL2(`a_b_c.xlsx`)

```{figure} images/SUB2.svg
:width: 1000px
:name: graph_sub2

Example of a two level scenario tree 
```

```{table} Naming and meaning of the structure for excel files for a 2 level scenario tree
:name: 2SZ2SUB

| name | position in naming | Number of sensitivities  and possible meaning                   | meaning for the plot(for system wide indicators) | meaning  for the plot (for indicators by technologies)[^footnote2] |
| ---- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------ |
| a    | Scenario           | 2 technology portfolio (Portfolio a,  Portfolio b)           | columns[^footnote1]                              | rows[^footnote1]                                             |
| b    | Sub Scenario 1     | 2 $CO_2$ Prices (Sub Scenario 1/1 ;Sub Scenario 1/2 )        | rows[^footnote1]                              | columns[^footnote1]                                          |
| c    | Sub Scenario 2     | 2 Energy Carrier Prices (Sub Scenario 2/1 ;Sub Scenario 2/2 ) | x-axis and color of the data point                                 | shape of the data point                                                        |

[^footnote2]: (The x-axis is always reserved for the heat generators, therefore the scenarios and sub-scenarios must be adjusted accordingly)
[^footnote1]: (for each row and column a figure is created)
```

```{figure} images/2SZ_2SUB.svg
:height: 640px
:name: 2SZ2SUB_system_inidicator

Plot example of a two level scenario tree ({numref}`graph_sub2`) for a system indicator
```

```{figure} images/2SZ_1SUB_HG.svg
:height: 640px
:name: 2SZ2SUB_hg_inidicator

Plot example of a two level scenario tree ({numref}`graph_sub2`) for an indicator by technologies
```



### STL3(`a_b_c_d.xlsx`)

```{figure} images/SUB3.svg
:width: 1500px
:name: graph_sub3

Example of three level scenario tree (For the sake of a better overview, not all edges and nodes of the graph are displayed.)
```

```{table} Naming and meaning of the structure for excel files for a 3 level scenario tree
:name: 2SZ3SUB

| name | position in naming | Number of sensitivities  and possible meaning                   | meaning for the plot(for system wide indicators) | meaning  for the plot (for indicators by technologies)[^footnote2] |
| ---- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------ |
| a    | Scenario           | 2 technology portfolio (Portfolio a,  Portfolio b)           | rows[^footnote1]                                 | rows[^footnote1]                                             |
| b    | Sub Scenario 1     | 2 $CO_2$ Prices (Sub Scenario 1/1 ;Sub Scenario 1/2 )        | columns[^footnote1]                              | columns[^footnote1]                                          |
| c    | Sub Scenario 2     | 2 Energy Carrier Prices (Sub Scenario 2/1 ;Sub Scenario 2/2 ) | x-axis and color of the data point                                 | color of the data point                                                        |
| d    | Sub Scenario 3     | 2 Interest Rates (Sub Scenario 3/1 ;Sub Scenario 3/2 )       | shape of the data point                                            | shape of the data point                                                        |

[^footnote2]: (The x-axis is always reserved for the heat generators, therefore the scenarios and sub-scenarios must be adjusted accordingly)
[^footnote1]: (for each row and column a figure is created)
```

```{figure} images/2SZ_3SUB.svg
:height: 640
:name: 2SZ3SUB_system_inidicator

Plot example of a three level scenario tree ({numref}`graph_sub3`) for a system indicator
```

```{figure} images/2SZ_3SUB_HG.svg
:height: 640px
:name: 2SZ3SUB_hg_inidicator

Plot example of a three level scenario tree ({numref}`graph_sub3`)for an indicator by technologies
```



### STL4  (`a_b_c_d_e.xlsx`)

```{figure} images/SUB4.svg
:width: 1000px
:name: graph_sub4

Example of four level scenario tree (For the sake of a better overview, not all edges and nodes of the graph are displayed.)
```


```{table} Naming and meaning of the structure for excel files for a 4 level scenario tree
:name: 2SZ4SUB

| name | position in naming | Number of sensitivities  and possible meaning                   | meaning for the plot(for system wide indicators) | meaning  for the plot (for indicators by technologies)[^footnote2] |
| ---- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------ |
| a    | Scenario           | 2 technology portfolio (Portfolio a,  Portfolio b)           | rows[^footnote1]                                 | rows[^footnote1]                                             |
| b    | Sub Scenario 1     | 2 heat demands (Sub Scenario 1/1 ;Sub Scenario 1/2 )         | columns[^footnote1]                              | columns[^footnote1]                                          |
| c    | Sub Scenario 2     | 2 years (Sub Scenario 2/1 ;Sub Scenario 2/2 )                | x-axis                                           | color of the data point                                      |
| d    | Sub Scenario 3     | 2 Interest Rates (Sub Scenario 3/1 ;Sub Scenario 3/2 )       | color of the data point                          | drop down menu                                               |
| e    | Sub Scenario 4     | 2 $CO_2$ certificate prices (Sub Scenario 4/1 ;Sub Scenario 4/2) | shape of the data point                          | shape of the data point                                      |

[^footnote2]: (The x-axis is always reserved for the heat generators, therefore the scenarios and sub-scenarios must be adjusted accordingly)
[^footnote1]: (for each row and column a figure is created)
```

```{figure} images/2SZ_4SUB.svg
:height: 700px
:name: 2SZ4SUB_system_inidicator

Plot example of a four level scenario tree ({numref}`graph_sub4`) for a system indicator
```

```{figure} images/2SZ_4SUB_HG.svg
:height: 700px
:name: 2SZ4SUB_hg_inidicator

Plot example of a four level scenario tree ({numref}`graph_sub4`) for an indicators by technologies
```

As you can see in {numref}`2SZ4SUB_hg_inidicator` , there are duplicate data points that are indistinguishable. To make the data points distinctive, `Sub Scenario 3` is added as a drop-down menu from a 4-level scenario tree upwards. This allows all data points to be distinctive. The illustration in  {numref}`2SZ4SUB_hg_inidicator_dropdown` shows this approach.

```{figure} images/2SZ_4SUB_HG_1.png
:height: 700px
:name: 2SZ4SUB_hg_inidicator_dropdown

Plot Example of a four level scenario tree ({numref}`graph_sub4`) for Indicators by technologies with a drop-down menu 
```



### STL5 (`a_b_c_d_e_f.xlsx`)

```{figure} images/SUB5.svg
:width: 1000px
:name: graph_sub5

Example of five level scenario tree (For the sake of a better overview, not all edges and nodes of the graph are displayed.)
```

```{table} Naming and meaning of the structure for excel files for a 5 level scenario tree
:name: 2SZ5SUB

| name | position in naming | Number of sensitivities  and possible meaning                   | meaning for the plot(for system wide indicators) | meaning  for the plot (for indicators by technologies)[^footnote2] |
| ---- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------ |
| a    | Scenario           | 2 technology portfolio (Portfolio a,  Portfolio b)           | rows[^footnote1]                                 | rows[^footnote1]                                             |
| b    | Sub Scenario 1     | 2 heat demands (Sub Scenario 1/1 ;Sub Scenario 1/2 )         | columns[^footnote1]                              | columns[^footnote1]                                          |
| c    | Sub Scenario 2     | 2 years (Sub Scenario 2/1 ;Sub Scenario 2/2 )                | x-axis                                           | color of the data point                                      |
| d    | Sub Scenario 3     | 2 Interest Rates (Sub Scenario 3/1 ;Sub Scenario 3/2 )drop down menu | drop down menu                                   | drop down menu                                               |
| e    | Sub Scenario 4     | 2 $CO_2$ certificate prices (Sub Scenario 4/1 ;Sub Scenario 4/2) | color of the data point                          | shape of the data point                                      |
| f    | Sub Scenario 5     | 2 Energy Carrier Prices (Sub Scenario 5/1 ;Sub Scenario 5/2) | shape of the data point                          | color or shape   [^footnote3]                                |

[^footnote2]: (The x-axis is always reserved for the heat generators, therefore the scenarios and sub-scenarios must be adjusted accordingly)
[^footnote1]: (for each row and column a figure is created)
[^footnote3]: (random selection)
```

```{figure} images/2SZ_4SUB_HG.svg
:height: 700px
:name: 2SZ5SUB_system_inidicator

Plot example of a five level scenario tree ({numref}`graph_sub5`) for a system indicator
```

As you can see in {numref}`2SZ5SUB_system_inidicator` , there are duplicate data points that are indistinguishable. To make the data points distinctive, `Sub Scenario 3` is added as a drop-down menu from a 5-level scenario tree upwards. This allows all data points to be distinctive. The illustration in  {numref}`2SZ5SUB_dropdown` shows this approach.

```{figure} images/2SZ_5SUB_1.png
:height: 700px
:name: 2SZ5SUB_dropdown

Plot Example of a five level scenario tree ({numref}`graph_sub5`) for a system indicator with a drop-down menu 
```

The illustration in {numref}`2SZ5SUB_hg_inidicator`  shows that from a 5-level scenario tree onwards, even the addition of a drop-down menu does not make it possible to visually create a clear allocation of the data points. Of course, one can now create a drop-down menu for each additional sub-scenario, which would solve the problem with the ability to distinguish the data points, but the chart itself would not become clearer, nor would it be possible to publish analogue graphics (for papers, for example).  

```{figure} images/2SZ_3SUB_HG.svg
:height: 700px
:name: 2SZ5SUB_hg_inidicator

Plot example of a five level scenario tree ({numref}`graph_sub5`) for an indicators by technologies
```

---



```{warning}
It is not advisable to calculate scenario trees deeper than 5 levels ({numref}`graph_sub5`), as the results of the sensitivities are no longer straightforward to visualise and therefore can no longer be easily analysed and interpreted.
```



## Scenario Management Tool 

The main advantage of using the Scenario Management Tool is to only use two kind of files, whereas you separate which values stay constant and which parameters will change, this safes time and effort.

Two files are being used for generating scenarios ({numref}`scenGenFiles1-fig`):

+ {ref}`section:defaultInput`
+ {ref}`section:Scenarios`

```{figure} images/scenGenFiles1.PNG
:height: 150px
:name: scenGenFiles1-fig

Necessary excel files for scenario generation.
```
(section:defaultInput)=
### `default_input_dispatch.xlsx`

All values/parameters will be defined here which won't change for this run. There are predefined worksheets, which are shown in {numref}`defaultInput-fig`.

```{figure} images/defaultInput.PNG
:height: 35px
:name: defaultInput-fig

Possible options for setting default values.
```
Each worksheet has empty gaps to be filled up if necessary, as shown in {numref}`defaultImagesWhole-fig`.

```{figure} images/defaultImagesWhole.PNG
:height: 450px
:name: defaultImagesWhole-fig

Predefined values to set.
```
(section:Scenarios)=
### `scenarios.xlsx`

+ All values/parameters, which will be changed, will be added in the worksheets in {numref}`ScenariosSheetsWhole-fig`.

```{figure} images/ScenariosSheetsWhole.PNG
:height: 25px
:name: ScenariosSheetsWhole-fig

Predefined worksheets to fill in.
```

```{warning}
Delete all the values/parameters you don't want to vary and define individual names for each scenario/sub-scenario and coupled ones. If you don't want to make any specifications at a worksheet, however you have to put in the names of your *portfolios* and the number in the first column, like in {numref}`ScenariosSheetsHeatGen3-fig`. The other columns you can left blank.
```

You can choose the number of portfolios which you want to create and the type of heat generators. In {numref}`ScenariosSheetsHeatGen3-fig` there are different portfolios with its heat generators filled in each column (here *A*,*B*,*C* etc.). The different shades of the pink boxes just emphasize the different portfolios, but in general you are free to create as many as needed.

```{warning}
All the different worksheets in excel can be almost chosen freely, depending on the different sensitivities you want to calculate. However, the names have to start the same way as predefined in the {ref}`section:defaultInput`:
+ All worksheets here have to start with the specific sensitivity category (e.g.: for different electricity prices you need the *Profile* worksheet)
+ Then, add a minus afterwards and  a corresponding name for your sensitivity case (e.g.: *Profile - Electricity Prices* or *Data - interest rate*) .
```

```{figure} images/ScenariosSheetsHeatGen3.PNG
:height: 220px
:name: ScenariosSheetsHeatGen3-fig

Heat generators and portfolios definition.
```

```{tip}
If you want to use the same technologies for all portfolios (but e.g.: with different capacities), to get a better overview of the output plots, you should name the heating technologies equally for each portfolio, but with a **space character** afterwards the name, so that it will be treated as different values while runing the model, but to be plotted as the same technology to be comparable.
```

In {numref}`ScenariosSheetsEnergyCarrier2-fig` you can define the specified name and energy carrier for each portfolio.

```{figure} images/ScenariosSheetsEnergyCarrier2.PNG
:height: 250px
:name: ScenariosSheetsEnergyCarrier2-fig

Energy carrier definition.
```
Defining different heat storages is possible like in {numref}`ScenariosSheetsHeatStor2-fig`. 

```{figure} images/ScenariosSheetsHeatStor2.PNG
:height: 170px
:name: ScenariosSheetsHeatStor2-fig

Heat storage definition.
```
You can define a sensitivity for *profile*, which will be adapted like in {numref}`ScenariosSheetsProfile-fig`.

```{figure} images/ScenariosSheetsProfile.PNG
:height: 350px
:name: ScenariosSheetsProfile-fig

Examples of profile sensitivities.
```

For defining different sensitivities (e.g.: different gas prices, held in light and dark green in the figure), you have to adapt the following worksheet in {numref}`ScenariosSheetsPriceEmission2-fig`. It depends on the number of sensitivities how many "green boxes" you have create in that worksheet.

```{figure} images/ScenariosSheetsPriceEmission2.PNG
:height: 400px
:name: ScenariosSheetsPriceEmission2-fig

Sensitivity setting via price definition.
```
Additionally, you can define an *interest rate*, like in {numref}`ScenariosSheetsData2-fig`.

```{figure} images/ScenariosSheetsData2.PNG
:height: 200px
:name: ScenariosSheetsData2-fig

Interest rate definition.
```
```{tip}
If you want coupled sensitivities, you have to add the one you want to couple to the one which is defined in a worksheet. For instance, if you want to combine the effect of electricity prices with $CO_2$ prices, then you add a column for $CO_2$ prices in the worksheet where you defined the electricity price sensitivity.
```

If everything is defined correctly, then `dispatchScenarioGenerator.py` has to be executed, see {numref}`scenGenFiles2-fig`.

```{warning}
   Inside the python file `dispatchScenarioGenerator.py`:
Change the path of your input path for your dat-files, which should be the one where you cloned the repo in the beginning.
```
```{figure} images/scenGenFiles2.PNG
:height: 150px
:name: scenGenFiles2-fig

Execute the python file
```

+ After the code run, it creates an *output* folder, where you have as many folders as generated scenarios. Inside them, you find all your excel files with the sub-scenarios and varying sensitivities. 
+ To calculate the model, a *zip-file* has to be created out of all the portfolio folders. Then you can upload it, like described in this chapter before, with the button *Upload Power Plant Parameters* and check again, if the values you changed, fit. 
+ The last step is the calculation via the button *Run Dispatch Model* 