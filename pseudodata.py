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
        # return self.name_func_dict.keys()
        return names

    def get_labels(self):
        labels = [key['label'] for key in self.name_func_dict.keys()]
        return labels


# class PseudoFunction(object):
    # def __init__(self, name, label, active):
        # self.name = name
        # self.label = label
        # self.active = active

    # def __call__(self):
        # return 10

