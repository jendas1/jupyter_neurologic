# Prerequisites
Python 3.6 or greater is required.
# Install
### Pip version
```bash
# core
pip3 install .

# neurologic code highlighting
jupyter nbextension install neurologic_highlighter/
jupyter nbextension enable neurologic_highlighter/main

# enable displaying neural nets
jupyter nbextension enable --py widgetsnbextension
```
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
### Vagrant version
# TODO add short info about every option (https://www.vagrantup.com)
```bash
vagrant up
```
Access jupyter notebook on port 9999.
# Run
```
jupyter notebook
```
After that, browser window is opened. In that window, click on `neurologic.ipynb`. Enjoy!
