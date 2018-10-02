#-*-coding: utf-8 -*-
from multiprocessing import Process, Queue
from time import sleep

def OnePageHandling(Handler, queue):

    DataOnePage = Handler.execute()
    queue.put(DataOnePage)

def PagesListHandler(URLList, OnePageHandlerClass):

    data = []
    Handlers = []
    ProcessList = []
    q = Queue()
    i = 0
    for URL in URLList:
        Handler = OnePageHandlerClass(URL)
        p = Process(target=OnePageHandling, args=(Handler,q,))
        ProcessList.append(p)
        i += 1
        print("Запускаем процесс № ", i)
        p.start()
    # здесь надо подождать,пока все потоки не отработают
    print("Ожидаем завершение процессов...")
    while True:
        alive_is_here = False
        sleep(1)
        for i in range(0, len(ProcessList)):
            if ProcessList[i].is_alive():
                alive_is_here = True
                break
        if alive_is_here:
            continue
        else:
            break
    # извлекаем данные из очереди
    for i in range(0, q.qsize()):
        data.append(q.get())
    return data
