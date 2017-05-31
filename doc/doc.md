DOC
================================================================================

Concepts
--------------------------------------------------------------------------------
### Column
A column is an array of raw data from a (real or virtual) instrument, e.g., "time in seconds" or "voltage on DMM". Depending on context "column" may mean only a "raw" column or both "raw" and pseudocolumns.

### Pseudocolumn
A pseudocolumn is an array of data derived from a column, e.g., "conductance in units of e^2/h" instead of Siemens.
Pseudocolumns can be arbitrarily complex and may involve, e.g., differentiating or integral transforming multiple columns or other pseudocolumns.

### Sweep
`get_data`

Main window
--------------------------------------------------------------------------------
The FolderBrowser window contains a number of MplLayouts (=Matplotlib Layouts)
and a FileList to contain the sweep names.

MplLayout (Matplotlib Layout)
--------------------------------------------------------------------------------
The MplLayouts contain an instance of Plotcontrols (for controlling plot limits, column etc.), a Matplotlib canvas with a figure and one axes containing the plot, and a toolbar with the default Matplotlib tools (zoom, pan etc.).
The Matplotlib toolbar of the currently active MplLayout is highlighted in blue. The figure in the active MplLayout can be copied either as a png file (hotkey Ctrl-C) or as Python code (hotkey F2). The copied Python code is generated from a template and is intended to be portable so that it can be run from anywhere on the computer it was generated on. This means that all paths in the code are hard-coded. Note that the title is not included in the Python code since the algorithm that determines the title line breaks is not reliable or robust against changes in resolution, font size, etc.

PlotControls
--------------------------------------------------------------------------------
The PlotControls bar at the bottom of the MplLayout contains
- three drop-down menus for selecting the desired (pseudo-)column,
- a drop-down menu for selecting the colormap,
- a drop-down menu for selecting 2D plot type (Auto, imshow or pcolormesh),
- three text fields for selecting limits on the plot,
- one text field for selecting the aspect ratio.


The MplLayouts and the FileList are "dockable" meaning they can be detached from the main window and moved around.

