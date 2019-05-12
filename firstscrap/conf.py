#-*-coding: utf-8 -*-


CONFIG_FILE_NAME = './firstscrap/config.txt'

class Configurator(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configurator, cls).__new__(cls)
            cls.instance.load_options(CONFIG_FILE_NAME)
        return cls.instance

    def load_options(self, filename):
        
        self.openfile(filename)
        self.clean_string_list()
        self.make_options_dict()

    def openfile(self, filename):
        with open(filename, 'r') as f:
            self.string_list = f.read().strip().split('\n')

    def clean_string_list(self):               
        self.cleaned_string_list = []
        for _str in self.string_list:
            if not _str:
                continue
            if _str[0] == '#':
                continue
            else:
                self.cleaned_string_list.append(_str)
    
    def make_options_dict(self):
        self.options_dict = {}
        for _str in self.cleaned_string_list:
            key, value = _str.split('=')
            key = key.strip() 
            value = value.strip()
            self.options_dict[key] = value

    def print_options(self):
        
        printstr = ''
        for key in self.options_dict.keys():
            printstr = printstr + '\n\t{key} = {value}'.format( key=key, value=self.options_dict[key] ) 
        
        return printstr

    def __repr__(self):
        return '<Config:' + self.print_options()
