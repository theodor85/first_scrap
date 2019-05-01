#-*-coding: utf-8 -*-

import openpyxl
from firstscrap.pagehandler import PageHandler
from firstscrap.listhandler import list_handler
from datetime import datetime
from time import sleep
import re
import os
import json
from firstscrap.proxyrefresh import proxy_refresher

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

# класс для обработки страницы квартиры
class FlatHandler(PageHandler):

    def __init__(self, URL):
        super(FlatHandler, self).__init__()
        self.URL = URL
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, driver=None):

        data = {}
        data['link']    = self.URL
        data['name']    = soup.find('h1', class_='information__title___1nM29').get_text().strip()
        data['price']   = soup.find('div', class_='information__price___2Lpc0').span.get_text().strip()

        divs = soup.find('div', class_='detail-information__wrapper___FRRqm').find_all('div')
        for div in divs:

            spans = div.find_all('span')
            if ( spans[0].get_text().strip() == 'Площадь'):
                data['square'] = spans[1].get_text().strip()

            if ( spans[0].get_text().strip() == 'Цена за м²:'):
                data['price_per_meter'] = spans[1].get_text().strip()

        full_addr = soup.find('a', class_='information__address___1ZM6d').get_text().strip()
        addr_list = full_addr.split(',')
        data['address'] = addr_list[0] + ', ' + addr_list[1] + ', '+ addr_list[2]
        data['district'] = addr_list[3]

        # Рейтинг района  [3,5]
        data['area_rating'] =  soup.find('div', class_='area-rating__ratingNumber___1XZ04').get_text().strip()

        # Год постройки   [1990]
        # Этажность       [16]
        # Перекрытия      [Железобетонные]
        # Стены           [Панельные]
        # Газ.плита       [Нет]
        try:
            divs = soup.find('div', class_='project-info__wrapper___2b0As').find_all('div')
            for div in divs:

                spans = div.find_all('span')
                if ( spans[0].get_text().strip() == 'Год постройки:'):
                    data['year'] = spans[1].get_text().strip()

                if ( spans[0].get_text().strip() == 'Макс. этажность:'):
                    data['floors'] = spans[1].get_text().strip()

                if ( spans[0].get_text().strip() == 'Перекрытия:'):
                    data['flooring'] = spans[1].get_text().strip()

                if ( spans[0].get_text().strip() == 'Стены:'):
                    data['walls'] = spans[1].get_text().strip()

                if ( spans[0].get_text().strip() == 'Газ.плита:'):
                    data['gas_cooker'] = spans[1].get_text().strip()

        except:
            data['year'] = 'Информации нет'
            data['floors'] = 'Информации нет'
            data['flooring'] = 'Информации нет'
            data['walls'] = 'Информации нет'
            data['gas_cooker'] = 'Информации нет'

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

    # второй этап - спарсить данные по ссылкам
    print('Переходим ко второму этапу')
    links = []
    filename = os.path.dirname(os.path.realpath(__file__)) + '/data/arenda/flats_list.txt'
    with open(filename, 'r') as f:
       for link in f:
           links.append(link.strip())

    result = list_handler(links, FlatHandler, with_processes=True, process_limit=5)

    # выводим в json-файла
    filename = os.path.dirname(os.path.realpath(__file__)) + '/data/arenda/flats_rezult.json'
    with open(filename, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=4 )


def main():
    start = datetime.now()
    proxy_refresher()
    arenda(page_number=10, first_step=True)
    end = datetime.now()

    total = end - start
    print("Всё ОК! Всего затрачено времени: ", str(total))
    print("КОНЕЦ!")

if __name__ == '__main__':
    main()
