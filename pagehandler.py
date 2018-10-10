#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler, build_opener, install_opener
from bs4 import BeautifulSoup
from random import choice
from selenium import webdriver

def PageHandlerDecorator(UserHandler):
    """Декоратор класса.
    В декорируемом классе необходимо определить:
        метод extract_data_from_html(self, soup=None, driver=None), в которой нужно прописать выборку
            данных из html-страницы
            soup - это объект BeautifulSoup
            driver - это объект selenium
        поле URL - инициализирующееся в конструкторе
        поле UseSelenium - инициализирующееся в конструкторе. Принимает значение Fаlse или True
    """

    class PageHandler(UserHandler):
        """Класс обрабатывает один URL."""
        def __init__(self, URL):
            super().__init__(URL)
            self.ProxiesList = self._get_proxies_list("proxy_list.txt")
            self.UserAgentsList = self._get_user_agents_list("useragents.txt")

        #загружает список User-Agent
        def _get_user_agents_list(self, filename):
            return open(filename).read().strip().split('\n')

        #загружает список прокси-серверов
        def _get_proxies_list(self, filename):
            return open(filename).read().strip().split('\n')

        def execute(self):

            if self.UseSelenium:
                driver = self._get_selenium_driver()
                self._open_url_with_selenium(driver)
                data = self._get_data_from_page_with_selenium(driver)
                driver.close()
                return data
            else:
                return self._get_data_from_page_with_soup()

#****************** Методы для работы с BeautifulSoup **************************

        def _get_selenium_driver(self):
            try:
                driver = webdriver.Chrome(desired_capabilities=self._set_capabilities())
            except Exception as e:
                print("*** Ошибка при открытии драйвера selenium! Текст ошибки: ", e)
                raise Exception("*** Ошибка при открытии драйвера selenium! Текст ошибки: "+str(e))
            return driver

        def _open_url_with_selenium(self, driver):
            try:
                driver.get(self.URL)
            except Exception as e:
                print("*** Ошибка при открытии URL драйвером selenium! \n\tURL: {URL}\n\tТекст ошибки: {er_message}".format(URL=self.URL, er_message=str(e)))

        def _get_data_from_page_with_selenium(self, driver):
            try:
                data = self.extract_data_from_html(driver=driver)
            except Exception as e:
                print("*** Ошибка при обработке страницы с помощью selenium! \n\tURL: {URL}\n\tТекст ошибки: {er_message}".format(URL=self.URL, er_message=str(e)))
            return data

        def _set_capabilities(self):
            # используем случайный proxy
            proxy_name = choice(self.ProxiesList)
            capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            capabilities['proxy'] = {
                'httpProxy':proxy_name,
                'proxyType':'MANUAL',
            }
            return capabilities

#****************** Методы для работы с BeautifulSoup **************************

        def _get_data_from_page_with_soup(self):

            # открываем URL, получаем объект страницы и передаём его в BeautifulSoup
            # выбираем необходимые данные
            html = self._open_URL().read()
            try:
                data = self.extract_data_from_html( soup=BeautifulSoup(html, features="html.parser") )
            except Exception as e:
                raise Exception("Не удалось извлечь данные со страницы! \n\tURL: {URL} \n\tТекст ошибки: ".format(URL=self.URL) + str(e))

            return data

        def _open_URL(self):

            #указываем прокси-сервер, создаём объект запроса со случайным User-Agent
            # и открываем URL
            proxy = self._set_proxy()
            UAName = choice(self.UserAgentsList)
            req = Request(self.URL, headers={'User-Agent':UAName})
            try:
                html = urlopen(req)
            except Exception as e:
                raise Exception("""*** Ошибка при открытии URL функцией urlopen!
                    URL:{URL}
                    Прокси: {PROXY}
                    User-Agent: {UA}
                    Текст ошибки: """.format(
                        URL=self.URL,
                        PROXY=proxy.proxies['http'],
                        UA=UAName)
                            + str(e))
            return html

        def _set_proxy(self):
            proxy_name = choice(self.ProxiesList)
            proxy = ProxyHandler({'http':proxy_name})
            opener = build_opener(proxy)
            install_opener(opener)
            return proxy

    return PageHandler
