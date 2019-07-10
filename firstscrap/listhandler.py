#-*-coding: utf-8 -*-
from threading import Thread
from multiprocessing import Queue
from time import sleep
import random
import logging
import json

from tqdm import tqdm


LOG_FILE_NAME = 'log.log'


# def _without_processes(URLList, OnePageHandlerClass):
#     ''' Обработка списка URL-ов в простом цикле.  '''
#     data = []
#     i = 0
#     for URL in URLList:
#         i += 1
#         handler = OnePageHandlerClass(URL)
#         print("Обрабатываем страницу № %d, URL: %s"%(i, URL))
#         data.append(handler.execute())
#     return data

#************************** Многопоточная обработка *****************************

class ListHandler:

    def __init__(self, urls, func, with_threads=True, threads_limit=100):
        _set_log_options()
        self.urls = urls
        self.func = func
        self.with_threads = with_threads
        self.threads_limit = threads_limit
    
    def execute(self):
        if self.with_threads:
            data = self._execute_with_threads()
        else:
            data = self._execute_without_threads()
        return data

    def _execute_with_threads(self):
        ''' Запускает поток, который запускает рабочие потоки. Затем
        вынимает из очереди результаты. '''
        
        # сюда потоки будут складывать данные, затем отсюда мы их будем 
        # доставать
        data_queue = Queue() 
        
        input_data = {
            'data_queue': data_queue,
            'urls_list': self.urls,
            'work_function': self.func,
            'threads_limit': self.threads_limit,
        }

        thread_launcher = Thread(target=launch_threads, args=(), kwargs=input_data)
        thread_launcher.start()

        # вынимаем в бесконечном цикле результаты из очереди,
        # условие выхода: поток закончил работу И очередь пуста
        while True:
            if data_queue.empty():
                if not thread_launcher.is_alive():
                    break
                sleep(0.1)
            else:
                yield data_queue.get()
                

    def _execute_without_threads(self):
        data = []
        return data


def launch_threads(**input_data):
    passes_count = 0
    passes_limit = 2
    urls_list = list(input_data['urls_list'])
    while True:
        # если список URL-ов пустой, или превышен предел количества проходов,
        # то завершаем работу 
        if not( urls_list and (passes_count<=passes_limit) ):
            break
        else:
            urls_list = _list_handling(urls_list, input_data)
        passes_count += 1


def _list_handling(urls_list, input_data):
    ''' Запускает цикл обработки, ожидает завершения процессов,
    извлекает и возвращает список завершившихся с ошибкой url-ов 
    на повторную обработку. '''
    
    threads_list, urls_for_reprocess_queue = _url_list_loop(urls_list, input_data)
    _waiting_for_threads_completion(threads_list)
    urls_for_reprocess = _extract_urls_for_reprocess(urls_for_reprocess_queue)
    return urls_for_reprocess


def _url_list_loop(urls_list, input_data):
    ''' Осуществляет цикл по всем URL в списке и запускает процессы. '''

    threads_list = []
    urls_for_reprocess_queue = Queue()
    threads_count = 0

    for url in tqdm(urls_list):   # tqdm показывает прогресс-бар
        while True:
            number_alive = _get_number_alive(threads_list)
            # Если число "живых" больше либо равно лимиту, то ждём
            # иначе запускаем новый процесс и добавляем его в список.
            if number_alive >= input_data['threads_limit']:
                sleep(1)
                continue
            else:
                threads_count += 1
                input_data['url'] = url
                input_data['threads_count'] = threads_count
                input_data['urls_for_reprocessing_queue'] = urls_for_reprocess_queue
                t = Thread(target=_one_page_handling, args=(), kwargs=input_data)
                threads_list.append(t)
                t.start()
                break

    return threads_list, urls_for_reprocess_queue


def _get_number_alive(threads_list):
    ''' Узнаёт число "живых" потоков
    если поток "мертв", то удаляем его из списка. '''

    number_alive = 0
    j = 0
    while j<len(threads_list):
        if threads_list[j].is_alive():
            number_alive += 1
            j += 1
        else:
            del threads_list[j]

    return number_alive


def _one_page_handling(**input_data):
    ''' Эта функция запускается внутри рабочего потока. '''

    random_timeout()  # чтобы не заддосить сервер
    logger = logging.getLogger('list_handler')
    work_function = input_data['work_function']
    data_queue = input_data['data_queue']

    url = input_data['url']
    threads_count = input_data['threads_count']
    urls_for_reprocessing_queue = input_data['urls_for_reprocessing_queue']
    
    logger.info(
        'Процесс {pr}:\n\tНачало обработки URL\n\t{url}'.format(
            pr=str(threads_count),url=url
            )
        )

    try:
        one_page_data = work_function(url)  # здесь нужно добавить прокси и юзер-агент
    except Exception as e:
        logger.warning('''Процесс {pr}:\n\t Ошибка при обработке URL\n\t{url}.
            Текст ошибки: {msg}.\n\tURL отправлен на повторную обработку.
            '''.format(
                pr=str(threads_count), url=url, msg=e,
                )
            )
        urls_for_reprocessing_queue.put(url)
    else:
        logger.info(
            'Процесс {pr}:\n\tУспешно обработан URL\n\t{url}'.format(
                pr=str(threads_count), url=url
                )
            )
        data_queue.put(one_page_data)


def random_timeout():
    ''' Случайный тайм-аут от 0 до 5 секунд. '''
    sleep(random.randint(0, 5))


def _waiting_for_threads_completion(threads_list):
    print("Ожидаем завершение потоков...")
    while True:
        alive_is_here = False
        sleep(1)
        for i in range(0, len(threads_list)):
            if threads_list[i].is_alive():
                alive_is_here = True
                break
        if alive_is_here:
            continue
        else:
            break


def _extract_urls_for_reprocess(urls_for_reprocess_queue):
    
    urls_for_reprocess_list = []
    for _ in range(0, urls_for_reprocess_queue.qsize()):
        urls_for_reprocess_list.append(urls_for_reprocess_queue.get())
    return urls_for_reprocess_list


# ************************* Установка параметров логирования **************************

def _set_log_options():
    logger = logging.getLogger('list_handler')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(LOG_FILE_NAME)
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
