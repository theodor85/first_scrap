#-*-coding: utf-8 -*-
from multiprocessing import Process, Queue

def OnePageHandling(Handler, qu):

    try:
        DataOneJK = Handler.execute()
    except Exception as e:
        print(e)
    qu.put(DataOneJK)

def PagesListHandler(URLList, OnePageHandlerClass):

    data = []
    Handlers = []
    q = Queue()
    for URL in URLList:
        Handler = OnePageHandlerClass(URL)
        p = Process(target=OnePageHandling, args=(Handler,q,))
        p.start()

    for i in range(0, q.qsize()-1):
        data.append(q.get())
    return data
