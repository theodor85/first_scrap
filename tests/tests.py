import unittest
from firstscrap.pagehandler import PageHandler 

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


class Handler_classinform_BS(PageHandler):
    
    def __init__(self):
        super().__init__()
        self.URL = 'https://classinform.ru/okpo/01/ogrn1020100001778.html'
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, selenium_driver=None):

        data = []

        h2 = soup.find( "h2" )
        header = h2.get_text().strip()

        data.append(header)
        return data

class Handler_classinform_Selenium(PageHandler):
    
    def __init__(self):
        super().__init__()
        self.URL = 'https://classinform.ru/okpo/01/ogrn1020100001778.html'
        self.UseSelenium = True

    def extract_data_from_html(self, soup=None, selenium_driver=None):

        data = []

        selenium_driver.get(self.URL)

        h2 = selenium_driver.find_element_by_tag_name( "h2" )
        header = h2.text.strip()

        data.append(header)
        return data


class BSOnePageTest ( unittest.TestCase ):
    
    def test_soup ( self ):

        handler = Handler_classinform_BS()
        data = handler.execute()

        self.assertEqual(data[0], 
            'Гиагинское районное отделение Адыгейской республиканской общественной организации охотников и рыболовов' )


class SeleniumOnePageTest ( unittest.TestCase ):
    
    def test_selenium ( self ):

        handler = Handler_classinform_Selenium()
        data = handler.execute()

        self.assertEqual(data[0], 
            'Гиагинское районное отделение Адыгейской республиканской общественной организации охотников и рыболовов' )



if __name__ == '__main__' :
    unittest.main()