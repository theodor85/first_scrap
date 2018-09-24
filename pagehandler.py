#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler, build_opener, install_opener
from bs4 import BeautifulSoup
from random import choice

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
        data = self.ExtractDataFromHtml(bsObj)
        return data

    def OpenURL(self):
        """Метод делает 10 попыток открыть URL с разных прокси.
        Если открыть URL не удаётся, возвращется None. """
        i = 0
        while True:
            i += 1
            if i>10:
                return None
            #указываем прокси-сервер
            proxy_name = choice(self.ProxiesList)
            print(proxy_name)
            proxy = ProxyHandler({'http':proxy_name})
            opener = build_opener(proxy)
            install_opener(opener)
            # создаём объект запроса со случайным User-Agent
            UAName = choice(self.UserAgentsList)
            req = Request(self.URL, headers = {'User-Agent':UAName})
            try:
                # открываем URL
                html = urlopen(req)
                return html
            except Exception as e:
                print("************* URL не открылся! ************************")
                print("Текст ошибки:", e)
                print("\tURL:",self.URL)
                print("\tПрокси:",proxy_name)
                print("\tUser-Agent:",UAName)
                continue

    # это та самая функция, которую нужно изменять для каждой html-страницы
    def ExtractDataFromHtml(self, BS4):

        data = {}

        # получаем название ЖК
        lst = BS4.findAll("h1", {"class": "card_title", "itemprop": "name"})
        data['JK_name'] = lst[0].get_text()

        return data