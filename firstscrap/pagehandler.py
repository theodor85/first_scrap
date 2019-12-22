#-*-coding: utf-8 -*-
import functools, os
from random import choice, randint
from abc import ABC, abstractmethod
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

PROXY_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/proxy_list.txt'
USER_AGENTS_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/useragents.txt'


class SoupDataExtractor:

    def __init__(self, func, url, proxy, user_agent):
        ''' Прокси и юзер-агента можно передать в объект извне, 
        в противном случае, они будут подгружены из файлов.
         '''
        if not proxy:
            self._set_proxy()
        else:
            self.proxy = {'http': proxy}

        if not user_agent:
            self._set_user_agent()
        else:
            self.headers = {'user-agent': user_agent}
        
        self.func = func
        self.url = url

    def _set_proxy(self):
        self.proxy = {
            'http': choice( self._get_proxies_list(PROXY_LIST_FILENAME) ),
        }
    
    def _get_proxies_list(self, filename):
        ''' загружает список прокси-серверов '''
        return self._read_file(filename)

    def _read_file(self, filename):
        with open(filename, 'r') as f:
            data = f.read().strip().split('\n')
        return data

    def _set_user_agent(self):
        self.headers = {
            'user-agent': choice( self._get_user_agents_list(USER_AGENTS_LIST_FILENAME) ), 
        }

    def _get_user_agents_list(self, filename):
        ''' Загружает список User-Agent '''
        return self._read_file(filename)
    
    def extract_data(self):
        sleep(randint(0, 5))
        html = self._do_request()
        data = self._extract_data_with_soup(html)
        return data

    def _do_request(self):
        
        error_message = """*** Ошибка при выполнении http-запроса!
                URL:{URL}
                Прокси: {PROXY}
                User-Agent: {UA}
                Тип ошибки: {err_type}
                Текст ошибки: {msg}"""
        
        try:
            response = requests.get(self.url, proxies=self.proxy, headers=self.headers)
        except requests.exceptions.ConnectionError as e:
            raise UrlOpenWithSoupException( 
                error_message.format(
                    URL=self.url,
                    PROXY=self.proxy['http'],
                    UA=self.headers['user-agent'],
                    err_type = type(e),
                    msg=str(e),
                )
            )

        return response.text

    def _extract_data_with_soup(self, html):
        try:
            data = self.func( self.url, soup=BeautifulSoup(html, features="html.parser") )
        except Exception as e:
            raise ExtractDataWithSoupException("""*** Ошибка при извлечении данных из веб-страницы!
                URL:{URL}
                Текст ошибки: {msg}""".format(
                    URL=self.url,
                    msg=str(e),
                )
            )
        return data 


def pagehandler(use_selenium=False):
    def decorator(func):
            
        @functools.wraps(func)
        def execute(url, proxy=None, user_agent=None):
            
            if use_selenium:
                pass
            else:
                data_extractor = SoupDataExtractor(func, url, proxy, user_agent)
            return data_extractor.extract_data()

        return execute

    return decorator



PROXY_LIST_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/proxy_list.txt'
USER_AGENTS_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/useragents.txt'

# паттерн Стратегия для выбора бэкенда селениума
# базовый класс для паттерна Стратегия
class SeleniumBackendGetter(ABC):
    
    @abstractmethod
    def get_selenium_driver(self):
        pass 

# конкретная стратегия: используем Chrome и chromedriver
class ChromeBackendGetter(SeleniumBackendGetter):
    
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list

    def get_selenium_driver(self):
        options = self._set_chrome_options()
        capabilities = self._set_capabilities()
        driver = webdriver.Chrome(
                desired_capabilities=capabilities, 
                options=options)
        return driver

    def _set_capabilities(self):
        # используем случайный proxy
        proxy_name = choice(self.proxy_list)
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['proxy'] = {
            'httpProxy':proxy_name,
            'proxyType':'MANUAL',
        }
        return capabilities

    def _set_chrome_options(self):
        # используем опции Chrome. 
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # режим без графического интерфейса
        return options

  


class PageHandler(ABC):
    """Абстракнтый класс для обработки одного URL.
    В дочернем классе необходимо реализовать:
        метод extract_data_from_html(self, soup=None, selenium_driver=None), в которой нужно прописать выборку
            данных из html-страницы
            soup - это объект BeautifulSoup
            selenium_driver - это объект selenium
        в конструкторе прописать вызов базового конструктора:
            super().__init__()
        в конструкторе определить поля:
            поле URL - url-адрес страницы для обработки
            поле use_selenium - используется ли selenium (True) или BeautifulSoup (False)
    """
    def __init__(self):
        self.use_selenium = False
        self.URL = ''
        self.ProxiesList = self._get_proxies_list(PROXY_LIST_FILE_NAME)
        self.UserAgentsList = self._get_user_agents_list(USER_AGENTS_FILE_NAME)

    @abstractmethod
    def extract_data_from_html(self, soup=None, selenium_driver=None):
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

        if self.use_selenium:

            # контекст паттерна Стратегия
            # в этом месте должен быть выбор класса, в зависимости от настроек
            driver_getter = ChromeBackendGetter(self.ProxiesList)

            driver = self._get_selenium_driver(driver_getter)
            self._open_url_with_selenium(driver)
            data = self._get_data_from_page_with_selenium(driver)
            driver.close()
            return data
        else:
            return self._get_data_from_page_with_soup()

#****************** Методы для работы с Selenium *******************************

    def _get_selenium_driver(self, driver_getter):
        
        try:
            driver = driver_getter.get_selenium_driver()
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
            data = self.extract_data_from_html(selenium_driver=driver)
        except Exception as err:
            raise ExtractDataWithSelenimException("Ошибка при извлечении данных со страницы с помощью selenium!", self.URL, err)
        return data


#****************** Методы для работы с BeautifulSoup **************************

    def _get_data_from_page_with_soup(self):

        # открываем URL, получаем объект страницы и передаём его в BeautifulSoup
        # выбираем необходимые данные
        html = self._receive_html_from_URL()
        try:
            data = self.extract_data_from_html( soup=BeautifulSoup(html, features="html.parser") )
        except Exception as e:
            raise Exception("Не удалось извлечь данные со страницы! \n\tURL: {URL} \n\tТекст ошибки: ".format(URL=self.URL) + str(e))

        return data

    def _receive_html_from_URL(self):
        headers = self._get_headers()
        proxy = self._get_proxy()
        html = self._try_to_request(headers, proxy)
        return html

    def _get_headers(self):
        headers = {
            'user-agent': choice(self.UserAgentsList), 
        }
        return headers

    def _get_proxy(self):
        proxy = {
            'http': choice(self.ProxiesList),
        }
        return proxy

    def _try_to_request(self, headers, proxy):
        try:
            response = requests.get(self.URL, proxies=proxy, headers=headers)
        except Exception as e:
            raise Exception("""*** Ошибка при открытии при выполнении http-запроса!
                URL:{URL}
                Прокси: {PROXY}
                User-Agent: {UA}
                Текст ошибки: """.format(
                    URL=self.URL,
                    PROXY=proxy['http'],
                    UA=headers['user-agent'])
                        + str(e))
        return response.text


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

class ExtractDataWithSoupException(Exception):
    pass

class UrlOpenWithSoupException(Exception):
    pass
