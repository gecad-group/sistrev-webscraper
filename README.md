# SISTREV WebScraper

This is the repo for my PESTI Project: _Development of a web scraper for bibliographic reviews_.

This project consists of a Python Notebook that assists an investigator in the process of systematic reviews.

### Dependencies
This readme file assumes a Linux environment. Most commands will work the same on Windows.

To run this project you should have both python and jupyter installed on your machine.

If on Ubuntu, run:

    $ sudo apt install jupyter-notebook ipython3 python3-venv

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

### How do I run this?

#### Setting up the virtual environment (optional) (recommended)

After cloning the repository, create a new Python Virtual Environment.

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

If running the virtual environment, you need to setup the kernel for the notebook to find the dependencies.

    $ ipython kernel install --user --name=sistrev-env

#### Running the notebook

To run the jupyter instance, do

    $ jupyter notebook

A browser instance should open automatically (If not, click the link)

__!!! If you are using a virtual environment, change the kernel !!!__

1. Open the notebook 
 ![Open the notebook](docs/images/Open%20Notebook.png)

2. On the top bar, click on kernel.
 ![On the top bar, click on kernel.](docs/images/Kernel%20Top%20Bar.png)

3. Change to the kernel created for the environment (sistrev-env) 
 ![Change to the kernel created for the environment (sistrev-env)](docs/images/Select%20the%20kernel.png)

Now you should be able to run the notebook