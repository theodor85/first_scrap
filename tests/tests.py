import unittest

from firstscrap.pagehandler import PageHandler 

from firstscrap.pagehandler import pagehandler
# план тестирования
# Что тестируем                     | Имя тестового класса      | Готовность
#-----------------------------------------------------------------------
# BS - одиночная страница           | BSOnePageTest             | OK
# Selenium - одиночая стр.          | SeleniumOnePageTest       | OK
#-----------------------------------------------------------------------
# BS - список стр. - без процессов  | BSListWithoutMPTest       | -
# Sel - список стр. - без процессов | SeleniumListWithoutMPTest | -
# BS - список стр. - c процессами   | BSListMPTest              | -
# Sel - список стр. - c процессами  | SeleniumListMPTest        | -          

TEST_URL = 'https://classinform.ru/okpo/01/ogrn1020100001778.html'
CHECK_TEXT = 'Гиагинское районное отделение Адыгейской республиканской общественной организации охотников и рыболовов'

@pagehandler(use_selenium=False)
def get_data(url, soup=None):
    h2 = soup.find( "h2" )
    header = h2.get_text().strip()
    return header

@pagehandler(use_selenium=True)
def get_data_selenium(url, selenium=None):
    data = []
    h2 = selenium.find_element_by_tag_name( "h2" )
    header = h2.text.strip()
    data.append(header)
    return data    

   
class BSOnePageTest_decors(unittest.TestCase):
    def test_soup (self):
        data = get_data(TEST_URL)
        self.assertEqual(next(data), CHECK_TEXT)


class SeleniumOnePageTest_decors(unittest.TestCase):
    def test_selenium(self):
        data = get_data_selenium(TEST_URL)
        self.assertEqual(data[0], CHECK_TEXT)


if __name__ == '__main__' :
    unittest.main()