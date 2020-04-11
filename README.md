# First_scrap

https://theodor85.github.io/first_scrap/

- - -
[English](README.md), [Русский](README-ru.md)
- - -

First_scrap is a library for multithread scraping sites with random proxies and user-agents.

## Installation

To get started with the first_scrap library, activate (or create if necessary) your virtual environment. For example, as follows:

    python3 -m venv env
    source ./env/bin/activate

To install First_scrap use pip package manager:

    pip install firstscrap

Another installing approach is getting source code from GitHub. For this execute the commands in your console:

    git clone http://github.com/theodor85/first_scrap
    cd first_scrap
    python setup.py develop

## How to use

Using example for exctracting data from one web page:


```python
from firstscrap import pagehandler

@pagehandler(parser="BeautifulSoup")
def get_data(url, soup=None):
    # your only beatifulsoup code, without any requests, proxies, etc
    span = soup.find( name="span", attrs={"class": "p-nickname vcard-username d-block"} )
    text = span.get_text().strip()
    return text

if __name__ == '__main__' :
    print( get_data('https://github.com/theodor85') )

    # output:
    # theodor85
```

## What's under hood

When extracting data from a single page:

1. Random proxy server and user-agent are selected from the lists stored in the file.
2. These proxies and user-agents are used to access the page we need.
3. With BeautifulSoup the data is retrieved from the page.

## The most interesting thing is plenty identical pages processing

Here is the example:

```python
from firstscrap import listhandler

TEST_URLLIST_OLX = [
    'https://www.olx.ua/obyavlenie/spetsialist-po-podklyucheniyu-interneta-IDGnCkB.html',
    'https://www.olx.ua/obyavlenie/menedzher-po-robot-s-klentami-IDGkGK6.html',
]

@listhandler(threads_limit=5, parser='BeautifulSoup')
def get_date_time_from_olx(urllist, soup=None):
    ''' Beautifulsoup code for one page '''
    em = soup.find('em')
    row_text = em.get_text().strip()
    return row_text

if __name__ == '__main__' :
    data = get_date_time_from_olx(TEST_URLLIST_OLX)
    for item in data:
        print(item)
# output:
# Добавлено: в 16:49, 26 декабря 2019, Номер объявления: 626235005
# Добавлено: в 16:18, 29 декабря 2019, Номер объявления: 625536978

```

## What's under hood

The program processes each page in a separate thread, and the number of threads running at the same time does not exceed `threads_limit`.

Every thread makes request using random proxy and user-agent.

## Running the tests

To run the tests type in your console:

    python -m unittest -v tests/tests.py

Before running the tests enjure that your internet connection is active.

## Contributing

Merge you code to the 'develop' branch for contributing please.

Forks and pull requests are welcome! If you like first_scrap, do not forget to put a star!

## Bug reports

To bug report please mail to fedor_coder@mail.ru with tag "first_scrap bug reporting".

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
