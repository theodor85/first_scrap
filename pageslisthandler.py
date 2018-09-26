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
    ProcessList = []
    q = Queue()
    for URL in URLList:
        Handler = OnePageHandlerClass(URL)
        p = Process(target=OnePageHandling, args=(Handler,q,))
        ProcessList.append(p)
        p.start()
    # здесь надо подождать,пока все потоки не отработают
    while True:
        for i in range(0, len(ProcessList)-1):
            if ProcessList[i].is_alive():
                continue
        break

    for i in range(0, q.qsize()-1):
        data.append(q.get())
    return data
