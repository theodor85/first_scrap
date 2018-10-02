#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler, build_opener, install_opener
from bs4 import BeautifulSoup
from random import choice
from selenium import webdriver

def PageHandlerDecorator(UserHandler):
    """Декоратор класса.
    В декорируемом классе необходимо определить:
        метод ExtractDataFromHtml(self, soup=None, driver=None), в которой нужно прописать выборку
            данных из html-страницы
        поле URL - инициализирующееся в конструкторе
        поле UseSelenium - инициализирующееся в конструкторе. Принимает значение Fаlse или True
    """

    class PageHandler(UserHandler):
        """Класс обрабатывает один URL."""
        def __init__(self, URL):
            super().__init__(URL)
            self.ProxiesList = self._GetProxiesList("proxy_list.txt")
            self.UserAgentsList = self._GetUserAgentsList("useragents.txt")

        #загружает список User-Agent
        def _GetUserAgentsList(self, filename):
            return open(filename).read().strip().split('\n')

        #загружает список прокси-серверов
        def _GetProxiesList(self, filename):
            return open(filename).read().strip().split('\n')

        def execute(self):

            if self.UseSelenium:
                driver = webdriver.Chrome(desired_capabilities=self._SetCapabilities())
                driver.get(self.URL)
                data = self.ExtractDataFromHtml(driver = driver)
                driver.close()
                return data
            else:
                # открываем URL, получаем объект страницы и передаём его в BeautifulSoup
                html = self._OpenURL()
                if html == None:
                    raise Exception("Ошибка: Не удалось открыть URL "+self.URL)
                bsObj = BeautifulSoup(html.read(), features="html.parser")
                # выбираем необходимые данные
                data = self.ExtractDataFromHtml(soup = bsObj)
                return data

        def _SetCapabilities(self):
            # используем случайный proxy
            proxy_name = choice(self.ProxiesList)
            capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            capabilities['proxy'] = {
                'httpProxy':proxy_name,
                'proxyType':'MANUAL',
            }
            return capabilities

        def _OpenURL(self):
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

    return PageHandler
