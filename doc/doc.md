User Guide
================================================================================


Concepts
--------------------------------------------------------------------------------
### Column
A column is an array of raw data from a (real or virtual) instrument, e.g., "time in seconds" or "voltage on DMM". Depending on context "column" may mean only a "raw" column or both "raw" and pseudocolumns.

### Pseudocolumn
A pseudocolumn is an array of data derived from a column, e.g., "conductance in units of e^2/h" instead of Siemens.
Pseudocolumns can be arbitrarily complex and may involve, e.g., differentiating or integral transforming multiple columns or other pseudocolumns.
Pseudocolumns are calculated lazily in the FolderBrowser, i.e., not until requested from the drop-down menus.

### Sweep
The Sweep class stores data (as a structured Numpy array) and meta (as a dictionary) from a sweep. The Sweep class can also load a pseudocolumn file with `set_pdata` such that pseudocolumns can also be accessed. To access data columns you can use either the data or pdata attribute or the method `get_data` which looks in both data and pdata:
```
a_sweep = Sweep(<path to sweep directory>)
time = a_sweep.data['time']
conductance = a_sweep.pdata['conductance']
conductance2 = a_sweep.get_data('conductance')
```
The `conductance` and `conductance2` arrays will be identical in this example.

### Widget
A widget is a basic element in the Qt framework. From the Qt website:

> Widgets are the primary elements for creating user interfaces in Qt. Widgets can display data and status information, receive user input, and provide a container for other widgets that should be grouped together. A widget that is not embedded in a parent widget is called a window.

In FolderBrowser MplLayouts are widgets, PlotControls is a widget, the drop-down menus inside PlotControls are also widgets etc.


Main window
--------------------------------------------------------------------------------
The FolderBrowser window contains a number of MplLayouts (=Matplotlib Layouts)
and a FileList to contain the sweep names.
The MplLayouts and the FileList are "dockable" meaning they can be detached from the main window and moved around.


MplLayout (Matplotlib Layout)
--------------------------------------------------------------------------------
A MplLayout contains
- an instance of Plotcontrols (for controlling plot limits, column etc.),
- a Matplotlib canvas with a figure and one axes containing the plot,
- a toolbar with the default Matplotlib tools (zoom, pan etc.).

Information about the Matplotlib toolbar can be found
[here](https://matplotlib.org/users/navigation_toolbar.html)
The Matplotlib toolbar of the currently active MplLayout is highlighted in blue. The figure in the active MplLayout can be copied either as a png file (hotkey Ctrl-C) or as Python code (hotkey F2). The copied Python code is generated from a template and is intended to be portable so that it can be run from anywhere on the computer it was generated on. This means that all paths in the code are hard-coded. Note that the title is not included in the Python code since the algorithm that determines the title line breaks is not reliable or robust against changes in resolution, font size, etc.

The algorithm for updating the plot proceeds as follows:
- When a value is changed in the widgets in PlotControls a callback function is executed.
- The callback function schedules a redraw in the MplLayout if one is not already scheduled (to avoid redrawing multiple times).
- The callback function changes the state of the MplLayout, potentially calling other state-changing methods.
- The figure is redrawn based on the state of the MplLayout.

The figure in an MplLayout can be edited manually from a Jupyter notebook.


PlotControls
--------------------------------------------------------------------------------
The PlotControls bar at the bottom of the MplLayout contains
- three drop-down menus for selecting the desired (pseudo-)column,
- a drop-down menu for selecting the colormap,
- a drop-down menu for selecting 2D plot type (Auto, imshow or pcolormesh),
- three text fields for selecting limits on the plot,
- one text field for selecting the aspect ratio.
