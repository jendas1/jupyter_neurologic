# NeuroLogic Toolbox
NeuroLogic Toolbox tries to help you to write and analyze neurologic program.
To showcase most important tools, simple tutorial in form of Jupyter notebooks was created.

## How to open jupyter notebook?
[Jupyter notebooks](http://www.jupyter.org) are interactive and rich documents with ability to contain code as well.
To open these notebooks and use all tools inside you need to install various dependencies.

For the most simplest and autonomous way, go for the [vagrant version](#vagrant-version).
Vagrant is a program that creates and run virtual machine with all dependencies automatically installed.

If you use conda, go for the [conda version](#conda-version) that as well as vagrant handles all dependencies.

For most experienced user use [pip version](#pip-version) to install all needed packages to open and run neurologic code.
## Install versions
### Vagrant version
You have to have vagrant installed. To install it, visit https://www.vagrantup.com .
After that, just open terminal with this folder as a current directory and run:
```bash
vagrant up
```
Wait until start of VM and access jupyter notebook on via web browser on port 9999 (exact url will be shown in terminal).
In that window, click on `1. Getting started with NeuroLogic programming.ipynb`. Enjoy!
### Conda version
```bash
# core
conda env create --file environment.yml
source activate neurologic

# neurologic code highlighting
jupyter nbextension install --sys-prefix neurologic_highlighter/
jupyter nbextension enable --sys-prefix neurologic_highlighter/main

# enable displaying neural nets
jupyter nbextension enable --sys-prefix --py widgetsnbextension
```
After installation, run `jupyter notebok` that will open browser. In that window, click on `1. Getting started with NeuroLogic programming.ipynb`. Enjoy!
### Pip version
Note: Java 8 or greater, GrahpViz and Python 3.6 or greater is required.
```bash
# core
pip3 install .

# neurologic code highlighting
jupyter nbextension install neurologic_highlighter/
jupyter nbextension enable neurologic_highlighter/main

# enable displaying neural nets
jupyter nbextension enable --py widgetsnbextension
```
After installation, run `jupyter notebok` that will open browser. In that window, click on `1. Getting started with NeuroLogic programming.ipynb`. Enjoy!

