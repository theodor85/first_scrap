#-*-coding: utf-8 -*-
from multiprocessing import Pool

data = []
def OnePageHandling(URL, OnePageHandlerClass):
    PageHandler = OnePageHandlerClass(URL)
    try:
        DataOneJK = PageHandler.execute()
    except Exception as e:
        print(e)
    data.append(DataOneJK)
    return data

def PagesListHandler(URLList, OnePageHandlerClass):
    with Pool(10) as p:
        p.map(OnePageHandling, URLList)
    return data
