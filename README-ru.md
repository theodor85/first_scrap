# First_scrap

https://theodor85.github.io/first_scrap/

- - -
[English](README.md), [Русский](README-ru.md)
- - -

First_scrap - это библиотека для многопоточного парсинга данных с использованием случайных прокси и user-agents.

## Установка

Чтобы начать работу с библиотекой first_scrap, активируйте (или создайте при необходимости) ваше виртуальное окружение. Например, следующим образом:

    python3 -m venv env
    source ./env/bin/activate

Чтобы установить First_scrap воспользуйтесь менеджером пакетов pip:

    pip install firstscrap

Другой способ установки - получить исходный код с GitHub. Для этого выполните в консоли команды:

    git clone http://github.com/theodor85/first_scrap
    cd first_scrap
    python setup.py develop

## Как использовать

Пример использования для извлечения данных из одной веб-страницы:

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

## Что происходит под капотом

При извлечении данных из одной страницы:

1. Из списков, хранящихся в файле, выбираются случайные прокси-сервер и user-agent.
2. Эти прокси-сервер и user-agent используются для обращения к нужной нам странице.
3. С помощью BeautifulSoup данные извлекаются из страницы.

## Самое интересное - обработка множества однотипных страниц

Пример:

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

## Что происходит под капотом

Программа обрабатывает каждую страницы в отдельном потоке, иколичество потоков, запущенных в одно и то же время, не может превышать `threads_limit`.

Каждый поток делает запрос с использованием случайных прокси и user-agent.

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
