from concurrent.futures import ThreadPoolExecutor
import functools

from firstscrap.pagehandler.static_parser import pagehandler


def listhandler(threads_limit=10, parser='BeautifulSoup'):
    def decorator(func):
            
        @functools.wraps(func)
        def execute(url_list):
            
            @pagehandler(parser=parser)
            def work_function(url, soup=None):
                return func(url, soup)

            return BSListDataExtractor(
                url_list,
                work_function,
                threads_limit,
                ).get_data()

        return execute

    return decorator


class BSListDataExtractor:
    def __init__(self, url_list, work_function, threads_limit):
        self.url_list = url_list
        self.work_function = work_function
        self.threads_limit = threads_limit

        self.parsers = ['BeautifulSoup', 'BeautifulSoup']
        self.proxies_list = ['213.27.152.15:3128', '190.93.176.11:8080']
        self.user_agents_list = ['Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)']

    def get_data(self):
        workers_count = min(self.threads_limit, len(self.url_list))
        with ThreadPoolExecutor(workers_count) as executor:
            data = executor.map(self.work_function, self.url_list, self.parsers, self.proxies_list, self.user_agents_list)
        return data
