import sys
sys.path.append({path_to_folderbrowser_dir})
import numpy as np
from plothandler import plot_handler_factory
from datahandler import data_handler_factory
from custom_colormap import get_colormap
from sweep import Sweep
import matplotlib.pyplot as plt
import importlib.util

pcols_path = {pcols_path}
spec = importlib.util.spec_from_file_location('', pcols_path)
pcols = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcols)

sweep = Sweep({sweep_path})
sweep.set_pdata(pcols.name_func_dict)
x = sweep.get_data({x_name})
y = sweep.get_data({y_name})
z = {z_data_code}

data_h = data_handler_factory(x, y, z)
fig, ax = plt.subplots()
plot_h = plot_handler_factory(ax, data_h, plot_dim=2)

ax.ticklabel_format(style='sci', axis='both',
                    scilimits={scilimits}, useOffset=False)
ax.set_xlabel({xlabel})
ax.set_ylabel({ylabel})
ax.set_xlim({xlim})
ax.set_ylim({ylim})

im = plot_h.plot(plot_type={plot_2D_type})

# Colorbar
# --------
cmap = get_colormap({cmap_name}, {zlim})
cbar = fig.colorbar(mappable=im)
cbar.formatter.set_powerlimits({scilimits})
im.set_cmap(cmap)
im.set_clim({zlim})
cbar.set_label({zlabel})

plt.tight_layout()

plt.show()
# fig.savefig('foo.pdf', bbox_inches='tight', pad_inches=0.05)
