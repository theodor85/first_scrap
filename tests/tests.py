import unittest

from firstscrap.listhandler import listhandler_bs

from firstscrap.pagehandler.static_parser import pagehandler
from firstscrap.pagehandler.selenium import pagehandler_selenium
# план тестирования
# Что тестируем                     | Имя тестового класса      | Готовность
#-----------------------------------------------------------------------
# BS - одиночная страница           | BSOnePageTest             | OK
# Selenium - одиночая стр.          | SeleniumOnePageTest       | OK
#-----------------------------------------------------------------------
# BS - список стр. - без потоков  | BSListWithoutMPTest       | X
# Sel - список стр. - без потоков | SeleniumListWithoutMPTest | -
# BS - список стр. - c потоками   | BSListMPTest              | OK
# Sel - список стр. - c потоками  | SeleniumListMPTest        | X          

TEST_URL = 'https://classinform.ru/okpo/01/ogrn1020100001778.html'
CHECK_TEXT = 'Гиагинское районное отделение Адыгейской республиканской общественной организации охотников и рыболовов'

@pagehandler(parser="BeautifulSoup")
def get_data(url, soup=None):
    h2 = soup.find( "h2" )
    header = h2.get_text().strip()
    return header

@pagehandler_selenium
def get_data_selenium(url, selenium=None):
    h2 = selenium.find_element_by_tag_name( "h2" )
    header = h2.text.strip()
    return header    

   
class BSOnePageTest(unittest.TestCase):
    def test_soup(self):
        data = get_data(TEST_URL)
        self.assertEqual(data, CHECK_TEXT)


class SeleniumOnePageTest(unittest.TestCase):
    def test_selenium(self):
        data = get_data_selenium(TEST_URL)
        self.assertEqual(data, CHECK_TEXT)


# ************* Тестируем извлечение данных из списка url *************************
# сайт olx.ua

TEST_URL_OLX = 'https://www.olx.ua/rabota/telekommunikatsii-svyaz/'

@pagehandler_selenium
def get_links(url, soup=None):
    ''' Извлекает ссылки на объявления '''
    links = []
    a_tags = soup.find_all( "a", class_="marginright5 link linkWithHash detailsLink")
    for a in a_tags:
        links.append(a['href']) 
    return links

TEST_URLLIST_OLX = [
    'https://www.olx.ua/obyavlenie/spetsialist-po-podklyucheniyu-interneta-IDGnCkB.html',
    'https://www.olx.ua/obyavlenie/menedzher-po-robot-s-klentami-IDGkGK6.html',
]

@listhandler_bs(threads_limit=5)
def get_date_time_from_olx(urllist, soup=None):
    ''' Получает строку, содержащую дату и время публикации объявления '''
    em = soup.find('em')
    row_text = em.get_text().strip()
    return row_text

class BSListMPTest(unittest.TestCase):
     
    def test_soup_list(self):
        data = get_date_time_from_olx(TEST_URLLIST_OLX)
        
        counter = 0  # чтобы проверить, что собрано элементов данных больше нуля
        for item in data:
            counter =+ 1
            print(item)
            self.assertRegex(item, r'([0-1]\d|2[0-3])(:[0-5]\d)')  # время HH:MM
            self.assertRegex(item, r'\d{1,}\s([а-яА-ЯёЁ]){1,}\s\d\d\d\d')  # дата 29 июня 2019  2 июля 2019
        self.assertGreater(counter, 0)
        
#**************************************************************************************************



if __name__ == '__main__' :
    unittest.main()