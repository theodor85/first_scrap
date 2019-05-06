# First_scrap

- - -
[English](README.md), [Русский](README-ru.md)
- - -

First_scrap - это библиотека для мультипроцессного парсинга данных с использованием случайных прокси и user-agents.

## Установка и начало работы

Чтобы начать работу с библиотекой first_scrap, активируйте (или создайте при необходимости) ваше виртуальное окружение. Например, следующим образом:

    python3 -m venv env
    source ./env/bin/activate

Чтобы установить First_scrap воспользуйтесь менеджером пакетов pip:

    pip install firstscrap

Другой способ становки - получить исходный код с GitHub. Для этого выполните в консоли команды:

    git clone http://github.com/theodor85/first_scrap
    cd first_scrap
    python setup.py develop

### Как использовать

Чтобы извлечь данные из одной веб-страницы, создайте класс, производный от абстрактного класса PageHandler.

В вашем классе необходимо определить конструктор, в котором обязательно вызвать конструктор базового класса и определить два поля объекта: `URL` и `UseSelenium`. 

`URL` - это интернет адрес страницы, из которой вы хотите извлечь данные. 

`UseSelenium` - поле логического типа, определяет будет ли использоваться BeautifulSoup (значение `False`) или Selenium (значение `True`).

Также необходимо определить метод `extract_data_from_html(self, soup=None, driver=None)`. В этом методе используйте 

```python
from firstscrap.pagehandler import PageHandler

# класс для обработки одной страницы
class FlatHandler(PageHandler):

    def __init__(self, URL):
        super(FlatHandler, self).__init__()
        self.URL = URL
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, driver=None):

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
В переменной `data` будут помещены выбранные с сайта данные.

### Необходимые компоненты

Для использования возможностей бибиотеки Selenium необходимо установить в сиcтеме браузер Google Chrome ([скачать можно здесь](http://#)) и chromedriver ([инструкция по установке](http://#)).

Поддержка других браузеров планируется.

## Запуск автоматизированных тестов

Чтобы запустить тесты, введите в консоли:

    python -m unittest -v tests/tests.py

## Как внести вклад в проект

Для того, чтобы сделать ваш вклад в проект, вливайте ваш код в ветку 'develop'.

Fork'и pull request'ы приветствуются! Если вам понравился first_scrap, не забудьте поставить звёздочку! 

## License

Этот проект личензируетя под лицензией MIT. Подробнее смотрите файл [LICENSE.txt](LICENSE.txt)
