from concurrent.futures import ThreadPoolExecutor
import functools

from firstscrap.pagehandler.static_parser import pagehandler


def listhandler_bs(threads_limit=10):
    def decorator(func):
            
        @functools.wraps(func)
        def execute(url_list):
            
            @pagehandler_bs
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

    def get_data(self):
        workers_count = min(self.threads_limit, len(self.url_list))
        with ThreadPoolExecutor(workers_count) as executor:
            data = executor.map(self.work_function, self.url_list)
        return data
