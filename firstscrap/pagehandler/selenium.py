from abc import ABC, abstractmethod
import functools
from random import choice

from selenium import webdriver


def pagehandler_selenium(func):
        
    @functools.wraps(func)
    def execute(url, proxy=None, user_agent=None):
        return SeleniumDriver().get_data(
            func,
            url,
            proxy,
            user_agent,
        )

    return execute



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


#****************************** Исключения для Selenium ************************

class SeleniumException(Exception):
    """Базовый класс для исключений, возникающих при работе драйвера Selenium."""
    def __init__(self, Message, URL, Error):
        super(SeleniumException, self).__init__(Message)
        self.Message = Message
        self.URL = URL
        self.Error = Error

    def __str__(self):
        return "{msg}\n\tСообщение об ошибке: {err}\n\tНеобработан URL: {url}".format(msg=self.Message, err=self.Error, url=self.URL)

class SelenimDriverException(Exception):
    pass

class UrlOpenWithSeleniumException(Exception):
    pass

class ExtractDataWithSelenimException(Exception):
    pass
