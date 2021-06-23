(install_conda)=

Installation
=======================

The installation is a three step process:
1. installation of a python environment
2. installation of a solver
3. installation of the HotmapsDispatchModel

## Python environment

The easiest way to install a Python environment is through the **conda** package manager.

You have two *conda* download options:

1. [Anaconda](https://www.anaconda.com/products/individual#Downloads)
2. [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

```{tip}
Whether you use Anaconda or Miniconda, select the most recent version.
```



```{admonition} Anaconda or Miniconda?
Choose Anaconda if you:

- Like to have 1,500 scientific packages automatically installed at once.
- Have the time ---a few minutes  
- And have the disk spaceand -- 3 GB.
- Do not want to individually install each of the packages you want to use.

Choose Miniconda if you:

- Do not have time or disk space to install over 1,500 packages at once.
- Want fast access to Python and the conda commands and you wish to sort out the other programs later.
- Do not mind installing each of the packages you want to use individually.

more see [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#id1)
```



```{tip}
I recommend installing Miniconda, since no packages are installed here and you have a clean base environment
```

### Windows 

The following steps are described for **Anaconda Installation** for Windows

* Go to the [Anaconda Webpage](https://www.anaconda.com/products/individual#Downloads) and choose the right version for your system software

```{figure} images/1.PNG
:height: 300px
:name: my-fig-ref

Anaconda webpage
```

* Follow the installation instructions (described in {numref}`InstallOne-fig`, {numref}`InstallTwo-fig` and {numref}`InstallThree-fig`)

```{figure} images/2.PNG
:height: 350px
:name: InstallOne-fig

Installation wizzard - part one
```

```{figure} images/3.PNG
:height: 350px
:name: InstallTwo-fig

Installation wizzard - part two
```

```{figure} images/4.PNG
:height: 350px
:name: InstallThree-fig

Installation wizzard - finish
```

After installing Anaconda or Miniconda in Windwos you should have the Anaconda Prompt installed

```{figure} images/AnacondaPrompt.png
:height: 70 px
:name: Anaconda-Prompt-win 

Anaconda Prompt after Installing Miniconda or Anaconda in Windows
```

### Linux

The following steps are described for the Miniconda Installation for Linux

- First log into your linux machine and start the terminal


```{figure} images/linux_terminal.png
:height: 350 px
:name: linux_terminal

Login Linux Terminal
```

- Then go to the homepage of [Miniconda](https://docs.conda.io/en/latest/miniconda.html#miniconda) and choose the latest version of miniconda with python3 according to your operating system settings and hardware specification.

  If you are working without a graphical user interface, you can simply download the installer file using the `wget` command.
  All you have to do is copy the appropriate link and enter the following command with the link in your terminal (see yellow mark in {numref}`linux_install_1`) and press 'enter'

  ```
  wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh
  ```

  ```{figure} images/install_1_linux.png
  :height: 150 px
  :name: linux_install_1
  
  Download the installer file 
  ```

- Then execute the downloaded file with the `sh` command and press enter to continue

  ```
  sh Miniconda3-py39_4.9.2-Linux-x86_64.sh
  ```

  ```{figure} images/install_2_linux.png
  :height: 150 px
  :name: linux_install_2
  
  License Agreement
  ```

- 1. Hold 'enter'
  2. type "yes" in the terminal
  3. hit 'enter' again to confirm the installation location

  ```{figure} images/install_3_linux.png
  :height: 200 px
  :name: linux_install_3
  
  Agree with license and confirm installation location
  ```

- 1. After Installation is done type "yes" in the terminal to initialize the miniconda with each login

  2. close and reopen the current shell so the installation take effect 

  ```{figure} images/install_5_linux.png
  :height: 450 px
  :name: linux_install_5
  
  Initialize conda environment with every login 
  ```

- If you login with a new session or open a new shell, you should see  now `(base)` on the left side of the input prompt (see red mark in {numref}`linux_install_4`)

  That means that conda was successfully installed

  ```{figure} images/terminal_with_activated_conda.png
  :height: 200 px
  :name: linux_install_4
  
  Initialize conda environment with every login 
  ```

---

## Solver

To solve an optimisation problem, a solver is necessary. The HotmapsDispatch Model supports the GLPK and the GUROBI solver. Their installation is described in the following chapters.

### GLPK

The GLPK solver is automatically part of the HotmapsDispatchModel installation (see {numref}`install_app`).

To check if you have installed the GLPK solver you can enter the following commands in the Anaconda Prompt / Linux Terminal. 
 - activate the environment

  ```
  conda activate hotmapsDispatch
  ```

 - test if the GLPK Solve is installed

  ```
  glpsol
  ```

If the output is as shown in {numref}`glpk_test` then the GLPK Solver is installed and can be used

```{figure} images/glpk_test.png
:height: 70px
:name: glpk_test

Test GLPK Installation
```

~~~{warning}


If you get a message that the `glpsol` command is not found or not installed, you have to install the GLPK solver manually.

But first try to install the GLPK solver via the conda package manager.
Enter the following commands in your Anaconda Prompt/Linux terminal

```
conda acitvate hotmapsDispatch

conda install -c conda-forge/label/gcc7 glpk
```

If this did not work either, you have to install the GLPK solver manually.

- for Linux you can find the GLPK Solver and the installation instructions at this [link](https://www.gnu.org/software/glpk/#downloading)
- for Windows you can find the exe files and the installation instructions under this [link](http://winglpk.sourceforge.net/). You must then set the environment variables

**In both cases it is necessary to extend the environment variable PATH so that the HotmapsDispatchApplication can access the GLPK solver.**


For Windows open the AnacondaPrompt and type the flowing command

```
rundll32.exe sysdm.cpl,EditEnvironmentVariables
```

Now a new window open ({numref}`path_var_windows`) , enter threre the path to the w64 folder of the solver, depending on where you unpacked the [zip-file](https://sourceforge.net/projects/winglpk/files/latest/download), in this example the w64 folder was extracted in `C:\glpk-4.65\w64`



```{figure} images/path_var_windows.png
:height: 400px
:name: path_var_windows

Setting Path Environment Variable in
```

For Linux you have to modify the .bashrc file. Add `export PATH="${PATH}:${glpk_installation_folder_where_glpsol_is_located}"` to end of the file.  See in  the gurobi example in {numref}`bashrc_gurobi`)

~~~



### Gurobi

> GUROBI has a better performance but is a commercial software, But academic licenses are available for universities and research institutions. 

If you want to install the Gurobi Solver go to the webpage of **Gurobi** and create an account and [login](https://www.gurobi.com/login/) (point a in {numref}`GurobiOne-fig`) and go to *Downloads &Licenses* (point b in {numref}`GurobiOne-fig`) and then click on [*Gurobi Optimizer*](https://www.gurobi.com/downloads/gurobi-optimizer-eula/)  (point c in {numref}`GurobiOne-fig`)

```{figure} images/7.PNG
:height: 350px
:name: GurobiOne-fig

Gurobi Webpage
```

* Click on the button *I Accept the End User License Agreement* ({numref}`GurobiTwo-fig`) and choose the latest version of Gurobi ({numref}`GurobiThree-fig`)

```{figure} images/7a.PNG
:height: 200px
:name: GurobiTwo-fig

Gurobi Optimizer Download
```

---

#### Windows

```{figure} images/8.PNG
:height: 350px
:name: GurobiThree-fig

Gurobi Optimizer Download - Latest version
```

* Follow the installation steps of Gurobi ({numref}`GurobiFour-fig` until {numref}`GurobiNine-fig`)

```{figure} images/9.PNG
:height: 350px
:name: GurobiFour-fig

Gurobi Installation Process - step one
```

```{figure} images/10.PNG
:height: 350px
:name: GurobiFive-fig

Gurobi Installation Process - step two
```

```{figure} images/11.PNG
:height: 350px
:name: GurobiSix-fig

Gurobi Installation Process - step three
```

```{figure} images/12.PNG
:height: 350px
:name: GurobiSeven-fig

Gurobi Installation Process - step four
```

```{figure} images/13.PNG
:height: 350px
:name: GurobiEigth-fig

Gurobi Installation Process - step five
```

```{figure} images/14.PNG
:height: 350px
:name: GurobiNine-fig

Gurobi Installation Process - step six
```


* Then you have to restart your computer so that Gurobi can be installed properly ({numref}`GurobiTen-fig`)


```{figure} images/15.PNG
:height: 200px
:name: GurobiTen-fig

Gurobi Installation Process - step seven
```

---

(bashrc_gurobi)=

#### Linux

- Copy the link of the recent gurobi opimizer for linux from [here](https://www.gurobi.com/downloads/gurobi-optimizer-eula/) and use for example the `wget` command to download the files for the Gurobi opimizer.

```
wget https://packages.gurobi.com/9.1/gurobi9.1.2_linux64.tar.gz
```

```{figure} images/gurobi_zip_linux.png
:height: 150px
:name: Gurobi1_linux

Download the Gurobi Opimizer
```

- Unpack the files into a directory of your choice. I will use `~/myApps` as my destination directory. 

```
tar -xzf gurobi9.1.2_linux64.tar.gz -C ~/myApps
```

```{figure} images/extract_gurobi_files_linux.PNG
:height: 100px
:name: Gurobi2_linux

Extract Gurobi optimizer to installation directory
```

- The Gurobi Optimizer makes use of several executable files. In order to allow these files to be found when needed, you will have to modify a few environment variables:

  - `GUROBI_HOME` should point to your `<installdir>/gurobi912/linux64`.
  - `PATH` should be extended to include `<installdir>/gurobi912/linux64/bin`.
  - `LD_LIBRARY_PATH` should be extended to include `<installdir>/gurobi912/linux64/lib`.

  Users of the `bash` shell should add the following lines to their `.bashrc` files:

  ```{note}
  These paths should be adjusted to reflect your chosen installation directory. In this case it's ~/myApps
  ```

  1. Open the .bashrc file from your home directory 

     ```
     nano ~/.bashrc
     ```
  
     ```{figure} images/bashrc.PNG
     :height: 25px
   :name: Gurobi3_linux
     
     ```
  
   Open the .bashrc file
     ```
  
  2. Use your arrow keys and go to the buttom of the file and copy paste the below lines.
  
     ```
     export GUROBI_HOME=~/myApps/gurobi912/linux64
   export PATH="${PATH}:${GUROBI_HOME}/bin"
     export LD_LIBRARY_PATH="${GUROBI_HOME}/lib"
     export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib" 
     ```
  
     ```{figure} images/bashrc_gurobi1.PNG
     :height: 850px
   :name: Gurobi4_linux
     
   Export the system path variables to get access to gurobi
     ```
  
  3. Then press 'CTRL+X'
  
     ```{figure} images/bashrc_gurobi2.PNG
     :height: 250px
   :name: Gurobi5_linux
     
     ```
  
   Save the changes in .bashrc
     ```
  
  4. Press 'enter'
  
     ```{figure} images/bashrc_gurobi3.PNG
     :height: 250px
     :name: Gurobi6_linux
     
     Save the changes in .bashrc 
     ```

* Close your current terminal window and open a new one after you have made these changes in order to pick up the new settings.

  Type then `gurobi_cl` in your terminal. If you get a message like {numref}`Gurobi7_linux`, then you have successfully installed the Gurobi optimizer

  ```{figure} images/gurobi_cl.PNG
  :height: 350px
  :name: Gurobi7_linux
  
  Test if Gurobi optimizer is installed
  ```

---

#### Set up a Gurobi license 

* After installation, you go to the Gurpobi Webpage again, click *Downloads & Licenses* (point a in {numref}`GurobiElev-fig`), then *Your Gurobi Licenses* (point b in {numref}`GurobiElev-fig`). There you can find your licenses, click on the License ID (point c in {numref}`GurobiElev-fig`)

  If you want to request an academic license click [here](https://www.gurobi.com/downloads/end-user-license-agreement-academic/)

```{figure} images/16.PNG
:height: 350px
:name: GurobiElev-fig

Gurobi Installation Process - step eight
```


* At the bottom of the page there is a *key* for installation. Copy the whole line and enter it in your Anaconda Prompt or in your Linux shell. Then hit 'enter'


```{figure} images/16a.PNG
:height: 350px
:name: GurobiTwelve-fig

Gurobi Installation Process - step nine
```

```{figure} images/gurobi_license.PNG
:height: 250px
:name: Gurobilicense_linux

Gurobi Installation Process - step nine
```

- Test if the license worked by typing `guroib_cl` in your Anaconda Prompt or in your Linux shell

  ```{figure} images/gurobi_cl2.PNG
  :height: 150px
  :name: gurobi_cl2
  
  Test Gurobi with license in Linux
  ```

  ```{figure} images/gurobi_cl3.PNG
  :height: 200px
  :name: gurobi_cl3
  
  Test Gurobi with license in Windows
  ```

---

(install_app)=

## Install HotmapsDispatch Application

1. install a python environment (see {numref}`install_conda`)

2. Download the [repository](https://github.com/tuw-eeg/hotmapsDispatch/archive/master.zip) and save and unzip the content into your desired location

3. open the AnacondaPrompt in that location and type following commands

   a. `conda env create -f environment.yml`

   b. `conda activate hotmapsDispatch`

   c. Start the application`python -m app `for the GUROBI solver or if you want to use the GLPK solver `python -m app --s glpk`




```{warning}
Never close the **Anaconda Promt** during installation process until it is finished!
```

---



## Start  HotmapsDispatch Application

(normal_interface)=

### Normal Interface

To Start the tool after installation ({numref}`install_app`)  open the AnacondaPrompt and type following commands:

1. activate your environment with 

   ```
   conda activate hotmapsDispatch
   ```

   ```{margin} Note
   Replace "path2folder" with the path of the location where you unzip the tool
   ```

2. navigate to the location you unzip the tool by typing 

   ```
   cd path2folder
   
   ```

   

3. type `python -m app `for the GUROBI solver or if you want to use the GLPK solver `python -m app --s glpk` After that your default browser should open and the web user interface will show up 

   ~~~{sidebar} A short hand for this is following command
   ```
   python -m app --s gurobi --p 1234 --o False --n 1
   ```
   ~~~

   

   ~~~{warning}
   If you are working on an operating system without a graphical user interface, you must also set the flag `openbrowser` to False, otherwise the program will try to open a browser and this can lead to an error.
   In addition, you can specify which port should be opened with the paramter `port`. 
   In Linux you can also choose if you like to start a multiprocess so that multiple instances can be open at the same time, with the `numproc` you can specify the number of cores that should be used, 0 means that the application decides how many cpu cores are used depending on how many people acces the web user interface
   An example is the following command that opens a port at 1233, use only one core, use the GUROBI Solver and  do nott open the browser automatically
   
   ```
   python -m app --solver gurobi --port 1234 --openbrowser False --numproc 1
   ```
   ~~~


### Headless  Interface (remote server)

If you have access to a powerful simulation machine, it is very obvious that you want to install and use the HotmapsDispatch model there. However, most of these machines are remote, do not have a graphical user interface and the rights to such machines are usually restricted. In order to access the web interface of the model without granting special rights, it is best to establish a tunnel with the help of which you can then work from your local machine and are able to use the web interface of the model.

1. First you install ({numref}`install_app`) and then start the model on your **<u>remote machine</u>** as described above in {numref}`normal_interface`. 

2. Then you have to create a tunnel to your remote machine. In Windows you can use the Windows Terminal (Download in [Microsoft Store](https://aka.ms/terminal) or [GitHub](https://github.com/microsoft/terminal/releases)) or you can use [Putty](https://www.puttygen.com/download-putty#PuTTY_for_windows) to establish the tunnel.

#### Windows Terminal / Linux Terminal

If you are using the Microsoft Terminal or the Linux Terminal, you can use the following command  to establish a ssh tunnel.  Enter the following command from your local machine that you want to connect to the remote machine that has the application run.

```
ssh -N -f -L local_port:localhost:remote_port username@serverIP
```

```{table} Paramter Description of the ssh tunnel command 
:name: tunnel_params

| name          | meaning                                                      |
| ------------- | ------------------------------------------------------------ |
| `local_port`  | this is the port of your local machine (if you use for example `1111` as your `local_port`, you can excess the WebUserInterface of the hotmapsDispatch Model with your browser at  http://localhost:1111/ |
| `remote_port` | this is the port of the hotmapsDispatch application at your remote machine. You can change the port with the `config.json` file or when you start the the Dispatch Model at the remote machine specify the port with the `p`-flag (i.e. 9666) |
| `username`    | username  of the remote machine                              |
| `serverIP`    | (IP)-Adress of the remote machine                            |


```

#### Putty

If you use Putty you have to make the settings as shown in the {numref}`putty_ssh` in your local machine.  See {numref}`tunnel_params` for the used parameters.

```{figure} images/putty_ssh.PNG
:height: 400px
:name: putty_ssh

Putty settings for ssh tunnel
```



```{warning}
Do not close the window (Microsft Terminal Tab,Linux Terminal or Putty) otherwise the tunnel connection will  be interrupted and you will no longer be able to access the web user interface.
```



```{admonition} Pay attention
If the internet connection is interrupted, the tunnel is also interrupted. When you reconnect, a new session will be accessed and your work will be lost (also during a refresh of the page). To mitigate this risk donwload your work in frequent periods . In case of an interruption you can contiune from the latest state you downloaded before the disconnection or refresh.
```





