Scenario Mode
============================

If you want to do sensitivity analyses you have to start a run for each parameter you want to vary, save the results and then change the value and run the calculation again, save the results and so on.

As you can see, this is a very time consuming and painstaking process.

To simplify this process there is the Scenario Mode.

For example if you like to include more sensitivity parameters such as different $CO_2$ price values, then the easiest way to calculate is the so-called **scenario mode**. It gives you the opportunity to use more and different sensitivities and calculate it at once.

---

## How to create a scenario

The scenario mode is designed on the basis of a two-level tree model. {numref}`scenario_mode_concept` illustrates this concept.

```{figure} images/GUI_Scenario_Creation.svg
:height: 750px
:name: scenario_mode_concept

Scenario Mode Design
```

If you want to create a scenario tree like  {numref}`scenario_mode_concept`, then creating it through the GUI is easy. Otherwise, if you want more sensitivity levels then it is simpler to create them via explicit excel files and/or use the Scenario Management Tool , which is described in {doc}`Scenario Generation`.

> A possible task for the use of the Scenario Mode could be the following:
>
> The aim is to examine 3 technology portfolios (Portfolio a, Portfolio b and Portfolio c). 
>
> - For Portfolio a the impact of different CO2 prices should be investigated.
> - For Portfolio b the effect of different energy prices should be analyzed , and 
> - For Portfolio c the effects of differnt interest rates and different system temperatures should be studied 
>
> This task can be described as a 2-stage scenario tree ({numref}`example_scenario_mode`,) and is simple to create with the integrated graphical user interface. 

```{figure} images/Example_Scenario_Mode.svg
:height: 750px
:name: example_scenario_mode

Example of a Scenario Tree that can be simple and easy create through the GUI 
```

When using the GUI to create a scenario, do the following steps

+ Enabling of the scenario mode, {numref}`enableScenMode-fig`

```{figure} images/enablingScenarioMode.PNG
:height: 450px
:name: enableScenMode-fig

Enabling the scenario mode
```
+ Choosing a name for the new scenario and sub-scenario, and apply the names, {numref}`nameScen-fig`. 
  + Choose a name for your scenario
  + Press *apply* 
  + Then two messages should appear that your chosen name was adapted
  + The chosen name replaced the *default* filling

```{figure} images/nameScenario.PNG
:height: 450px
:name: nameScen-fig

Name the scenarios 
```
+ Choose the names for the sub-scenarios, similar like the step for renaming scenarios, {numref}`nameSubScen-fig`.

  + Go to *parameters* and choose a name for the first sub-scenario
  + Press *apply*
  + Then two messages should appear that your chosen name was adapted
  + The chosen name replaced the *default_sub* filling
  
```{warning}
   Don't choose a name for a sub-scenario with an `underline _` symbol involved, as it may cause trouble, see {doc}`Scenario Generation`.
```

```{figure} images/nameSubScenario1.PNG
:height: 450px
:name: nameSubScen-fig

Name the sub-scenarios 
```
```{tip}
   Choose a fitting name for your subscenarios, like in {numref}`nameSubScen-fig`, as the name symbolizes which parameter was modified.
```
+ If you like to add more sub-scenarios with the same parameter modification as the first sub-scenario was made, then do the following steps:
  + Go to *parameters* and chose a name for the next sub-scenario
  + Press *add*,  see {numref}`nameSubScen2-fig`
  + Then two messages should appear that your chosen sub-scenario was added
  + Via drop down, you should see now all the sub-scenarios you already created
  + Then the one parameter which differs through all sub-scenarios has to be set, so go to the one where the parameter has to be adapted (in this example it would be the $CO_2$ price value) and choose the correct value,  see {numref}`nameSubScen3-fig`.
  + If the values are adapted, then you should see the different values in the parameter box you have changed by clicking on one of  the sub-scenarios, see {numref}`nameSubScen4-fig`.

  ```{warning}
  If you have made a mistake and you want to have a different value for a sub-scenario, the text field with the sub-scenario name must be empty before you change the value with apply, otherwise the application thinks that you want to make a new sub-scenario and since the name is already assigned, an error will occur that you cannot rename an already existing sub-scenario.
  ```
```{figure} images/nameSubScenario2.PNG
:height: 300px
:name: nameSubScen2-fig

Creating additional sub-scenarios, step one
```

```{figure} images/nameSubScenario3.png
:height: 300px
:name: nameSubScen3-fig

Creating additional sub-scenarios, step two
```

```{figure} images/nameSubScenario4.png
:height: 300px
:name: nameSubScen4-fig

Creating additional sub-scenarios, step three
```
+ If you have created all the necessary sub-scenarios, you need to click on *Run Dispatch Model* to calculate your individual scenario. On the right side of the button you can see the calculation process, depending on the number of sub-scenarios, see {numref}`RunScenarioMode-fig`. 

