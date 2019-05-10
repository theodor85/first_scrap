from .pagehandler import PageHandler
import os

class ProxyRefresher2ip(PageHandler):
    """."""

    def __init__(self):
        super(ProxyRefresher2ip, self).__init__()
        self.URL = 'https://2ip.ru/proxy/'
        self.UseSelenium = False

    def extract_data_from_html(self, soup=None, selenium_driver=None):
        data = []
        trs = soup.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            if tds:
                data.append( tds[0].get_text().strip() )

        return data

def proxy_refresher():

    refresher = ProxyRefresher2ip()
    new_proxy_list = refresher.execute()

    filename = os.path.dirname(os.path.realpath(__file__)) + '/proxy_list.txt'
    with open(filename, 'w') as f:
        for i in new_proxy_list:
            f.write( '{}\n'.format(i) )
