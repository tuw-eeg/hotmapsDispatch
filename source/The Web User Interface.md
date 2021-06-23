The Web User Interface
============================

The User Interface is shown in {numref}`UserInterface-fig`. The application is divided into four sections: 

1. {ref}`section:buttonSection`
2. {ref}`section:notificationSection`
3. {ref}`section:outputSection`
4. {ref}`section:dataSection`

```{figure} images/UserInterface.PNG
:height: 450px
:name: UserInterface-fig

The Web User Interface and its sections.
```
In the following subchapters you can find a more detailed description for each mentioned section. 

(section:buttonSection)=
## Button section
{numref}`ButtonSec-fig` gives an overview of the different buttons. 

```{figure} images/buttonSection.PNG
:height: 350px
:name: ButtonSec-fig

Buttons
```
Here you have the choice between 

+ {ref}`subsection:DownloadPPP`: download the created structure to save your progress after calculation
+ {ref}`subsection:UploadPPP`: upload your saved progress or a custom structure into the application
+ {ref}`subsection:RunDM`: run the created model (if  {ref}`subsection:Scenario` is not used )
+ {ref}`subsection:Reset`: reset the view for a better workflow
+ {ref}`subsection:Invest`: start an investment model
+ {ref}`subsection:Scenario`: run the created model through the scenario mode 


(subsection:DownloadPPP)=
### Download Power Plant Parameters
```{figure} images/DownloadButton.PNG
:height: 35px
:name: DownloadButton-fig
:figclass: margin
```

By pressing this button, the browser will try to download a file with the name
`download_input.xlsx` that contains all the information regarding heat producers
and heat storages. The downloaded file has the following format: it consists of five worksheets, whearas these have a certain strucutre, as shown in detail in   {numref}`defaultImagesWhole-fig`. The values would be filled, depending on the parameters which were set. In general, the file has the exact structure of the `default_input_dispatch.xlsx`, described in {doc}`Scenario Generation`. 

```{figure} images/defaultImagesWhole.PNG
:height: 450px
:name: defaultImagesWhole-fig

Download file structure 
```

(subsection:UploadPPP)=
### Upload Power Plant Parameters
```{figure} images/UploadButton.PNG
:height: 35px
:name: UploadButton-fig
:figclass: margin
```
By clicking this button, a pop up window will open and you will be able to
upload an *xlsx file*. That overwrites the content of the web user interface.

```{warning}
The file you upload **must** have the structure as described in {ref}`subsection:DownloadPPP`.
```
When uploading a file, the following points are necessary to know:

* You have to create a file that has the same names for the worksheets (like displayed in {ref}`subsection:DownloadPPP`) and columns
* The worksheet and column names are case sensitive
* You must specify an index column starting with 0
* You can create a maximum of 13 energy carriers

In {numref}`heatGenTypes-tab`, there is a list of available heat generator types. The types with a `*` define not predefined value types which haven't been specified yet. All types of heat pumps are displayed in {numref}`heatPump-tab`, where *variable* COP means a COP depending on the flow temperature, the return temperature and the heat source. In general, depending on the heat generator type, there are predefined values for switch-off, power reduction or sensitivity, which can and should be adapted to achieve different behavior of the heat generators.


```{table} Possible heat generators to choose 
:name: heatGenTypes-tab

| name available (case sensitive) | description                                                  | implementation note                                         |
| ------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| CHP-BP                          | Back Pressure CHP                                            |                                                             |
| CHP-SE                          | Steam Pressure CHP                                           |                                                             |
| boiler                          | heat boiler                                                  |                                                             |
| Solar Thermal                   | Solar thermal plant                                          | At maximum selected radiation profile the solar power plant gives the maximum output |
| Waste treatment                 | waste incineration plants                                    |                                                             |
| Waste Heat*                     | Power plants that work with the unused heat from other power plants |                                                             |
| Geo Thermal*                    | Geo thermal power plant                                      |                                                             |
| Power To Heat*                  | Power to heat devices                                        |                                                             |

```






```{table} Heat pump types and description
:name: heatPump-tab

| heat pumps -  variations | description    | implementation note                                          |
| ------------------------ | -------------- | ------------------------------------------------------------ |
| heat pump                | constant COP   | For temperatures < 0°C, the heat pump doesn’t work           |
| Heat Pump Air            | *variable* COP | As reference it uses the outside temperature                 |
| Heat Pump River          | *variable* COP | As reference it uses the river temperature; for temperatures < 3°C it doesn't work; linerar reduction of power between 6° C and 3°C |
| Heat Pump WasteWater     | *variable* COP | As reference it uses the temperature of waste water          |
| Heat Pump Ind. Wasteheat | *variable* COP | As reference a constant heat source was taken                |


```


