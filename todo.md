TODO
====
High Priority
-------------
* mplcursor.


Medium Priority
---------------
* Allow multiple functionalities when loading a data folder:
  1) Load the specified path directly (keyword direct_load=True?).
  2) List the subfolders and let the user pick one of them to load.
* Make class+hotkey to copy all figures in a combined canvas.
  Add support for 2+1 layouts
* Write tests for DataHandler and PlotHandler.
* Make test that compares data and meta loaded with and without pandas.
* Add support for updating plot in PlotHandler instead of redrawing every time.
* Consider how to handle case where 3D data is loaded into DataHandler without
  a z array.
* Change limit for when the displayed x y z values change to scientific
  notation.
* Show error in place of plot if calculation of columns fails.
* Handle exponential label so it does not overlap with title or axis labels.
* Handle large numbers in a different way than turning them into nan. They mess
  up, e.g., max and min functions. Use clip=True in colormaps?
* Make update_cmap in MplLayout into its own class.
* Figure out what the arguments to autoscale_view do and why they mess up
  image plots. Also consider removing ax.relim
* Add separator in QCombobox.
* Compare subtract function with matlab-qd to confirm that they're working as
  intended.
* Show that GUI is loading using decorators.
* Can polyfit handle nan? http://stackoverflow.com/questions/28647172/numpy-polyfit-doesnt-handle-nan-values


Low Priority
------------
* Show path to data in Ctrl+T dialog.
* Use relative imports?
* Make setup.py file. You must do it in a way that allows you to uninstall the
  package again!
* Decorators in separate file?
* Let user specify path for Sweep class. This can make data not in the
  matlab-qd format compatible with the FolderBrowser.
* Load attributes in TextForCopying as a dictionary instead of individual
  arguments.
* Add comboboxes to apply function to data. Figure out where to put them first.
* Radio button for live update.
* Migrate the rest of the data_loader project where sweep.py came from.
* Make a diagram that shows the order in which attributes are updated in
  MplLayout
* Set active layout in FolderBrowser when a widget in PlotControls is clicked.
* Implement hotkeys on a level above the interactive MPL controls.
* Preserve interactive settings (e.g., grid) when updating plots.
* Consider making filelistwidget update automatically when files are added.


Do when MPL 2.0 is in anaconda
------------------------------
* Wrap title text. This isn't really useful for MPL < 2.0 since tight_layout
  will continually shrink the figure if the title or labels are wider or higher
  than the figure.
* Remove border right of colorbar in image plots. Wait for mpl 2.0.
* Increase font size for labels. You can't really do this before MPL 2.0
  introduces better tight_layout functionality.


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
* Use absolute path in template.py?
* Specify path to names_func_dict file instead of supplying the dictionary
  itself. By doing this names_func_dict can be reloaded with a hotkey.
* Move repository to github.
* Find icon for GUI.
* Current in 2016-10-20#003 doesn't plot correctly.
* Ctrl+t hotkey only works when one of the plots is 3D.
* Data sometimes isn't rotated correctly for imshow, ex:
  2014_10_14_cnt_gen5_cellF\data\device_FI_january2015\2015-01-27#002
* Load data faster by using pandas' read_csv. I can't use numpy's fromfile since
  it provides no speed-up if a separator must be supplied.
* Make sure that np.copy makes a deep copy.
  I'm not 100% sure about the deep/shallow distinction, but the numpy docs show
  that the array created by copying array a is not changed if we change array a
  which is sufficient for me.
* In pcols.py when subtracting a fit the data is transposed twice I think,
  causing it to be displayed wrongly.
* Add support for 2D data in Handler3DData and call the class something else
  like DataHandler.
* Abort functions in data_handler if data is invalid.
* Remove unnecessary argments to super.
* Add support for plotting using pcolor.
* Put autoscale_view in common_update.
* Set column comboboxes back to previous setting if new setting is invalid.
* Only one entry is shown in file_list for sweeps with the same name.
* 1D plot crashes in some conditions. Probably when a pcol is selected which
  cannot be calculated. Solution: Revert selected column in set_data_for_plot
  if it is invalid.
* Make all text selectable.
* F5 updates file_list
* Use scientific notation on colorbar (+axes?) given some conditions on data.
* Fix large_to_nan.
* Make function to update FileListWidget.
* Set values over 1e30 to NaN to prevent them from blowing up the colorscale.
* Move arr_varies_monotonically_on_axis to the Sweep class.
* Hotkey for "Open Folder".
* Add datestamp to title of plot.
* Call tight_layout after GUI window has opened. Currently the figure call
  tight_layout before GUI has opened so it doesn't fill the canvas.
* Allow pseudocolumns to fail silently.
* Make toolbar narrower. In the long term consider getting rid of the icons
  altogether, keeping only the numbers that indicate the current point.
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


Ignored
-------
* The following is incorrect. The size is not typically 2MB. Copy images in
  lower resolution. Currently some are 2MB which is too much.
* Consider clearing figure before plotting. Then the Home key on the toolbar
  may work. This turned out not to be necessary.
* Consider subclassing FigureCanvas. MplLayout is rather large at the moment.
  I've split MplLayout but I have not subclassed FigureCanvas.
* Call tight_layout when mpl_layouts are resized by user.
  I don't think this can be done in a robust way in QT and it's a rather
  useless feature.
* Fix the showEvent issue. Plot should be updated on resize and initialization.
  The GUI is initialized with no sweep selected. Thus, there is no need to
  update plot on initialization.
* Plot is redrawn on EVERY showEvent including minimizing the window and
  opening it again. I think it should only be redrawn on the FIRST showEvent.
