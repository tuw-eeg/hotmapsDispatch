[![](https://img.shields.io/badge/conda-v0.0-red)](https://gitter.im/)
[![](https://img.shields.io/badge/documentation-v0.0-red)](https://readthedocs.io/)

---
# HotMaps Dispatch Model

<img src="https://github.com/HotMaps/hotmaps_wiki/blob/master/Images/dh_supply/concept.png?raw=true" width="364">

*A web user interface for energy systems modelling* | [GitHub](https://github.com/tuw-eeg/hotmapsDispatch/tree/dev)

---

## Content

* [About](#about)
* [How to intall](#How-to-install)
* [Quick start](#quick-start)
* [Documentation](#documentation)
* [Contributing](#contributing)
* [What's new](#whats-new)
* [Citing Calliope](#citing-calliope)
* [License](#license)
* [Attribution](#Attribution)
---

## About

The HotMaps Dispatch Model is a web user interface to develop energy system models.
It is based on [Pyomo](https://pyomo.readthedocs.io/en/stable/) for modeling and [bokeh](https://docs.bokeh.org/en/0.12.0/index.html) for visualization and interaction. 
The primary focus is flexible model creation with/and without the web user interface, and a high temporal resolution (hourly based) for the optimization. It has also the ability to execute and create many scenarios.  

A model can be fully defined by the web user interaface, with financal and technical details on technologies, demand,electricity,temperature and radiation profiles. You can also define and upload your own data. The Hotmaps Disptach Model takes these inputs and constructs an optimization problem, solves it, and reports back the results. The results are saved as HTML (for visialisation), JSON and EXCEL Files and can be further analyzed.


## How to install
1. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)

2. Download this [repository](https://github.com/tuw-eeg/hotmapsDispatch/archive/dev.zip) and save and unzip the content into your desired loacation

2. open the conda prompt in that location and type following comands 

    a. `conda env create -f environment.yml` 
    
    b. `conda activate hotmapsDispatch`
    
    d. `cd app/modules/common/FEAT/F16`

    c. ``python F16_server.py``

After that your default browser should open and the web user interface will show up

## Quick start 

> **Not implemented todo**

The Hotmaps Dispatch Model can run on Windows, macOS and Linux. 

Installing it is quickest with the `conda` package manager by running a single command: `conda create -c conda-forge -n  python=3.6 hotmapsDispatch`  


See the documentation for more [information on installing](https://hotmapsdispatch.readthedocs.io/en/latest/).

and also some example are [included]()

The [Getting Started Guide](https://hotmapsdispatch.readthedocs.io/en/latest/) is a good place to start and to get a feeling how the model works.


## Documentation

> **Not implemented todo**

Documentation is available on Read the Docs:

* [Read the documentation online (recommended)](https://hotmapsdispatch.readthedocs.io/en/latest/)
* [Download all documentation in a single PDF file](https://hotmapsdispatch.readthedocs.io/en/latest/)

## Contributing

> **Not implemented todo**

To contribute changes:

1. Fork the project on GitHub
2. Create a feature branch to work on in your fork (`git checkout -b new-feature`)
3. Add your name to the AUTHORS file
4. Commit your changes to the feature branch
5. Push the branch to GitHub (`git push origin my-new-feature`)
6. On GitHub, create a new pull request from the feature branch

See our [contribution guidelines](https://github.com/tuw-eeg/hotmapsDispatch/blob/dev/CONTRIBUTING.md) for more information -- and [join us on Gitter](https://gitter.im/tuw-eeg/hotmapsDisptach) to ask questions or discuss code.

## What's new

> **Not implemented todo**

See changes made in recent versions in the [changelog](https://github.com/tuw-eeg/hotmapsDispatch/blob/dev/changelog.md).

## Citing
> **Not implemented todo**

If you use ``HotMaps Disptach`` for academic work please cite:

Autor Name. HotMaps Disptach: a web user interface for energy systems modelling. *Reference. [doi](https://doi.org/)*

## License

Copyright 2019 HotMaps Disptach contributors:
* Michael Hartner
* Richard Büchele
* David Schmidinger
* Michael Gummhalter
* Jeton Hasani

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


## Attribution

The layout and content of this document is partially based on the [calliope-project](https://github.com/calliope-project/calliope/blob/master/README.md).
