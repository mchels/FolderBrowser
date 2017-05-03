import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def get_colormap(cmap_name, lims):
    if cmap_name in ('light symmetric', 'dark symmetric', 'symmetric'):
        n_points = 256
        if cmap_name in ('light symmetric', 'symmetric'):
            org_cmap = plt.get_cmap('RdBu_r')
            neg_cmap = get_part_of_cmap(org_cmap, 0.0, 0.5, n_points)
            pos_cmap = get_part_of_cmap(org_cmap, 0.5, 1.0, n_points)
        elif cmap_name == 'dark symmetric':
            neg_color_vals = {
                'red': ((0.0, 0.6, 0.6),
                        (0.6, 0.0, 0.0),
                        (1.0, 0.0, 0.0)),
                'green': ((0.0, 1.0, 1.0),
                          (0.4, 0.8, 0.8),
                          (1.0, 0.0, 0.0)),
                'blue': ((0.0, 1.0, 1.0),
                         (0.8, 0.8, 0.8),
                         (1.0, 0.0, 0.0)),
            }
            neg_cmap = mcolors.LinearSegmentedColormap('', neg_color_vals)
            pos_cmap = plt.get_cmap('afmhot')
        max_abs = np.max(np.abs(lims))
        min_val = lims[0]
        max_val = lims[1]
        z_range = max_val - min_val
        if min_val < 0 < max_val:
            # Negative
            neg_fraction = abs(min_val) / z_range
            n_neg_points = int(neg_fraction * n_points)
            neg_low = 1.0 - abs(min_val)/max_abs
            neg_vals = np.linspace(neg_low, 1.0, n_neg_points)
            neg_colors = neg_cmap(neg_vals)
            # Positive
            pos_fraction = abs(max_val) / z_range
            n_pos_points = int(pos_fraction * n_points)
            pos_high = abs(max_val) / max_abs
            pos_vals = np.linspace(0.0, pos_high, n_pos_points)
            pos_colors = pos_cmap(pos_vals)
            # Combine negative and positive.
            colors = np.vstack((neg_colors, pos_colors))
            cmap = mcolors.LinearSegmentedColormap.from_list('', colors)
        elif 0 <= min_val <= max_val:
            cmap = pos_cmap
        elif min_val <= max_val <= 0:
            cmap = neg_cmap
    else:
        cmap = plt.get_cmap(cmap_name)
    return cmap

def get_part_of_cmap(cmap, low, high, n_points):
    """
    cmap : Colormap instance
        Note that cmap can NOT be a string.
    """
    new_cmap_vals = cmap(np.linspace(low, high, n_points))
    new_cmap = mcolors.LinearSegmentedColormap.from_list('', new_cmap_vals)
    return new_cmap
