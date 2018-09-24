#-*-coding: utf-8 -*-
from multiprocessing import Pool

def PagesListHandler(URLList, OnePageHandlerClass):

    

    def OnePageHandling(self, URL):
        self.PageHandler.URL = URL
        try:
            DataOneJK = self.PageHandler.execute()
        except Exception as e:
            print(e)
        data.append(DataOneJK)

    def execute(self):
        with Pool(10) as p:
            p.map(self.OnePageHandling, self.URLList)
        return self.data
