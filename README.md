# SISTREV WebScraper

This is the repo for my PESTI Project: _Development of a web scraper for bibliographic reviews_.

This project consists of a Python Notebook that assists an investigator in the process of systematic reviews.

>[!NOTE]
>__The app has been updated!__
>
>Now there is a web version of the datacleaner module. It should be [available](http://192.168.2.68:8502) if connected to GECAD's internal network.

### Dependencies
This readme file assumes a Linux environment, but instructions for Windows will also be provided

To run this project you should have both python and jupyter installed on your machine.

#### Linux

On most Linux distributions, Python 3 should already be installed. If not, add the package python3 to the following commands.

If on Ubuntu/Debian, run:

    $ sudo apt install jupyter-notebook ipython3 python3-venv

If on Fedora, run:
    
    $ sudo yum install jupyter-notebook ipython3 python3-venv

You can check if both are installed with

    $ python3 --version
    Python 3.10.12

And

    $ jupyter --version
    Selected Jupyter core packages...
    IPython          : 7.31.1
    ipykernel        : 6.7.0
    ipywidgets       : 6.0.0
    jupyter_client   : 7.1.2
    jupyter_core     : 4.9.1
    jupyter_server   : not installed
    jupyterlab       : not installed
    nbclient         : 0.5.6
    nbconvert        : 6.4.0
    nbformat         : 5.1.3
    notebook         : 6.4.8
    qtconsole        : not installed
    traitlets        : 5.1.1

_**Note**: The '$' indicates the commands you should run. I have provided the outputs of some commands on my machine_

---

#### Windows

Install Python from the [official website](https://www.python.org/).

After the installation, open the "Command Prompt" or "PowerShell". Check if python is installed with:

    > python --version

To install Jupyter, run:

    > pip -m install jupyter

*Note: 
You don't need to install Jupyter now, you can install later, after [installing the dependencies](#installing-dependencies). 
This way it is installed only on the virtual environment and there's no need to configure the kernel*

To check if jupyter installed successfully, run:
    
    > jupyter --version

---

### Running the project

In this section, instructions on running the project are provided. 

#### Setting up the virtual environment (optional)

After cloning the repository, you can create a new Python Virtual Environment so the dependencies are only installed on the project.

    .../webscraper$ python3 -m venv .venv

To activate the virtual environment run

    $ source .venv/bin/activate

Or, on Windows (needs to run on PowerShell):
    
    > .venv\bin\Activate.ps1

Now a tag about the environment should appear on the terminal prompt

    (.venv) .../webscraper$

#### Installing dependencies

The project has all packages it depends on _requirements.txt_

    $ pip install -r requirements.txt

#### Setting up the kernel for the notebook (required if running a venv)

If running the virtual environment and jupyter was installed outside it, you need to configure the kernel for the notebook to find the dependencies.

    $ ipython kernel install --user --name=sistrev-env

#### Running the notebook

To run the jupyter instance, do

    $ jupyter notebook

A browser instance should open automatically (If not, click the link)

__!!! If you are using a virtual environment with jupyter installed globaly, change the kernel !!!__

1. Open the notebook 
![Open the notebook](docs/images/Open%20Notebook.png)


2. On the top bar, click on kernel.
![On the top bar, click on kernel.](docs/images/Kernel%20Top%20Bar.png)


3. Change to the kernel created for the environment (sistrev-env) 
![Change to the kernel created for the environment (sistrev-env)](docs/images/Select%20the%20kernel.png)

Now you should be able to run the notebook by opening sistrev.ipynb
