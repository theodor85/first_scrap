#-*-coding: utf-8 -*-
from multiprocessing import Process, Queue
from time import sleep
import random
import logging
import json
from tqdm import tqdm

# во временном файле хранятся данные, сохраняющиеся
# "на лету", чтобы они не пропали при сбое 
TEMP_FILE_NAME = 'temp.dat'

LOG_FILE_NAME = 'log.log'

def _without_processes(URLList, OnePageHandlerClass):
    ''' Обработка списка URL-ов в простом цикле.  '''
    data = []
    i = 0
    for URL in URLList:
        i += 1
        handler = OnePageHandlerClass(URL)
        print("Обрабатываем страницу № %d, URL: %s"%(i, URL))
        data.append(handler.execute())
    return data

#************************** Многопоточная обработка *****************************
def random_timeout():
    ''' Случайный тайм-аут от 0 до 5 секунд. '''
    sleep(random.randint(0, 5))

def is_no_json_data():
    ''' Функция определяет, есть данные в json-файле или только открывающая скобочка.
    Это нужно для корректной записи данных: ставить запятую или нет. '''
    
    with open(TEMP_FILE_NAME, 'r') as f:
        s = f.read()
    
    if s=='[':
        return True
    else:
        return False


def _one_page_handling(handler, queue, process_count):
    ''' Эта функция запускается внутри процесса. '''

    # случайный тайм-аут
    # лог: начало работы
    # запуск обработчика страницы c try/catch
    # лог: успешно/неуспешно с сообщением об ошибке
    #     запись результата в JSON-файл
    #     лог: данные успешно записаны в файл
    # если не успешно:
    #     URL заносится в очередь на повторную обработку,
    #     лог: URL записан на повторную обработку
    random_timeout()
    logger = logging.getLogger('list_handler')
    
    URL = handler.URL
    logger.info('Процесс {pr}:\n\tНачало обработки URL\n\t{url}'.format(pr=str(process_count),url=URL))

    try:
        one_page_data = handler.execute()
        logger.info('Процесс {pr}:\n\tУспешно обработан URL\n\t{url}'.format(pr=str(process_count),url=URL))
        
        # если это первая запись во временный файл, то не нужна запятая
        need_comma = not is_no_json_data()
        with open(TEMP_FILE_NAME, 'a') as f:
            if need_comma:
                f.write(',\n')           
            json.dump(one_page_data, f, ensure_ascii=False, indent=4 )
  
        logger.info('Процесс {pr}:\n\tУспешно сохранены данные во временном файле из URL\n\t{url} '.format(pr=str(process_count),url=URL))

    except Exception as e:
        logger.warning('''Процесс {pr}:\n\t Ошибка при обработке URL\n\t{url}.
            Текст ошибки: {msg}.\n\tURL отправлен на повторную обработку.
            '''.format(pr=str(process_count), url=URL, msg=e))
        queue.put(URL)



def _get_number_alive(process_list):
    ''' Узнаёт число "живых" процессов
    если процесс "мертв", то удаляем его из списка. '''

    number_alive = 0
    j = 0
    while j<len(process_list):
        if process_list[j].is_alive():
            number_alive += 1
            j += 1
        else:
            del process_list[j]

    return number_alive


def _url_list_loop(URLList, OnePageHandlerClass, process_limit):
    ''' Осуществляет цикл по всем URL в списке и запускает процессы. '''

    #data = []
    process_list = []
    q = Queue()
    process_count = 0
    # -------для отладки. Ограничитель количества урлов -----------------------
    is_debag_limit = True
    debug_count = 0
    debug_limit = 10
    #--------------------------------------------------------------------------
    for URL in tqdm(URLList):
        
        # -------для отладки. Ограничитель количества урлов --------------------
        if is_debag_limit:
            debug_count += 1
            if debug_count >= debug_limit:
                break
        #-----------------------------------------------------------------------

        handler = OnePageHandlerClass(URL)
        while True:

            number_alive = _get_number_alive(process_list)
            # Если число "живых" больше либо равно лимиту, то ждём
            # иначе запускаем новый процесс и добавляем его в список.
            if number_alive >= process_limit:
                sleep(1)
                continue
            else:
                process_count += 1
                p = Process(target=_one_page_handling, args=(handler,q,process_count))
                process_list.append(p)
                p.start()
                break


    return process_list, q

def _wait_processes(process_list):

    print("Ожидаем завершение процессов...")
    while True:
        alive_is_here = False
        sleep(1)
        for i in range(0, len(process_list)):
            if process_list[i].is_alive():
                alive_is_here = True
                break
        if alive_is_here:
            continue
        else:
            break

def _get_urls_with_errors(errors_urls_queue):
    
    errors_urls_list = []
    for _ in range(0, errors_urls_queue.qsize()):
        errors_urls_list.append(errors_urls_queue.get())
    return errors_urls_list


def _list_handling(URLList, OnePageHandlerClass, process_limit):
    
    process_list, errors_urls_queue = _url_list_loop(URLList, OnePageHandlerClass, process_limit)
    _wait_processes(process_list)
    urls_with_errors = _get_urls_with_errors(errors_urls_queue)
    return urls_with_errors

    
def _with_processes(URLList, OnePageHandlerClass, process_limit):
    ''' Осуществляет многопроцессную, многопроходную обработку списка URL-ов.  '''
    
    # создаём и очищаем временный файл,записываем туда 
    # первый знак json
    with open(TEMP_FILE_NAME, 'w') as f:
        f.write('[')

    passes_count = 0
    passes_limit = 2
    while True:
        # если список URL-ов пустой, или превышен предел количества проходов,
        # то завершаем работу 
        if not( URLList and (passes_count<=passes_limit) ):
            break
        else:
            URLList = _list_handling(URLList, OnePageHandlerClass, process_limit)
        passes_count += 1

    # записываем закрывающую скобочку, чтобы были корректные данные json
    with open(TEMP_FILE_NAME, 'a') as f:
        f.write(']')    

    # возвращем сохраненную информацию
    data = {}
    with open(TEMP_FILE_NAME, 'r') as f:
        data = json.load(f)
    
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


# ************************* Интерфейсная функция **************************************

def list_handler(URLList, OnePageHandlerClass, with_processes=True, process_limit = 10):
    ''' Функция  обрабатывает список URL-ов.'''

    _set_log_options()
    if with_processes:
        return _with_processes(URLList, OnePageHandlerClass, process_limit)
    else:
        return _without_processes(URLList, OnePageHandlerClass)
