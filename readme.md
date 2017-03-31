FolderBrowser
=============

Description
-----------
This project provides a GUI for visualizing data acquired with the [matlab-qd](https://github.com/qdev-dk/matlab-qd) framework by Anders Jellinggaard.
The gui itself is a Python implementation of the [gui from matlab-qd](https://github.com/qdev-dk/matlab-qd/tree/master/%2Bqd/%2Bgui).

Installation
------------
All packages used for FolderBrowser are included in the Anaconda distribution.
Get it from [https://www.continuum.io/downloads](https://www.continuum.io/downloads) with the newest Python 3 version.
Note that versions newer than Python 3.5 may cause issues, see section Known Issues.

If you already have Anaconda installed (with Python 3.5) but the packages are not up to date, simply run
````
conda update anaconda
````
from the terminal to update the packages.

When you have all packages installed run `example.py` in the `examples` directory.


Requirements
------------
* Python 3+ (tested with version 3.5)
* Matplotlib (tested with version 1.5.3)
* PyQt 5 (tested with version 5.6)
* Numpy (tested with version 1.11)


Optional packages
-----------------
* Pandas (improves loading times by a factor 2-10x, tested with version 0.18.1)


Hotkeys
-------
| Key           | Function      |
| ------------- | ------------- |
| F2            | Copy code for figure to clipboard |
| F5            | Reload file list |
| F6            | Reload pseodocolumn file |
| Ctrl-c        | Copy figure as png |
| Ctrl-t        | Show figure properties in dialog as copyable text |
| Ctrl-w        | Close window |
| Ctrl-shift-o  | Open folder containing data |


Known Issues
------------
2017-03-31: Anaconda's Python 3.6 distribution may give an error "DLL load failed: The specified module could not be found." In this case downgrade the distribution to Python 3.5 using
````
conda install python=3.5
````
from the terminal.
