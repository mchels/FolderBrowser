import numpy as np
from functools import partial


name_func_dict = {
    'backgate': {'label': 'Backgate voltage (V)'},
    'MC': {'label': 'Mixing chamber temperature (K)'},
}

def parent_f(data, pdata, meta):
    return data['MC'] * 10

name = 'MC*10'
func = partial(parent_f)
label = 'MC temperature in unhelpful units'
name_func_dict[name] = {'func': func, 'label': label}
