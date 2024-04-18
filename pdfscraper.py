import pycurl
from io import BytesIO
import certifi


class PDFScraper:
    def __init__(self):
        pass


if __name__ == '__main__':
    buffer = BytesIO()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://www.doi.org/10.1109/ecai50035.2020.9223186')
    c.setopt(pycurl.WRITEDATA, buffer)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(pycurl.VERBOSE, False)
    c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0')
    c.setopt(pycurl.COOKIEJAR, 'cookie')
    c.setopt(pycurl.COOKIEFILE, 'cookie')
    c.perform()

    final_url: str = c.getinfo(pycurl.EFFECTIVE_URL)
    id: str = final_url.rstrip('/').rsplit('/')[-1]

    print(final_url)
    print(id)

    import prerunchecks
    prerunchecks.check_network()

    with open('out.pdf', 'wb') as f:
        c.setopt(pycurl.URL, f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={id}")
        c.setopt(pycurl.WRITEDATA, f)
        c.perform()


