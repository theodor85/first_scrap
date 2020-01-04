from bs4 import BeautifulSoup


__ParsersTable = {}


def get_parser(parser_name):
    return __ParsersTable[parser_name]


def register_parser(parser_name):
    def decorator(func):
        __ParsersTable[parser_name] = func
        return func
    return decorator


@register_parser(parser_name='BeautifulSoup')
def beatiful_soup_parser(row_html):
    return BeautifulSoup(row_html, features='html.parser')