```{figure} images/CalculationSubScen.png
:height: 300px
:name: RunScenarioMode-fig

Run the created scenario.
```

```{figure} images/profile_chosen.png
:height: 450px
:name: profileChosen-fig

Choose your profiles for each category.
```

```{figure} images/HeatGen_add.png
:height: 450px
:name: HeatGen-fig

Add heat generators to run your model.
```

```{figure} images/MissingCap_adapt.png
:height: 450px
:name: MissingCapacity-fig

Avoid missing capacities.
```

```{warning}
  Make sure you 

   + have filled up all the categories in *profiles* with a valid profile ({numref}`profileChosen-fig`), for details see {doc}`Inputs`.
   + have created a Heat Generator, {numref}`HeatGen-fig` (follow the steps in the figure, for detailed information about the steps, especially step 5, see {doc}`The Web User Interface`.
   + have chosen the right installed capacity so that no missing capacity is possible, {numref}`MissingCapacity-fig`.

Otherwise you won't be able to run the model and get resuts, as you get error messages before.
```



```{tip}
After you have created your scenarios via the web interface, you can press *Download* so that you save your progress and do not lose the system you have created.

After you have pressed *Download*, a zip is downloaded.

The zip file has the following structure:


        scenario_inputs.zip
            ├───Scenario 1
            │       Sub Scenario 1.xlsx
            │       Sub Scenario 2.xlsx
            │		<>...xlsx
            ├───Scenario 2
            │       Sub Scenario a.xlsx
            │       Sub Scenario b.xlsx
            │       Sub Scenario c.xlsx
            │		<>...xlsx
            └───<>
            │		...xslx  
            ...



- The folders describe the scenarios and the output files is also named after them.

- Within each folder (scenario) you will find Excel files that describe the sub-scenarios and also the outputs files are named after them.

The system for the scenario tree described in {numref}`example_scenario_mode` has folowing structure  

        scenario_inputs.zip
            ├───Porfolio a
            │       CO2 High.xlsx
            │       CO2 LOW.xlsx
            │
            ├───Porfolio b
            │       Energy Carrier Prices HIGH.xlsx
            │       Energy Carrier Prices LOW.xlsx
            │       Energy Carrier Prices MID.xlsx
            │
            └───Porfolio c
                    Interest Rate 10%.xlsx
                    Interest Rate 2%.xlsx
                    System Temperatur HIGH.xlsx
                    System Temperatur LOW.xlsx
  

Having this structure in mind, you can define your scenarios manually via Excel files without the web user interface.
A more detailed description of the an automated process of this can be found in {doc}`Scenario Generation`.

You can upload the zip file again and read the scenarios into the model check/change values and calculate the scenario tree at once.

To upload a scneario tree you must always proceed as follows:

1. Enable Scenario Mode
2. Upload Power Plant Paramters 
3. select zip file and press ok


```

---



(section:scenariomodeOutput)=

## Scenario Mode Output

There are two options of saving the output of the scenario calculation:

+ Data will be saved automatically in this path, if you have everything locally saved: 
  `...\Dispatch\app\modules\common\AD\F16_input\static` with the following structure:

**scenario mode folder:** one folder per scenario, which is named by the exact date and time when the scenario was run.

Inside that folder, the structure looks always like this:

  1. *scenario folders*: folders named by the created main scenarios (number of folders depends on the number of created scenarios)
     1. *sub-scenario folders*: folders inside the main folder defined by the created sub-scenarios (one or more); here you always find data and generator files with **single value**, which is explained in {numref}`ExcelFiletable-ref`.
     2. *HTML file* : will be created automatically, it shows you the results via plots and separates it, depending on the different scenarios you made.

The structure is shown in {numref}`scenOutput-fig`.

```{figure} images/scenOutput.png
:height: 250px
:name: scenOutput-fig

Folder structure of scenario output.
```


```{table} Output data type in Excel
:name: ExcelFiletable-ref
|                | single value                                                 | hourly value                                                 |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Data           | big categorties/ indicators (e.g. whole costs, not specified for each technology) ; data is displayed as one value per indicator | big categorties/ indicators (e.g. whole costs, not specified for each technology) ; data is displayed as hourly values for the whole year |
| Generator Data | categories per technology (e.g. $CO_2$ price per technology or installed capacity); data is displayed as one value per indicator | categories per technology (e.g. $CO_2$ price per technology or installed capacity); data is displayed as hourly values for the whole year |
```

+ Data can be downloaded separately from the server by clicking at *Download ZIP File*, see {numref}`CalcDone-fig`.

```{figure} images/CalcDone.png
:height: 200px
:name: CalcDone-fig

Download possibility after calculation.
```

Inside the zip-file, you find as many folders as scenarios were created. Here, you don't have explicitly an HTML file or other excel output files as option one has. Inside these folders you find as many folders as you have created sub-scenarios.  


