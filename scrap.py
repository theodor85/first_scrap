#-*-coding: utf-8 -*-

import openpyxl
from pagehandler import PageHandler
from listhandler import PagesListHandler
from datetime import datetime
from time import sleep
import re


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
def arenda():

    # первый этап - спарсить ссылки на предложения
    # генерируем список ссылок
    base_link = 'https://www.domofond.ru/arenda-studiy-krasnoyarsk-c3174?&Page='
    links = [ base_link+str(i) for i in range(1, 11) ]

    linksgetter = LinksGetter(links[9])
    data = linksgetter.execute()

    for link in data:
        print(link)


    # второй этап - спарсить данные по ссылкам


def main():
    start = datetime.now()
    arenda()
    end = datetime.now()

    total = end - start
    print("Всё ОК! Всего затрачено времени: ", str(total))
    print("КОНЕЦ!")

if __name__ == '__main__':
    main()
