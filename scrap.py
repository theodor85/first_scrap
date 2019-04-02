#-*-coding: utf-8 -*-

import openpyxl
from pagehandler import PageHandler
from listhandler import list_handler
from datetime import datetime
from time import sleep
import re
import os


# аренда
class LinksGetter(PageHandler):

    def __init__(self, URL):
        super().__init__()
        self.URL = URL
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, driver=None):

        data = []
        a_items = soup.find_all( "a", class_=re.compile("long-item-card__item___ubItG") )
        for a_item in a_items:
            data.append( 'https://www.domofond.ru' + a_item['href'] )

        return data

#main
def arenda(page_number, first_step=True):

    if first_step:
        # первый этап - спарсить ссылки на квартиры
        # генерируем список ссылок
        base_link = 'https://www.domofond.ru/arenda-studiy-krasnoyarsk-c3174?&Page='
        links = [ base_link+str(i) for i in range(1, page_number+1) ]

        # получаем список списков
        list_of_lists = list_handler(links, LinksGetter, with_processes=True, process_limit=10)

        # получаем плоский список
        flats_list = []
        for list in list_of_lists:
            flats_list = flats_list + list

        # записываем результат этого этапа в файл
        filename = os.path.dirname(os.path.realpath(__file__)) + '/data/arenda/flats_list.txt'
        with open(filename, 'w') as f:
            for flat in flats_list:
                f.write( '{fl}\n'.format(fl=flat) )

    # links = []
    # with open('flamp.txt', 'r') as f:
    #    for link in f:
    #        links.append(link)
    #
    # firms = PagesListHandler(links, FirmPage, WithProcesses=True, ProcessLimit = 10)
    # with open('firms.txt', 'w') as f:
    #    for firm in firms:
    #        f.write('{name}\t{site}\n'.format(name=firm['name'], site=firm['site']))

    # второй этап - спарсить данные по ссылкам


def main():
    start = datetime.now()
    arenda(page_number=10, first_step=True)
    end = datetime.now()

    total = end - start
    print("Всё ОК! Всего затрачено времени: ", str(total))
    print("КОНЕЦ!")

if __name__ == '__main__':
    main()
