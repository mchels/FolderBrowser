class PseudoData(dict):
    def __init__(self, name_func_dict, sweep):
        super(PseudoData, self).__init__()
        self.name_func_dict = name_func_dict
        self.sweep = sweep

    def __getitem__(self, key):
        if key in self.keys():
            return dict.__getitem__(self, key)
        elif key in self.name_func_dict:
            func = self.name_func_dict[key]['func']
            pcol = func(self.sweep.data, self.sweep.pdata, self.sweep.meta)
            self.__setitem__(key, pcol)
            return pcol
        else:
            return dict.__getitem__(self, key)

    def get_names(self):
        names = [k for k, v in self.name_func_dict.items() if 'func' in v]
        names.sort()
        return names
