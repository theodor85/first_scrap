#-*-coding: utf-8 -*-
from multiprocessing import Pool

data = []
def OnePageHandling(URL, HandlerClass):
    PageHandler = HandlerClass(URL)
    try:
        DataOneJK = PageHandler.execute()
    except Exception as e:
        print(e)
    data.append(DataOneJK)

def PagesListHandler(URLList, OnePageHandlerClass):
    with Pool(10) as p:
        p.map(OnePageHandling, URLList)
    return data