(subsection:RunDM)=

###  Run Dispatch Model
```{figure} images/RunModellButton.PNG
:height: 35px
:name: RunModellButton-fig
:figclass: margin
```

By pressing this button, the optimization will start. You will get a progress
shown in the {ref}`section:notificationSection`.
Depending on the structure you create, the optimization will run for about 60 to
120 seconds.
Please be aware that your browser might freeze at that time.
After the solution is found the results are shown in the output section. You can
download then the results via the *buttons* in the  {ref}`section:notificationSection`. Also, if something gets wrong you will get
information there.

```{note}
If unexpected errors occur, please document and send detailed instruction to
reproduce the error and send these instruction with a short problem description.
```

(subsection:Reset)=
### Reset View
```{figure} images/ResetButton.PNG
:height: 35px
:name: ResetButton-fig
:figclass: margin
```
By pressing this button, the notification section and the output section will be
cleared, and you will get a “fresh” view.


(subsection:Invest)=
### Invest
```{figure} images/InvestButton.PNG
:height: 35px
:name: InvestButton-fig
:figclass: margin
```
See {doc}`Investment Mode` for detailed information. 

(subsection:Scenario)=
### Scenario Mode
```{figure} images/ScenarioButton.PNG
:height: 40px
:name: ScenarioButton-fig
:figclass: margin
```
See {doc}`Scenario Mode` for detailed information.


(section:notificationSection)=
## Notification section
```{figure} images/NotificationSection1.PNG
:height: 350px
:name: NotificationSection1-fig

Notification and missing capacity section.
```

In the following you will see some frequent messages (progress and error
information) that might appear in the notification section.
In general, the *missing capacities* section gives you an overview of how much capacity is missing to reach the peak load, like the notification in {numref}`InstalledCapac-fig` shows.

(subsection:PressDownloadPPP)=
### After pressing *Download Power Plant Parameters*
```{figure} images/DownloadButton.PNG
:height: 35px
:name: DownloadButton1-fig
:figclass: margin
```
+ **Nothing to download**
Typically, this occurs when you want to download the initial page, to download
you need to add first a heat generator. 

```{figure} images/NothingToDownload.PNG
:height: 200px
:name: DownloadButton1-fig

Nothing to download
```

+ **Download done**

```{figure} images/DownloadDone.PNG
:height: 200px
:name: DownloadButton1-fig

Download done
```

(subsection:PressUploadPPP)=
### After pressing *Upload Power Plant Parameters*
```{figure} images/UploadButton.PNG
:height: 35px
:name: UploadButton1-fig
:figclass: margin
```

+ **Not a valid file to upload**
```{figure} images/NotValidUpload.PNG
:height: 200px
:name: DownloadButton1-fig

Not a valid file to upload
```
This is shown when you try to upload an filetype other then `.xlsx`.

+ **Fatal Error \@ Update**
```{figure} images/FatalErrorUpdate.PNG
:height: 200px
:name: DownloadButton1-fig

Fatal Error \@ Update
```

This is shown when your file you want to upload has not the needed
structure, see  {ref}`subsection:UploadPPP`.

+ **Upload Done**
```{figure} images/UploadDone.PNG
:height: 200px
:name: DownloadButton1-fig

Upload Done
```

(subsection:PressRunDM)=
###  After pressing *Run Dispatch Model*
```{figure} images/RunModellButton.PNG
:height: 35px
:name: RunModellButton1-fig
:figclass: margin
```
+ **Dispatch in progress, please be patient...**
```{figure} images/DispatchProgress.PNG
:height: 200px
:name: DispatchProgress-fig

Dispatch in progress
```
This can take some time. Typically, also to browser can freeze when the
calculation is done and the results are rendered in the browser.

+ **Calculation is done**
```{figure} images/CalcIsDone.PNG
:height: 200px
:name: CalcIsDone-fig

Calculation is done
```
With these buttons, you can download your results. It might happen that the
page freezes after downloading, please be patient. Therefore it is recommended  to save the link of these files by  (right) clicking on the buttons and choosing *Copy Link*.

```{note}
After 2 hours these links will not work but you can download the files directly if the page freezes and so save  time.
```

+ **No Heat Generators available**
```{figure} images/NoHeatGenAvailable.PNG
:height: 200px
:name: NoHeatGenAvailable-fig

No Heat Generators available
```
This will happen if you haven’t specified any heat generators and wanted to
start the model from the initial page.

+ **The installed capacities are not enough to cover the load**

