TODO
====
Need to have
------------
* Prepare FolderBrowser to be loaded from Jupyter notebook. Figure out why the
  Jupyter kernel crashes after instantiating a couple of FolderBrowsers, even
  if it is %reset between instantiations.
* Add pseudocolumns.


Nice to have
------------
* Add dropdown for colormap.
* Figure out what the arguments to autoscale_view do and why they mess up
  image plots.
* Call tight_layout when mpl_layouts are resized by user.
* Make mpl_layouts take up equal amounts of space at initialization.
* Make hotkeys work.
* Consider clearing figure before plotting. Then the Home key on the toolbar may work.
* Consider subclassing FigureCanvas. MplLayout is rather large at the moment.
* Add button to copy figure.
* Button for "Open Folder".
* Radio button for live update.
* Break up FolderBrowser.__init__ into more methods!
* Migrate the rest of the data_loader project where sweep.py came from.


Done
----
*DONE Allow mpl_layouts to be arranged horizontally.
*DONE Prevent duplicate figures to open when FolderBrowser is started from
  Jupyter notebook.
*DONE Add support for plotting 2D data.
    *DONE Enable control of x- and y-axis with the comboboxes. Right now only
      the z combobox has effect when plotting 2D.
    *DONE Add colorbar.
*DONE Add plot title, axis labels.
*DONE Show message in statusbar that data is 1D and can't be plotted as image.
*DONE I think I have to make comboBoxes into a class of its own.
*DONE The items in the file list are not sorted. They are now.
