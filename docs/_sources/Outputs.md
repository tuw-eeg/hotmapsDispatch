Outputs
=======================

## General structure

In general, you always get the excel data sheets for your model which you created, and you can analyze plots which are generated too. It is helpful to save the output after running the model, as it could be overwritten by refreshing the page or if an error occurs.{numref}`portfolioWhole-fig` show the structure of the output. 


```{figure} images/portfolioWhole.PNG
:height: 350px
:name: portfolioWhole-fig

Possible output when creating many portfolios and the corresponding sub folders
```


## Structure in detail

Depending on the mode you chose, the output varies a little bit concerning the structure. See the subchapters below for detailed information or go straight to the extra chapters for more information on the rest when picking these modes.

### Input Excel File

```{figure} images/portfolioOutputInput.PNG
:height: 250px
:name: portfolioOutputInput-fig

Input excel file which will be created for output
```

As displayed in {numref}`portfolioOutputInput2-fig`, the structure of the input file, which will be generated, is the same as already mentioned in {doc}`The Web User Interface`. There you will find all the input parameters you put in the model for calculation.


```{figure} images/portfolioOutputInput2.PNG
:height: 250px
:name: portfolioOutputInput2-fig

Input excel file structure
```

### Output HTML File

```{figure} images/portfolioOutputHtml.PNG
:height: 250px
:name: portfolioOutputHtml-fig

Output HTML file which will be created for output
```

If you open the HTML file, you find various analyses of the calculation and different graphs. Like {numref}`portfolioOutputHTML3-fig` shows, you have some options where you can take a closer look to the results. {numref}`portfolioOutputHTML4-fig`to   {numref}`portfolioOutputHTML4-fig`then shows the graphs for the first option, the *Thermal Power Energy Mix*. If you want to filter the results, you can click in the legend on the functions you don't want to see in the graph, and it will get grey in the legend and disappear in the graph, see {numref}`portfolioOutputHTML5-fig` for instance. This option you also have for the other graphs which have a legend beside, like comparing  {numref}`portfolioOutputHTML7-fig` and {numref}`portfolioOutputHTML8-fig`.


```{figure} images/portfolioOutputHTML3.PNG
:height: 100px
:name: portfolioOutputHTML3-fig

Output HTML file options
```

```{figure} images/portfolioOutputHTML4.PNG
:height: 500px
:name: portfolioOutputHTML4-fig

Energy mix and electricity price
```

```{figure} images/portfolioOutputHTML5.PNG
:height: 350px
:name: portfolioOutputHTML5-fig

Filtering options through the legend
```

```{figure} images/portfolioOutputHTML6.PNG
:height: 350px
:name: portfolioOutputHTML6-fig

Output HTML file - heat price graph
```

```{figure} images/portfolioOutputHTML7.PNG
:height: 350px
:name: portfolioOutputHTML7-fig

Filtering option for heat storages - one function visible
```

```{figure} images/portfolioOutputHTML8.PNG
:height: 350px
:name: portfolioOutputHTML8-fig

Filtering option for heat storages - two functions visible
```

Other sections which have the same graphs, are the *TPE* for summer and winter, specifically, if you like to filter for seasonal data.

The next section, where different graphs are used, is the *Load Duration Curve* section, see {numref}`portfolioOutputHTML9-fig`.


```{figure} images/portfolioOutputHTML9.PNG
:height: 350px
:name: portfolioOutputHTML9-fig

Load duration curve graph - also filter possibilities
```

The following figures ( {numref}`portfolioOutputHTML10-fig` to {numref}`portfolioOutputHTML13-fig`) show the output pie charts of *TPE and plant capacities*. Every pie chart has a corresponding bar chart on the right side, like the example in {numref}`portfolioOutputHTML11-fig` shows, and also filtering options like described before. 

```{figure} images/portfolioOutputHTML10.PNG
:height: 350px
:name: portfolioOutputHTML10-fig

Pie chart for thermal generation mix
```

```{figure} images/portfolioOutputHTML11.PNG
:height: 350px
:name: portfolioOutputHTML11-fig

Bar chart for thermal generation mix
```

```{figure} images/portfolioOutputHTML12.PNG
:height: 350px
:name: portfolioOutputHTML12-fig

Pie chart for installed capacities
```

```{figure} images/portfolioOutputHTML13.PNG
:height: 350px
:name: portfolioOutputHTML13-fig

Pie chart for full load hours
```

The section *Specific capital costs of IC* shows details about the costs through a bar chart and a corresponding table underneath the chart, like shown (here seperately) in {numref}`portfolioOutputHTML14-fig` and {numref}`portfolioOutputHTML11-fig`. 

```{figure} images/portfolioOutputHTML14.PNG
:height: 400px
:name: portfolioOutputHTML14-fig

Bar chart for cost details
```

```{figure} images/portfolioOutputHTML15.PNG
:height: 350px
:name: portfolioOutputHTML15-fig

Table for cost details
```

The last two sections contain on the one hand all details for the *$CO_2$ emissions*, {numref}`portfolioOutputHTML16-fig`and {numref}`portfolioOutputHTML17-fig`, and on the other hand a summary of the results through a table, see {numref}`portfolioOutputHTML18-fig`. 

```{figure} images/portfolioOutputHTML16.PNG
:height: 350px
:name: portfolioOutputHTML16-fig

Bar chart for $CO_2$ emissions
```

```{figure} images/portfolioOutputHTML17.PNG
:height: 250px
:name: portfolioOutputHTML17-fig

Table for $CO_2$ emissions
```

```{figure} images/portfolioOutputHTML18.PNG
:height: 350px
:name: portfolioOutputHTML18-fig

Table for total results
```


### Output Excel Files

```{figure} images/portfolioOutputExcel.PNG
:height: 250px
:name: portfolioOutputExcel-fig

Output excel files which will be created for output
```

Depending on the variety of sensitivities you made, you get different number of output excel files. For example, like shown from {numref}`portfolioOutputExcel2-fig` to {numref}`portfolioOutputExcel6-fig`, you can easily filter *values*, *heat generators*, *time* or *topic* to filter the necessary values for you. Just go to *Data*, then click on *filter* and the columns can be filtered for the necessary parameters. 

```{figure} images/portfolioOutputExcel2.PNG
:height: 350px
:name: portfolioOutputExcel2-fig

Output excel file structure - differs on the column number 
```

```{figure} images/portfolioOutputExcel3.PNG
:height: 350px
:name: portfolioOutputExcel3-fig

Filter possibility - topic
```

```{figure} images/portfolioOutputExcel4.PNG
:height: 350px
:name: portfolioOutputExcel4-fig

Filter possibility - time
```

```{figure} images/portfolioOutputExcel5.PNG
:height: 350px
:name: portfolioOutputExcel5-fig

Filter possibility - heat generator
```

```{figure} images/portfolioOutputExcel6.PNG
:height: 350px
:name: portfolioOutputExcel6-fig

Filter possibility - value
```