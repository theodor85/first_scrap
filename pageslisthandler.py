#-*-coding: utf-8 -*-
from multiprocessing import Pool

def OnePageHandling(Handler):

    try:
        DataOneJK = Handler.execute()
    except Exception as e:
        print(e)
    return DataOneJK

def PagesListHandler(URLList, OnePageHandlerClass):

    data = []
    Handlers = []
    for URL in URLList:
        Handler = OnePageHandlerClass(URL)
        Handlers.append(Handler)
    with Pool(10) as p:
        data = p.map(OnePageHandling, Handlers)
    return data
