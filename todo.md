TODO
====
Need to have
------------


Nice to have
------------
* Figure out what the arguments to autoscale_view do and why they mess up
  image plots.
* Call tight_layout when mpl_layouts are resized by user.
* Consider clearing figure before plotting. Then the Home key on the toolbar may work.
* Consider subclassing FigureCanvas. MplLayout is rather large at the moment.
* Button for "Open Folder".
* Radio button for live update.
* Migrate the rest of the data_loader project where sweep.py came from.
* Use clip=True in colormaps?
* Add separator in QCombobox.
* Compare subtract function with matlab-qd to confirm that they're working as
  intended.
* Allow pseudocolumns to fail silently.
* Add comboboxes to apply function to data. Figure out where to put them first.
* Set column comboboxes back to previous setting if new setting is invalid.
* Add datestamp to title of plot.
* Make a diagram that shows the order in which attributes are updated in
  MplLayout
* Set active layout in FolderBrowser when a widget in PlotControls is clicked.
* Preserve interactive settings (e.g., grid) when updating plots.
* Implement hotkeys on a level above the interactive MPL controls.
* Make toolbar narrower. In the long term consider getting rid of the icons
  altogether, keeping only the numbers that indicate the current point.


Known Issues
------------
* Calling tight_layout() when the axis title is wider than the plot causes the
  axis to shrink rather than fill the figure. This issue is a known bug which
  may be fixed in the 2.0.1 version of Matplotlib:
  https://github.com/matplotlib/matplotlib/issues/5456
* In a Jupyter notebook the magic %load_ext autoreload does not reload the
  classes if they are changed after initialization of the notebook.


Done/Fixed
----------
* fig_canvas -> canvas
* Highlight navigation bar on active qdockwidget.
* Break up FolderBrowser.__init__ into more methods!
* fig_canvas.figure.canvas.draw() -> fig_canvas.draw()
* Shrink the width on the column selector boxes. They expand anyway when
  opened.
* Add button to copy figure.
* RdBu_r colormap is not white at 0 when data is not symmetric about 0. Perhaps
  use OffsetNorm: https://github.com/matplotlib/matplotlib/pull/3858
  Update: RdBu_r is now centered around zero, but the colors saturate at both
  positive and negative values even if the abs(max(negative values)) is much
  smaller than abs(max(positive values)).
* QComboBox pop-ups do not expand to fit their text. Look into this solution:
  http://stackoverflow.com/questions/20554940/qcombobox-pop-up-expanding-and-qtwebkit/20909625#20909625
  or here:
  http://stackoverflow.com/questions/3151798/how-do-i-set-the-qcombobox-width-to-fit-the-largest-item
* Sort QComboBoxes by insertion order.
* Make mpl_layouts take up equal amounts of space at initialization.
* Data is sometimes plotted in the direction it is swept, rather than small ->
  large numbers. Example: sample 3D data gR.
* Something is not working right when custom_tight_layout is used many times on
  an MplLayout that does not change its size. Maybe invisible colorbars are
  created?
* Add pseudocolumns.
* x, y, z limits.
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
