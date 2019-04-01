#-*-coding: utf-8 -*-

import openpyxl
from pagehandler import PageHandlerDecorator
from listhandler import PagesListHandler
from datetime import datetime
from time import sleep


# класс для использования в декораторе
@PageHandlerDecorator
class OneJKHandler(object):
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = False
    # это та самая функция, которую нужно изменять для каждой html-страницы
    def extract_data_from_html(self, soup=None, driver=None):

        data = {}
        data['jk_name'] = soup.find("h1", {"class": "card_title", "itemprop": "name"}).get_text()
        data['address'] = soup.find("div", {"class": "info_item"}).get_text().strip()
        data['price'] = ' '.join( soup.find("div", {"class": "descrition_price_item"}).get_text().strip().split() )
        div_table = soup.find("div", {"id": "house_content"})
        data['1_kom_metres'] = div_table.find("div", {"class":"card_row_item ws_nw lh_24 fs_16"}).get_text().strip()

        return data

@PageHandlerDecorator
class ListPage(object):
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = True
    def extract_data_from_html(self, soup=None, driver=None):

        data = []

        while True:
            list_a = driver.find_elements_by_xpath( '//a[@class="pos_a z_i_1 d_b layout"]' )
            for a in list_a:
                href = a.get_attribute('href')
                print("Найдена ссылка", href)
                # если ссылка рекламная, то её пропускаем
                if href.find('adfox') != -1:
                    print("\tЭта ссылка рекламная!")
                else:
                    data.append(href)

            # находим жлемент "Далее" и кликаем на нём. Если его нет (он не активен)
            # то выходим из цикла
            ul = driver.find_element_by_xpath( '//ul[@class="yiiPager"]' )
            try:
                li_next_hidden = ul.find_element_by_xpath('//li[@class="next hidden"]')
                break
            except:
                li = ul.find_element_by_class_name('next')
                a = li.find_element_by_tag_name('a')
                a.click()
                break  # для тестирования.
                sleep(3)

        return data

# аренда


#main
def arenda():

    # первый этап - спарсить ссылки на предложения
    # генерируем список ссылок
    base_link = 'https://www.domofond.ru/arenda-studiy-krasnoyarsk-c3174?&Page='
    links = [ base_link+str(i) for i in range(1, 11)]

    for link in links:
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
