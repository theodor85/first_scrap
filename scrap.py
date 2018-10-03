#-*-coding: utf-8 -*-

## TODO: 1. Сделать обработку списка ЖК через кликанье кнопки "Далее" - 1 п. -ОК, но на это ушло 1,5 часа
#        2. Флаг processLimit и его работа - 2 п.
#        3. Спарсить сайт с новостройками - 1 п.

import openpyxl
from pagehandler import PageHandlerDecorator
from pageslisthandler import PagesListHandler
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
    def ExtractDataFromHtml(self, soup=None, driver=None):

        data = {}
        # получаем название ЖК
        lst = soup.findAll("h1", {"class": "card_title", "itemprop": "name"})
        data['JK_name'] = lst[0].get_text()

        return data

@PageHandlerDecorator
class ListPage(object):
    def __init__(self, URL):
        self.URL = URL
        self.UseSelenium = True
    def ExtractDataFromHtml(self, soup=None, driver=None):

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
                sleep(3)

        return data


#main
if __name__ == '__main__':
    start = datetime.now()

    lstPage = ListPage('https://www.novostroy-m.ru/baza')
    data = lstPage.execute()
    i = 0
    for item in data:
        i += 1
        print( "№ %d. %s" %(i, item) )

    end = datetime.now()

    total = end - start
    print("Всё ОК! Всего затрачено времени: ", str(total))

    print("Запись в файл...")
    f = open('links.txt', 'w')
    for item in data:
        f.write(item+'\n')
    f.close()
    print("КОНЕЦ!")
