from concurrent.futures import ThreadPoolExecutor
import functools
from random import choice

from firstscrap.pagehandler.static_parser import pagehandler
from firstscrap.pagehandler.static_parser import PROXY_LIST_FILENAME
from firstscrap.pagehandler.static_parser import USER_AGENTS_LIST_FILENAME


def listhandler(threads_limit=10, parser='BeautifulSoup'):
    def decorator(func):
            
        @functools.wraps(func)
        def execute(url_list):
            
            @pagehandler(parser=parser)
            def work_function(url, soup=None):
                return func(url, soup)

            return ListDataExtractor(
                url_list,
                work_function,
                threads_limit,
                parser_name = parser,
                ).get_data()

        return execute

    return decorator


class ListDataExtractor:
    def __init__(self, url_list, work_function, threads_limit, parser_name):
        self.url_list = url_list
        self.work_function = work_function
        self.threads_limit = threads_limit
        self.parser_name = parser_name

        self.parsers = ParserNameIterator(parser_name=parser_name)
        self.proxies = FileStringsIterator(PROXY_LIST_FILENAME)
        self.user_agents = FileStringsIterator(USER_AGENTS_LIST_FILENAME)

    def get_data(self):
        workers_count = min(self.threads_limit, len(self.url_list))
        with ThreadPoolExecutor(workers_count) as executor:
            data = executor.map(
                self.work_function,
                self.url_list,
                self.parsers,
                self.proxies,
                self.user_agents,
            )
        return data


class FileStringsIterator:
    ''' Бесконечный итератор, возващает случайную последовательность
    строк, загруженных из файла.
    '''
    def __init__(self, filename):
        self.filename = filename
        self._load_strings_from_file()

    def __iter__(self):
        return self
    
    def __next__(self):
        return self._get_random_string()

    def _load_strings_from_file(self):
        self._strings = self._read_file()

    def _read_file(self):
        with open(self.filename, 'r') as f:
            data = f.read().strip().split('\n')
        return data

    def _get_random_string(self):
        return choice(self._strings)


class ParserNameIterator:

    def __init__(self, parser_name):
        self.parser_name = parser_name

    def __next__(self):
        return self.parser_name

    def __iter__(self):
        return self