```{figure} images/InstalledCapac.PNG
:height: 200px
:name: InstalledCapac-fig

Installed capacities are not enough to cover load
```
This will be shown when you haven’t specified enough MW to cover the peak load
It can be checked via the *Missing Capacities* notification on the right sight of the notification section, see {numref}`NotificationSection1-fig`.

+ **Error: Problem proven to be feasable or unbounded**
```{figure} images/ErrProbInfeasable.PNG
:height: 200px
:name: ErrProbInfeasable-fig

Problem proven to be feasable or unbounded
```

This happens typically when constraints cannot be met. This can have a lot of
reasons, its upon to you to think about what could happen.

+ **Error: Please specify the technologies for the investment model**
```{figure} images/ErrInvestmentMode.PNG
:height: 200px
:name: ErrInvestmentMode-fig

Specify  technologies for the investment model
```

This is shown when you enable investment planning but you forgot to select the
heat generators and heat storages to mark, with whom it should do an investment
optimization.

(subsection:Invest)=
### After pressing *Invest*
```{figure} images/InvestButton.PNG
:height: 35px
:name: InvestButton1-fig
:figclass: margin
```
+ **Mark Technologies by pressing “CTRL” + “left mouse”, Rows are marked yellow**

```{figure} images/MarkTechnology.PNG
:height: 200px
:name: MarkTechnology-fig

Marking Technologies
```
As soon as you press this button you will see this information in the
notification section, it tells you that you need to specify for which generators
and storages to do the investment planning. If you don’t mark technologies you
will get the message as described in {numref}`ErrInvestmentMode-fig`.

(subsection:Reset)=
### After pressing other butttons

+ After pressing the `+` button in the *heat producers and heat storage tab*
```{figure} images/HeatProd.PNG
:height: 200px
:name: HeatProd-fig

Open heat producers and storage tab
```
This waiting spinner is especially visible after pressing the `+` button, typically
the browser freezes, so be patient, the *add* section is loading. 

+ After Pressing the `✓ ADD` button in the *heat generator adding section*
**Heat Generator ADDED**
```{figure} images/HeatGenAdded.PNG
:height: 200px
:name: HeatGenAdded-fig

Pressing `✓ ADD` button
```
+ After Pressing the `✓` button in the *Sale-/Electricity Price Tab*

**Sale-/Electricity price Data is set as Default**
```{figure} images/ElPriceSetDefault.PNG
:height: 200px
:name: ElPriceSetDefault-fig

Pressing `✓` button
```
**Sale-/Electricity price Data for *Heat Generator name* is added**

```{figure} images/ElecPriceDataAdded.PNG
:height: 200px
:name: ElecPriceDataAdded-fig

Sale-/Electricity price Data
```
+ After Uploading a file in the *Load Individual Data* tab

**Invalid Filetyp to load \@ Loading External Data**
```{figure} images/InvalidFiletypeExtData.PNG
:height: 200px
:name: InvalidFiletypeExtData-fig

Invalid Filetyp
```
This is shown when you try to upload a filetype that is not `.xlsx` or `.csv`

**Your file has not enough values (please specify 8760 values)**
```{figure} images/NotEnoughValues.PNG
:height: 200px
:name: NotEnoughValues-fig

File has not enough values
```
Your file that you upload has to have the structure as described in {doc}`Inputs`.

**External Data Loaded**
```{figure} images/ExternalDataLoaded.PNG
:height: 200px
:name: ExternalDataLoaded-fig

Fullfilling the structure as described
```
This is shown when the external data has been uploaded.

+ After Pressing the *✓  Save*  button in the *Load Individual Data* tab

**External Data *DataName* added to *profile type* as *DataName_1***

```{figure} images/ExtDataIndividualAdded.PNG
:height: 200px
:name: ExtDataIndividualAdded-fig

External Data *DataName* added
```
This is shown after adding  custom data to the profiles as described
in {doc}`Inputs`.

**n_th/COP - External Data added to *Heat Generator name***
```{figure} images/EtaAndCOPAdded.PNG
:height: 200px
:name: EtaAndCOPAdded-fig

n_th/COP
```
This is shown after adding a custom data for the thermal efficiency to a heat
generator.


(section:outputSection)=
## Output section
See {doc}`Outputs` for general information about the structure of the outputs, or see the specific mode chapters ({doc}`Scenario Mode`, {doc}`Scenario Generation` or in general {doc}`Example Projects`) for detailed information about the specific generated outputs there. 

(section:dataSection)=

## Data section
The data section is for defining the specific data you need for runing the application:
+ defining heat generators and storages
+ setting parameter
+ choosing electricity prices
+ adapting the heat demand
+ implementing individual data

To get detailed description, see {doc}`Inputs`.