# First_scrap

- - -
[English](README.md), [Русский](README-ru.md)
- - -

First_scrap is a library for scraping sites with multiprocessing, random proxies and user-agents.

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
To extract data from single web-page create a class that derives from the `PageHandler` abstract class.

In your class, you must define a constructor in which you must call the base class constructor and define two instance fields: `URL` and `use_selenium`:

- `URL` - URL of the web-page from which you want to extract data.
- `use_selenium` - this boolean field determine if BeautifulSoup will be used (if it sets in `False`) or Selenium (`True`).

As well you must define a method `extract_data_from_html(self, soup=None, selenium_driver=None)`. Use BeautifulSoup (`soup`) object or Selenium (`selenium_driver`) for data extraction.

An example is given below.

```python
from firstscrap.pagehandler import PageHandler

# class for one web-page handling
class OnePageHandler(PageHandler):

    def __init__(self, URL):
        super(FlatHandler, self).__init__()
        self.URL = URL
        self.use_selenium = False

    def extract_data_from_html(self, soup=None, selenium_driver=None):

        data = {}
        data['link']    = self.URL
        data['name']    = soup.find('h1', class_='information__title___1nM29').get_text().strip()
        data['price']   = soup.find('div', class_='information__price___2Lpc0').span.get_text().strip()
```
Then create an instance of that class and call the `execute()` method. 

```python
handler = FlatHandler('<your URL>')
data = handler.execute()
```

There are your extracted data in the `data` variable.

To extract data from list of many same web-pages use the `list_handler` function:

```python
from firstscrap.listhandler import list_handler

result = list_handler(list_of_links, OnePageHandler, with_processes=True, process_limit=5)
```

The function takes parametres:
- `list_of_links` - list of links to pages from which data will be extracted;
- `OnePageHandler` - descendant of `PageHandler` class, extracts data from one web-page;
- `with_processes` - boolean parameter, if multiprocessing will be used;
- `process_limit` - max number of processes.

## What's under hood

When extracting data from a single page:

1. Random proxy server and user-agent are selected from the lists stored in the file.
2. These proxies and user-agents are used to access the page we need.
3. With BeautifulSoup or Selenium (depending on the use_selenium field), the data is retrieved from the page and returned by the ' execute ()`method.

When extracting data from a page list:

1. If the `with_processes = False` parameter, the program retrieves data one by one from all pages in the passed list. At the same time, a random proxy server and user-agent are used every time.
2. Otherwise, the program starts processing each page in a separate process, and the number of processes running at the same time does not exceed `process_limit`.

### Prerequisites

To use the Selenium library opportunities, you must install the Google Chrome browser ([download here](https://www.google.com/intl/ru_ALL/chrome/)) and chromedriver ([installation instructions](https://sites.google.com/a/chromium.org/chromedriver/getting-started)) on your system.

Supporting for other brousers is planned.

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
