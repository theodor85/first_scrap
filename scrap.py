#-*-coding: utf-8 -*-

import openpyxl
from pagehandler import PageHandlerDecorator
from listhandler import PagesListHandler
from datetime import datetime
from time import sleep

# функция создаёт файл Excel и рисует шапку
def Head():
    wb = openpyxl.Workbook()
    wb.active.title = "Новостройки"
    sheet = wb.active

    sheet['A7'] = "Ссылка на ЖК"
    sheet.merge_cells('A7:A8')

    sheet['B7'] = "из главной шапки"
    sheet.merge_cells('B7:D7')

    sheet['B8'] = "название"
    sheet['C8'] = "адрес"
    sheet['D8'] = "цены"

    sheet['E7'] = 'из блока с ценами (квардратные метры/цена/в продаже)'
    sheet.merge_cells('E7:L7')

    sheet['E8'] = "студии"
    sheet['F8'] = "1 ком"
    sheet['G8'] = "2 ком"
    sheet['H8'] = "3 ком"
    sheet['I8'] = "4 ком"
    sheet['J8'] = "многокомнатные"
    sheet['K8'] = "другие"
    sheet['L8'] = "другие"

    sheet['M7'] = 'акционный блок (загловок/текст/дедлайн)'
    sheet.merge_cells('M7:Q7')

    sheet['M8'] = "акция 1"
    sheet['N8'] = "акция 2"
    sheet['O8'] = "акция 3"
    sheet['P8'] = "акция 4"
    sheet['Q8'] = "акция 5"

    sheet['R7'] = 'расположение'
    sheet.merge_cells('R7:AB7')

    sheet['R8'] = "регион"
    sheet['S8'] = "район"
    sheet['T8'] = "локация"
    sheet['U8'] = "метро + сколько минут пешком"
    sheet['V8'] = "станция мцк"
    sheet['W8'] = "жд станция+ колько минут пешком"
    sheet['X8'] = "адрес"
    sheet['Y8'] = "шоссе"
    sheet['Z8'] = ""
    sheet['AA8'] = ""
    sheet['AB8'] = ""

    return wb

# функция выбирает один ЖК - НЕ АКТУАЛЬНА
def OneJK(Workbook, URL, StringNum, proxy_name, useragent):

    #указываем прокси-сервер
    proxy = ProxyHandler({'http':proxy_name})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    # открываем URL
    req = Request(URL, headers = {'User-Agent':useragent})
    html = urlopen(req)
    bsObj = BeautifulSoup(html.read(), features="html.parser")

    # получаем название ЖК
    lst = bsObj.findAll("h1", {"class": "card_title", "itemprop": "name"})
    # и записываем его в табличку
    Cell = 'B'+str(StringNum)
    Workbook.active[Cell] = lst[0].get_text()

    print("Параметры запроса:")
    print("\tUser-Agent:", useragent)
    print("\tProxy:", proxy_name)
    print("В ячейку", Cell, "записаны данные:", lst[0].get_text())
    print("-"*40)

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

# классы для flamp
@PageHandlerDecorator
class LinksToFirms(object):
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = True
    def extract_data_from_html(self, soup=None, driver=None):

        data = []
        while True:
            list_sections = driver.find_elements_by_xpath( '//section[@class="card card--basic js-card-link"]' )
            print("Нашли список section")
            for section in list_sections:
                # извлекаем из тега а ссылку
                link = 'https:' + section.get_attribute('data-url')
                print("Найдена ссылка", link)
                # сохраняем данные
                data.append(link)

            # находим жлемент "Далее" и кликаем на нём. Если его нет (он не активен)
            # то выходим из цикла
            try:
                li_next_pagination = driver.find_element_by_xpath('//li[@class="pagination__item pagination__item--next"]')
                a_next = li_next_pagination.find_element_by_xpath('//a[@class="pagination__link pagination__link--next js-pagination-link"]')
                a_next.click()
                sleep(3)
            except:
                break

        return data


                # находим адрес сайта фирмы
                # web_site_li = driver.find_element_by_xpath( '//li[@class="filial-web__site"]' )
                # print("Нашли тег web_site_li")
                # web_site_a = web_site_li.find_element_by_xpath( '//a[@class="link link--blue js-link"]' )
                # print("Нашли тег web_site_a")
                # web_site = web_site_a.text
                # print("Получили текст ссылки на веб-сайт")

