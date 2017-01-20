import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def get_colormap(cmap_name, lims):
    if cmap_name == 'symmetric':
        max_abs = np.max(np.abs(lims))
        min_val = lims[0]
        max_val = lims[1]
        if min_val <= 0 <= max_val:
            z_range = max_val - min_val
            n_neg_points = int(abs(min_val)/z_range*100)
            neg_low_limit = 0.5 - abs(min_val)/max_abs/2
            neg_vals = np.linspace(neg_low_limit, 0.5, n_neg_points)
            neg_colors = plt.cm.RdBu_r(neg_vals)
            n_pos_points = int(max_val/z_range*100)
            pos_high_limit = 0.5 + max_val/max_abs/2
            pos_vals = np.linspace(0.5, pos_high_limit, n_pos_points)
            pos_colors = plt.cm.RdBu_r(pos_vals)
            colors = np.vstack((neg_colors, pos_colors))
            cmap = mcolors.LinearSegmentedColormap.from_list('foo', colors)
        elif 0 <= min_val <= max_val:
            cmap = plt.get_cmap('Reds')
        elif min_val <= max_val <= 0:
            cmap = plt.get_cmap('Blues_r')
    else:
        cmap = plt.get_cmap(cmap_name)
    return cmap
