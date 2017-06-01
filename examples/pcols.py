import numpy as np
from functools import partial


name_func_dict = {
    'backgate': {'label': 'Backgate voltage (V)'},
    'MC': {'label': 'Mixing chamber temperature (K)'},
}

def MC_mK(data, pdata, meta):
    return data['MC'] * 1000

name = MC_mK.__name__
func = partial(MC_mK)
label = 'Mixing chamber temperature (mK)'
name_func_dict[name] = {'func': func, 'label': label}
