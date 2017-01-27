from numpy import nanmin, nanmax

class PlotHandler(object):
    """
    Based on the type of data given in data_handler
    1. Plots on ax a 1D or 2D plot.
    """
    def __init__(self, ax, data_handler):
        self.ax = ax
        self.data_handler = data_handler


class Plot1DHandler(PlotHandler):
    def __init__(self, ax, data_handler):
        super().__init__(ax, data_handler)

    def plot(self, **kwargs):
        return self.plot_1D(**kwargs)

    def plot_1D(self, plot_type=None, **kwargs):
        tdata = self.data_handler.tdata
        ax = self.ax
        ax.plot(tdata[0], tdata[1], **kwargs)


class Plot2DHandler(PlotHandler):
    def __init__(self, ax, data_handler, plot_type=None):
        super().__init__(ax, data_handler)
        self.set_plot_type(plot_type)
        self.def_cmap_str = 'viridis'

    def set_plot_type(self, plot_type):
        assert plot_type in (None, 'imshow', 'pcolormesh')
        if not self.data_handler.data_is_valid:
            plot_type = None
        elif plot_type is not None:
            assert plot_type in ('imshow', 'pcolormesh')
        elif self.data_handler.imshow_eligible:
            plot_type = 'imshow'
        else:
            plot_type = 'pcolormesh'
        self.plot_type = plot_type

    def plot(self, plot_type=None, **kwargs):
        """
        Depends on set_plot_type.
        """
        if plot_type is None:
            plot_type = self.plot_type
            if self.data_handler.imshow_eligible:
                return self.plot_imshow(**kwargs)
            else:
                return self.plot_pcolormesh(**kwargs)
        if plot_type == 'imshow':
            return self.plot_imshow(**kwargs)
        elif plot_type == 'pcolormesh':
            return self.plot_pcolormesh(**kwargs)

    def plot_imshow(self, cmap=None, **kwargs):
        if cmap is None:
            cmap = self.def_cmap_str
        ax = self.ax
        x, y, z = self.data_handler.tdata
        extent = [x[0,0], x[-1,-1], y[0,0], y[-1,-1]]
        imshow_kwargs = {
            'origin': 'lower',
            'interpolation': 'none',
            'aspect': 'auto',
            'extent': extent,
            'cmap': cmap,
        }
        imshow_kwargs.update(kwargs)
        image = ax.imshow(z, **imshow_kwargs)
        return image

    def plot_pcolormesh(self, cmap=None, **kwargs):
        if cmap is None:
            cmap = self.def_cmap_str
        ax = self.ax
        x, y, z = self.data_handler.tdata
        plot_obj = ax.pcolormesh(x, y, z, cmap=cmap, **kwargs)
        return plot_obj


def plot_handler_factory(ax, data_handler, plot_dim, plot_type=None):
    data_dim = data_handler.data_dim
    assert (plot_dim, data_dim) in ((1, 1), (1,2), (2,2))
    if plot_dim == 1:
        return Plot1DHandler(ax, data_handler)
    elif plot_dim == 2 and data_dim == 2:
        return Plot2DHandler(ax, data_handler, plot_type)
