#-*-coding: utf-8 -*-
from multiprocessing import Process, Queue
from time import sleep

def OnePageHandling(Handler, queue):

    DataOnePage = Handler.execute()
    queue.put(DataOnePage)

def _WithoutProcesses(URLList, OnePageHandlerClass):
    data = []
    i = 0
    for URL in URLList:
        i += 1
        Handler = OnePageHandlerClass(URL)
        print("Обрабатываем страницу № %d, URL: %s"%(i, URL))
        data.append(Handler.execute())
    return data

def _WithProcesses(URLList, OnePageHandlerClass, ProcessLimit):
    data = []
    Handlers = []
    ProcessList = []
    q = Queue()
    i = 0
    assert ProcessLimit > 0
    for URL in URLList:
        Handler = OnePageHandlerClass(URL)
        while True:
            # узнаем число "живых" процессов
            # если процесс "мертв", то удаляем его из списка
            number_alive = 0
            for j in range(len(ProcessList)):
                if ProcessList[j].is_alive():
                    number_alive += 1
                else:
                    ProcessList[j] = None
            
            # если число "живых" больше либо равно лимиту, то ждём
            # иначе запускаем новый процесс и добавляем его в список
            if number_alive >= ProcessLimit:
                sleep(1)
                continue
            else:
                p = Process(target=OnePageHandling, args=(Handler,q,))
                ProcessList.append(p)
                i += 1
                print("Запускаем процесс № ", i)
                p.start()
                break

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

def PagesListHandler(URLList, OnePageHandlerClass, WithProcesses=True, ProcessLimit = 10):

    if WithProcesses:
        return _WithProcesses(URLList, OnePageHandlerClass, ProcessLimit)
    else:
        return _WithoutProcesses(URLList, OnePageHandlerClass)
