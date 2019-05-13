# First_scrap

- - -
[English](README.md), [Русский](README-ru.md)
- - -

First_scrap - это библиотека для мультипроцессного парсинга данных с использованием случайных прокси и user-agents.

## Установка

Чтобы начать работу с библиотекой first_scrap, активируйте (или создайте при необходимости) ваше виртуальное окружение. Например, следующим образом:

    python3 -m venv env
    source ./env/bin/activate

Чтобы установить First_scrap воспользуйтесь менеджером пакетов pip:

    pip install firstscrap

Другой способ становки - получить исходный код с GitHub. Для этого выполните в консоли команды:

    git clone http://github.com/theodor85/first_scrap
    cd first_scrap
    python setup.py develop

## Как использовать

Чтобы извлечь данные из одной веб-страницы, создайте класс, производный от абстрактного класса `PageHandler`.

В вашем классе необходимо определить конструктор, в котором обязательно вызвать конструктор базового класса и определить два поля объекта: `URL` и `use_selenium`. 

- `URL` - это интернет адрес страницы, из которой вы хотите извлечь данные. 
- `use_selenium` - поле логического типа, определяет будет ли использоваться BeautifulSoup (значение `False`) или Selenium (значение `True`).

Также необходимо определить метод `extract_data_from_html(self, soup=None, selenium_driver=None)`. В этом методе используйте объект BeautifulSoup (`soup`) или Selenium (`selenium_driver`) для извлечения данных. 

Пример приведен ниже.

```python
from firstscrap.pagehandler import PageHandler

# класс для обработки одной страницы
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
Затем, создайте экземпляр этого класса и вызовите его метод `execute()`:

```python
handler = FlatHandler('<ваш URL>')
data = handler.execute()
```

В переменной `data` будут помещены извлеченные с сайта данные.

Для извлечения данных из множества одинаковых страниц, используйте функцию `list_handler`:
```python
from firstscrap.listhandler import list_handler

result = list_handler(list_of_links, OnePageHandler, with_processes=True, process_limit=5)
```

Функция принимает следующие параметры:
- `list_of_links` - список ссылок на страницы, из которых извлекаются данные;
- `OnePageHandler` - класс-потомок `PageHandler`, извлекающий данные из одной страницы;
- `with_processes` - логический параметр, указывающий, применять ли многопроцессную обработку;
- `process_limit` - максимальное количество процессов, которое будет использоваться при многопроцессной обработке.

## Что происходит под капотом

При извлечении данных из одной страницы:

1. Из списков, хранящихся в файле, выбираются случайные прокси-сервер и user-agent.
2. Эти прокси-сервер и user-agent используются для обращения к нужной нам странице.
3. С помощью BeautifulSoup или Selenium (в зависимости от поля use_selenium) данные извлекаются из страницы и возвращаются методом `execute()`.

При извлечении данных из списка страниц:

1. Если параметр `with_processes = False`, то программа извлекает данные по очереди из всех страниц в переданном списке. При этом, каждый раз используется случаный прокси-сервер и user-agent.
2. В противном случае, программа запускает обработку каждой страницы в отдельном процессе, при этом, количество запущенных одновременно процессов не превышает `process_limit`. 

## Необходимые компоненты

Для использования возможностей бибиотеки Selenium необходимо установить в сиcтеме браузер Google Chrome ([скачать можно здесь](https://www.google.com/intl/ru_ALL/chrome/)) и chromedriver ([инструкция по установке](https://sites.google.com/a/chromium.org/chromedriver/getting-started)).

Поддержка других браузеров планируется.

## Запуск автоматизированных тестов

Чтобы запустить тесты, введите в консоли:

    python -m unittest -v tests/tests.py

Перед запуском тестов убедитесь, что ваше интернет-соединение активно.

## Как внести вклад в проект

Для того, чтобы сделать ваш вклад в проект, вливайте ваш код в ветку 'develop'.

Fork'и pull request'ы приветствуются! Если вам понравился first_scrap, не забудьте поставить звёздочку! 

## Сообщения об ошибках

Чтобы сообщить об ошибке, пожалуйста напишите мне на fedor_coder@mail.ru с пометкой в теме письма "first_scrap bug reporting".

## License

Этот проект личензируетя под лицензией MIT. Подробнее смотрите файл [LICENSE.txt](LICENSE.txt)
