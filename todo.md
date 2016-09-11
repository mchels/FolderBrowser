TODO
====
Need to have
------------
* Add pseudocolumns.
* x, y, z limits.


Nice to have
------------
* Figure out what the arguments to autoscale_view do and why they mess up
  image plots.
* Something is not working right when custom_tight_layout is used many times on
  an MplLayout that does not change its size. Maybe invisible colorbars are
  created?
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
* Hotkeys.


Known Issues
------------
* Calling tight_layout() when the axis title is wider than the plot causes the
  axis to shrink rather than fill the figure. This issue is a known bug which
  may be fixed in the 2.0.1 version of Matplotlib:
  https://github.com/matplotlib/matplotlib/issues/5456
* RdBu_r colormap is not white at 0 when data is not symmetric about 0. Perhaps
  use OffsetNorm: https://github.com/matplotlib/matplotlib/pull/3858
* Data is sometimes plotted in the direction it is swept, rather than small ->
  large numbers. Example: sample 3D data gR.
* In a Jupyter notebook the magic %load_ext autoreload does not reload the
  classes if they are changed after initialization of the notebook.


Done
----
* Prepare FolderBrowser to be loaded from Jupyter notebook. Figure out why the
  Jupyter kernel crashes after instantiating a couple of FolderBrowsers, even
  if it is %reset between instantiations.
* Add dropdown for colormap.
* Label on colorbar never changes from its initial value.
* Allow mpl_layouts to be arranged horizontally.
* Prevent duplicate figures to open when FolderBrowser is started from
  Jupyter notebook.
* Add support for plotting 2D data.
    * Enable control of x- and y-axis with the comboboxes. Right now only
      the z combobox has effect when plotting 2D.
    * Add colorbar.
* Add plot title, axis labels.
* Show message in statusbar that data is 1D and can't be plotted as image.
* I think I have to make comboBoxes into a class of its own.
* The items in the file list are not sorted. They are now.
