#-*-coding: utf-8 -*-
import functools, os
from random import choice
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

PROXY_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/proxy_list.txt'
USER_AGENTS_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/useragents.txt'



def pagehandler_bs(func):
        
    @functools.wraps(func)
    def execute(url, proxy=None, user_agent=None):
        return DataExtractor(
            func,
            url,
            proxy,
            user_agent,
            backend=BSDriver(),
        ).get_data()

    return execute


def pagehandler_selenium(func):
        
    @functools.wraps(func)
    def execute(url, proxy=None, user_agent=None):
        return DataExtractor(
            func,
            url,
            proxy,
            user_agent,
            backend=SeleniumDriver(),
        ).get_data()

    return execute


class DataExtractor:
    '''  '''

    def __init__(self, func, url, proxy, user_agent, backend):
        ''' Прокси и юзер-агента можно передать в объект извне, 
        в противном случае, они будут подгружены из файлов.
        '''
        self.func = func
        self.url = url
        self.proxy = proxy
        self.user_agent = user_agent
        self.backend_object = backend

    def get_data(self):
        return self.backend_object.get_data(
            self.func,
            self.url,
            self.proxy,
            self.user_agent,
        )


class BSDriver:

    def __init__(self):
        pass

    def get_data(self, func, url, proxy, user_agent):
        # получить параметры запроса (proxy, headers)
        request_params = RequestParametersSetter(proxy, user_agent)
        request_params.url = url

        # сделать запрос
        response = Request(request_params).do_request()

        # разобрать ответ и вернуть объект данных
        data = Parser(response, func, url).extract_data()
        return data


class RequestParametersSetter:

    def __init__(self, proxy, user_agent):
        
        if not proxy:
            self._set_proxy()
        else:
            self.proxy = {'http': proxy}

        if not user_agent:
            self._set_user_agent()
        else:
            self.headers = {'user-agent': user_agent}

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


class Request:
    
    def __init__(self, request_params):
        self.url = request_params.url
        self.proxy = request_params.proxy
        self.headers = request_params.headers

    def do_request(self):
        
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


class Parser:

    def __init__(self, html, func, url):
        self.html = html
        self.func = func
        self.url = url
    
    def extract_data(self):
        try:
            data = self.func(self.url, soup=BeautifulSoup(self.html, features="html.parser") )
        except Exception as e:
            raise ExtractDataWithSoupException("""*** Ошибка при извлечении данных из веб-страницы!
                URL:{URL}
                Текст ошибки: {msg}""".format(
                    URL=self.url,
                    msg=str(e),
                )
            )
        return data


class SeleniumDriver:

    def __init__(self):
        pass

    def get_data(self, func, url, proxy, user_agent):
        
        self.url = url
        self.func = func
        
        # контекст паттерна Стратегия
        # в этом месте должен быть выбор класса, в зависимости от настроек
        driver_getter = ChromeBackendGetter(proxy)

        self.driver = self._get_selenium_driver(driver_getter)
        self._open_url_with_selenium()
        data = self._get_data_from_page_with_selenium()
        self.driver.close()
        return data

    def _get_selenium_driver(self, driver_getter):
        
        try:
            driver = driver_getter.get_selenium_driver()
        except Exception as err:
            raise SelenimDriverException(
                "Ошибка при открытии драйвера selenium!", self.url, err)
        return driver

    def _open_url_with_selenium(self):
        try:
            self.driver.get(self.url)
        except Exception as err:
            raise UrlOpenWithSeleniumException(
                "Не удалось отрыть URL драйвером Selenium!", self.url, err)

    def _get_data_from_page_with_selenium(self):
        try:
            data = self.func(self.url, selenium=self.driver)
        except Exception as err:
            raise ExtractDataWithSelenimException(
                "Ошибка при извлечении данных со страницы с помощью selenium!",
                self.url,
                err,
            )
        return data





# паттерн Стратегия для выбора бэкенда селениума
# базовый класс для паттерна Стратегия
class SeleniumBackendGetter(ABC):
    
    @abstractmethod
    def get_selenium_driver(self):
        pass 

# конкретная стратегия: используем Chrome и chromedriver
class ChromeBackendGetter(SeleniumBackendGetter):
    
    def __init__(self, proxy):
        self.proxy_list = [proxy, ]

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