@PageHandlerDecorator
class FirmPage(object):
    """docstring for FirmPage."""
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = False
    def extract_data_from_html(self, soup=None, driver=None):

        data = {}
        try:
            data['name'] = soup.find("h1", {"class": "header-filial__name t-h3"}).get_text().strip()
        except:
            data['name'] = 'null'
        try:
            data['site'] = 'http://' + soup.find("a", {"class": "link link--blue js-link"}).get_text().strip()
        except:
            data['site'] = 'null'
        return data

@PageHandlerDecorator
class YandexPage(object):
    """docstring for ."""
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = True
    def extract_data_from_html(self, soup=None, driver=None):
        data = {}
        data['url'] = self.URL[45:]
        try:
            message_no_result = driver.find_element_by_xpath( '//div[@class="misspell__message"]' )
            data['python'] = False
            return data
        except:
            data['python'] = True
            return data



#main

def flamp():

    # извлекаем названия фирм и их веб-сайты
    # firms = LinksToFirms("https://krasnoyarsk.flamp.ru/search/разработка%20программного%20обеспечения")
    # try:
    #     data = firms.execute()
    # except Exception as e:
    #     print(e)
    #
    # print(data)
    #
    # with open('flamp.txt', 'w') as f:
    #    i = 0
    #    for link in data:
    #        f.write(link+'\n')

    # links = []
    # with open('flamp.txt', 'r') as f:
    #    for link in f:
    #        links.append(link)
    #
    # firms = PagesListHandler(links, FirmPage, WithProcesses=True, ProcessLimit = 10)
    # with open('firms.txt', 'w') as f:
    #    for firm in firms:
    #        f.write('{name}\t{site}\n'.format(name=firm['name'], site=firm['site']))

    firms = []
    url_list = []
    firms_list = []
    with open('firms.txt', 'r') as f:
       for str_ in f:
           firm = {}
           firm['name'], firm['url'] = str_.strip().split('\t')
           firms_list.append(firm)
           url_list.append(firm['url'])

    # очищаем список УРЛ-ов от значений 'null'
    j = 0
    while j<len(url_list):
        if url_list[j] == 'null':
            del url_list[j]
        else:
            j += 1
            continue

    for i in range(len(url_list)):
        print(url_list[i])

    # формируем ссылки на Яндекс https://yandex.ru/search/?text=python%20site%3Ahttp%3A%2F%2Fwww.intecmedia.ru
    for i in range(len(url_list)):
        url_list[i] = 'https://yandex.ru/search/?text=python%20site:' + url_list[i]

    for i in range(len(url_list)):
        print(url_list[i])

    data = PagesListHandler(url_list, YandexPage, WithProcesses=True, ProcessLimit = 4)

    print(data)

    # пишем сразу в Ексель
    wb = openpyxl.Workbook()
    wb.active.title = "Фирмы"
    sheet = wb.active

    sheet['B2'] = "Название фирмы"
    sheet['C2'] = "Web-сайт"
    sheet['D2'] = "Python"

    str_num = 3
    for firm in firms_list:
        cell_name = 'B' + str(str_num)
        cell_site = 'C' + str(str_num)
        cell_python = 'D' + str(str_num)
        sheet[cell_name] = firm['name']
        sheet[cell_site] = firm['url']

        for j in range(len(data)):
            if data[j]['url'] == firm['url']:
                if data[j]['python']:
                    sheet[cell_python] = 'V'
                break
        str_num += 1

    wb.save('Фирмы.xls')

def main():
    start = datetime.now()
    flamp()

    #URLList = []
    #with open('links.txt', 'r') as f:
    #    i = 0
    #    for link in f:
    #        URLList.append(link)
    #        i += 1
    #        if i >= 0:
    #            break

    # сделаем замеры времени 40 процессов, 20, 10, 5
    # здесь результаты (100 URL):
    # 4 процесса - 13:22 (sleep(1))
    # 40 процессов - 9:35    (без sleep)
    #        без sleep       sleep(0.1)      sleep(0.5)     sleep(1)
    # 4          7:16            7:18          7:01          7:02
    # 5          7:05            7:21          6:43          6:52
    # 10         6:10            6:08          6:13          6:07
    # 20         6:06            6:19          6:38          6:11
    # 40         6:04            6:12          6:04          ~
    #100        ~
    #без МП     9:15
    #URLList.append('http://abracadabra.blbl')
    #data = PagesListHandler(URLList, OneJKHandler, WithProcesses=False, ProcessLimit = 10)

    # jk_lst = ListPage('https://www.novostroy-m.ru/baza/')
    # data = jk_lst.execute()
    # print(data)

    end = datetime.now()

    total = end - start
    print("Всё ОК! Всего затрачено времени: ", str(total))
    print("КОНЕЦ!")

if __name__ == '__main__':
    main()
