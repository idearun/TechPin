__author__ = 'amir'
class DataField:

    def __init__(self,name,value):
        self.name = name
        self.value = value
        self.is_link = False
        self.logo = ''

    def make_link(self,logo):
        self.is_link = True
        self.logo = logo