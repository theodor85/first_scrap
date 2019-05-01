import unittest
from firstscrap.pagehandler import PageHandler 

class Handler_classinform_1(PageHandler):
    
    def __init__(self):
        super().__init__()
        self.URL = 'https://classinform.ru/okpo/01/ogrn1020100001778.html'
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, driver=None):

        data = []

        h2 = soup.find( "h2" )
        header = h2.get_text().strip()

        data.append(header)
        return data

class PageHandlerSoupTest ( unittest.TestCase ):
    
    def test_soup ( self ):

        handler = Handler_classinform_1()
        data = handler.execute()

        self.assertEqual(data[0], 
            'Гиагинское районное отделение Адыгейской республиканской общественной организации охотников и рыболовов' )



if __name__ == '__main__' :
    unittest.main()