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
To extract data from one web-page create a class that derives from the `PageHandler` abstract class.

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

### Prerequisites

To use the Selenium library opportunities, you must install the Google Chrome browser ([download here](http://#)) and chromedriver ([installation instructions](http://#)) on your system.

Supporting for other brousers is planned.

## Running the tests

To run the tests type in your console:

    python -m unittest -v tests/tests.py

Before running the tests enjure that your internet connection is active.

## Contributing

Merge you code to the 'develop' branch for contributing please.

Forks and pull requests are welcome! If you like first_scrap, do not forget to put a star!

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
