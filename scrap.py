#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler
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
    def __init__(self, arg):
        super(PageHandler, self).__init__()
        self.arg = arg

    def execute(self, arg):
        jk = JK()
        # заполняем поля объекта jk данными
        return jk

class JK(object):
    """Класс представляет собой набор данных, описывающий один
    Жилой комплекс."""
    def __init__(self, arg):
        super(JK, self).__init__()
        self.arg = arg



# функция выбирает один ЖК
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

#загружает список User-Agent
def GetUserAgentsList(filename):
    return open(filename).read().split('\n')

#загружает список прокси-серверов
def GetProxiesList(filename):
    return open(filename).read().split('\n')

#main

UAList = GetUserAgentsList("useragents.txt")
ProxiesList = GetProxiesList("proxy_list.txt")

JKList = ['https://www.novostroy-m.ru/baza/zhk_flotiliya',
    'https://www.novostroy-m.ru/baza/jk_mir_mitino',
    'https://www.novostroy-m.ru/baza/jk_na_dushinskoy_ulitse',
    'https://www.novostroy-m.ru/baza/apartkompleks_nahimov_nahimov',
    'https://www.novostroy-m.ru/baza/jk_ryazanskiy_prospekt_2']

wb = Head()

i = 0
for JK in JKList:
    OneJK(wb, JK, 9+i, choice(ProxiesList), choice(UAList))
    i+=1

wb.save('ex.xlsx')
print("Всё ОК!")
