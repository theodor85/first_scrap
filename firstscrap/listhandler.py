#-*-coding: utf-8 -*-
from threading import Thread
from multiprocessing import Queue
from time import sleep
import random
import logging

from tqdm import tqdm

LOG_FILE_NAME = 'log.log'


#************************** Многопоточная обработка *****************************

def listhandler(url_list, func, with_threads=True, threads_limit=5):
    _set_log_options()
    
    input_data = {
    'urls_list': url_list,
    'work_function': func,
    'threads_limit': threads_limit,
    }
    
    if with_threads:
        data_gen = _execute_with_threads(input_data)
    else:
        data_gen = _execute_without_threads(input_data)
    return data_gen


def _execute_with_threads(input_data):
    ''' Запускает поток, который запускает рабочие потоки. Затем
    вынимает из очереди результаты. Возращает объект-генератор.'''
       
    input_data['data_queue'] = Queue()
    input_data['threads_launcher'] = _run_threads_launcher(input_data)
    return _get_result_generator(input_data)


def _run_threads_launcher(input_data):
    threads_launcher = Thread(target=_launch_threads, args=(), kwargs=input_data)
    threads_launcher.start()
    return threads_launcher


def _get_result_generator(input_data):
    # вынимаем в бесконечном цикле результаты из очереди,
    # условие выхода: поток закончил работу И очередь пуста
    while True:
        if input_data['data_queue'].empty():
            if not input_data['threads_launcher'].is_alive():
                break
            sleep(0.1)
        else:
            yield input_data['data_queue'].get()


def _launch_threads(**input_data):
    ''' Многопроходная обработка url-ов '''
    passes_count = 0
    passes_limit = 2
    urls_list = list(input_data['urls_list'])
    while True:
        # если список URL-ов пустой, или превышен предел количества проходов,
        # то завершаем работу 
        if not( urls_list and (passes_count<=passes_limit) ):
            break
        else:
            # получаем необработанные url-ы
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

    _random_timeout()  # чтобы не заддосить сервер
    
    write_log_start_processing(input_data['threads_count'], input_data['url'])
    try_to_execute_work_function(input_data)


def write_log_start_processing(thread_num, url):
    logger = logging.getLogger('list_handler')
    logger.info(
        'Процесс {thr}:\n\tНачало обработки URL\n\t{url}'.format(
            thr=str(thread_num),url=url
            )
        )


def try_to_execute_work_function(input_data):
    work_function = input_data['work_function']
    url = input_data['url']
    thr_count = input_data['threads_count']
    try:
        one_page_data = work_function(url)  # TODO: здесь нужно добавить прокси и юзер-агент
    except Exception as e:
        # ошибка: пишем в лог и отправляем на повторную обработку
        _write_log_url_processing_error(thr_count, url, e)
        input_data['urls_for_reprocessing_queue'].put(url)
    else:
        # успешно: пишем в лог и помещаем данные в очередь
        _write_log_url_processing_success(thr_count, url)
        input_data['data_queue'].put(one_page_data)


def _write_log_url_processing_error(thr, url, msg):
    logger = logging.getLogger('list_handler')
    logger.warning('''Процесс {thr}:\n\t Ошибка при обработке URL\n\t{url}.
        Текст ошибки: {msg}.\n\tURL отправлен на повторную обработку.
        '''.format(
            thr=str(thr), url=url, msg=msg,
        )
    )


def _write_log_url_processing_success(thr, url):
    logger = logging.getLogger('list_handler')
    logger.info('''Процесс {thr}:\n\tУспешно обработан URL\n\t{url}'''.format(
        thr=str(thr), url=url
        ) 
    )


def _random_timeout():
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


# ************************* Обработка без потоков **************************

def _execute_without_threads(input_data):
    data = []
    return data

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