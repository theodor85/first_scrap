#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler, build_opener, install_opener
from bs4 import BeautifulSoup
from random import choice
import openpyxl

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

class PageHandler(object):
    """Класс обрабатывает один URL."""
    def __init__(self, URL):
        self.URL = URL
        self.ProxiesList = self.GetProxiesList("proxy_list.txt")
        self.UserAgentsList = self.GetUserAgentsList("useragents.txt")

    #загружает список User-Agent
    def GetUserAgentsList(self, filename):
        return open(filename).read().strip().split('\n')

    #загружает список прокси-серверов
    def GetProxiesList(self, filename):
        return open(filename).read().strip().split('\n')

    def execute(self):

        # открываем URL, получаем объект страницы и передаём его в BeautifulSoup
        html = self.OpenURL()
        if html == None:
            raise Exception("Ошибка: Не удалось открыть URL "+self.URL)
        bsObj = BeautifulSoup(html.read(), features="html.parser")

        # выбираем необходимые данные
        data = ExtractDataFromHtml(bsObj)
        return data

    def OpenURL(self):
        """Метод делает 10 попыток открыть URL с разных прокси.
        Если открыть URL не удаётся, возвращется None. """
        i = 0
        while True:
            i += 1
            if i>10:
                return None
            try:
                #указываем прокси-сервер
                proxy_name = choice(self.ProxiesList)
                proxy = ProxyHandler({'http':proxy_name})
                opener = build_opener(proxy)
                install_opener(opener)

                # открываем URL
                req = Request(URL, headers = {'User-Agent':choice(self.UserAgentsList)})
                html = urlopen(req)
                return html
            except Exception as e:
                print("********Прокси-сервер", proxy_name, "не открылся!***********")
                continue

    def ExtractDataFromHtml(self, BS4):

        data = {}

        # получаем название ЖК
        lst = bsObj.findAll("h1", {"class": "card_title", "itemprop": "name"})
        data['JK_name'] = lst[0].get_text()

        return data


class JK(object):
    """Класс представляет собой набор данных, описывающий один
    Жилой комплекс."""
    def __init__(self, arg):
        super(JK, self).__init__()
        self.arg = arg



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


#main

JKList = ['https://www.novostroy-m.ru/baza/zhk_flotiliya',
    'https://www.novostroy-m.ru/baza/jk_mir_mitino',
    'https://www.novostroy-m.ru/baza/jk_na_dushinskoy_ulitse',
    'https://www.novostroy-m.ru/baza/apartkompleks_nahimov_nahimov',
    'https://www.novostroy-m.ru/baza/jk_ryazanskiy_prospekt_2']

#wb = Head()

for JK in JKList:
    data = {}
    handler = PageHandler(JK)
    try:
        data = handler.execute()
    except Exception as e:
        print(e)

print(data)

#wb.save('ex.xlsx')
print("Всё ОК!")
