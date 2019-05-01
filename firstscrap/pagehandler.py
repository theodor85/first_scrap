#-*-coding: utf-8 -*-

import urllib.request
from urllib.request import urlopen, Request, ProxyHandler, build_opener, install_opener
from bs4 import BeautifulSoup
from random import choice
from selenium import webdriver

from abc import ABCMeta, abstractmethod

class PageHandler(metaclass=ABCMeta):
    """Абстракнтый класс для обработки одного URL.
    В дочернем классе необходимо реализовать:
        метод extract_data_from_html(self, soup=None, driver=None), в которой нужно прописать выборку
            данных из html-страницы
            soup - это объект BeautifulSoup
            driver - это объект selenium
        в конструкторе прописать вызов базового конструктора:
            super().__init__()
        в конструкторе определить поля:
            поле URL - url-адрес страницы для обработки
            поле UseSelenium - используется ли selenium (True) или BeautifulSoup (False)
    """
    def __init__(self):
        self.ProxiesList = self._get_proxies_list("./firstscrap/proxy_list.txt")
        self.UserAgentsList = self._get_user_agents_list("./firstscrap/useragents.txt")

    @abstractmethod
    def extract_data_from_html(self, soup=None, driver=None):
        pass

    #загружает список User-Agent
    def _get_user_agents_list(self, filename):
        return self._read_file(filename)

    #загружает список прокси-серверов
    def _get_proxies_list(self, filename):
        return self._read_file(filename)

    def _read_file(self, filename):
        with open(filename, 'r') as f:
            data = f.read().strip().split('\n')
        return data

    def execute(self):

        if self.UseSelenium:
            driver = self._get_selenium_driver()
            self._open_url_with_selenium(driver)
            data = self._get_data_from_page_with_selenium(driver)
            driver.close()
            return data
        else:
            return self._get_data_from_page_with_soup()

#****************** Методы для работы с Selenium *******************************

    def _get_selenium_driver(self):
        try:
            driver = webdriver.Chrome(desired_capabilities=self._set_capabilities())
        except Exception as err:
            raise SelenimDriverException("Ошибка при открытии драйвера selenium!", self.URL, err)
        return driver

    def _open_url_with_selenium(self, driver):
        try:
            driver.get(self.URL)
        except Exception as err:
            raise UrlOpenWithSeleniumException("Не удалось отрыть URL драйвером Selenium!", self.URL, err)

    def _get_data_from_page_with_selenium(self, driver):
        try:
            data = self.extract_data_from_html(driver=driver)
        except Exception as err:
            raise ExtractDataWithSelenimException("Ошибка при извлечении данных со страницы с помощью selenium!", self.URL, err)
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

#    return PageHandler

#****************************** Исключения *************************************

class PageHandlerException(Exception):
    """Базовый класс для всех исключений."""
    pass

#****************************** Исключения для Selenium ************************

class SeleniumException(PageHandlerException):
    """Базовый класс для исключений, возникающих при работе драйвера Selenium."""
    def __init__(self, Message, URL, Error):
        super(SeleniumException, self).__init__(Message)
        self.Message = Message
        self.URL = URL
        self.Error = Error

    def __str__(self):
        return "{msg}\n\tСообщение об ошибке: {err}\n\tНеобработан URL: {url}".format(msg=self.Message, err=self.Error, url=self.URL)

class SelenimDriverException(SeleniumException):
    pass

class UrlOpenWithSeleniumException(SeleniumException):
    pass

class ExtractDataWithSelenimException(SeleniumException):
    pass

#********************* Исключения для BeautifulSoup ****************************

class SoupException(PageHandlerException):
    """Базовый класс для исключений, возникающих при работе с BeautifulSoup."""
    def __init__(self, arg):
        super(PageHandlerException, self).__init__()
        self.arg = arg


class ExtractDataWithSoupException(Exception):
    """docstring for ExtractDataWithSoupException."""
    def __init__(self, arg):
        super(ExtractDataWithSoupException, self).__init__()
        self.arg = arg

class UrlOpenWithSoupException(Exception):
    """docstring for UrlOpenWithSoupException."""
    def __init__(self, arg):
        super(UrlOpenWithSoupException, self).__init__()
        self.arg = arg
