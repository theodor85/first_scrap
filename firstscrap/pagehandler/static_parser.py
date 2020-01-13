import functools, os
from random import choice

import requests

from .parsers import get_parser

PROXY_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/proxy_list.txt'
USER_AGENTS_LIST_FILENAME = os.path.dirname(os.path.realpath(__file__)) + '/useragents.txt'


def pagehandler(parser="BeautifulSoup"):
    def decorator(func):
        @functools.wraps(func)
        def execute(url, parser=parser, proxy=None, user_agent=None):
            return DataExtractor(func).get_data(
                Request(url, proxy, user_agent),
                Parser(parser),
            )
        return execute
    return decorator


class DataExtractor:
    '''  '''

    def __init__(self, func):
        self.func = func

    def get_data(self, request, parser):
        self.url = request.url   # self.url нужен для вставки в сообщение об ошибке
        html = request.do_request()
        parsed_html_obj = parser.parse(html)
        return self._try_extract_data(parsed_html_obj)

    def _try_extract_data(self, parsed_html_obj):
        try:
            data = self.func('', parsed_html_obj)
        except Exception as e:
            raise ExtractDataException("""*** Ошибка при извлечении данных из веб-страницы!
                URL:{URL}
                Текст ошибки: {msg}""".format(
                    URL=self.url,
                    msg=str(e),
                )
            )
        return data


class Request:
    
    def __init__(self, url, proxy, user_agent):
        self.url = url
        self.proxy = proxy
        self.user_agent = user_agent

    def do_request(self):
        
        params = RequestParameters(
                self.proxy, self.user_agent
            ).get_request_params()

        error_message = """*** Ошибка при выполнении http-запроса!
                URL:{URL}
                Прокси: {PROXY}
                User-Agent: {UA}
                Тип ошибки: {err_type}
                Текст ошибки: {msg}"""
        
        try:
            response = requests.get(
                self.url, proxies=params['proxies'], headers=params['headers']
            )
        except requests.exceptions.ConnectionError as e:
            raise UrlOpenException( 
                error_message.format(
                    URL=url,
                    PROXY=proxy['http'],
                    UA=headers['user-agent'],
                    err_type = type(e),
                    msg=str(e),
                )
            )

        return response.text


class RequestParameters:

    def __init__(self, proxy, user_agent):
        
        if not proxy:
            self._set_proxy()
        else:
            self.proxy = {'http': proxy}

        if not user_agent:
            self._set_user_agent()
        else:
            self.headers = {'user-agent': user_agent}

    def get_request_params(self):
        return {
            'proxies': self.proxy,
            'headers': self.headers,
        }

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


class Parser:

    def __init__(self, parser_name):
        self.parser_name = parser_name
    
    def parse(self, row_html):
        parser = get_parser(self.parser_name)
        return parser(row_html)


#********************* Исключения ****************************

class ExtractDataException(Exception):
    pass

class UrlOpenException(Exception):
    pass
