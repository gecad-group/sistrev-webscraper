import pycurl
from io import BytesIO
import certifi
from urllib.parse import urlparse
from scidownl import scihub_download
from scidownl.core.task import ScihubTask
import rispy
import os
import re
from datacleaner import DataCleaner

try:
    import readline
except:
    pass #readline not available

scihub_urls = ['https://sci-hub.se', 'https://sci-hub.st', 'https://sci-hub.yt']

class PDFScraper:
    def download_with_doi(doi: str, filename: str):
        filename = PDFScraper._clean_title(filename)
        #print('Getting', filename)
        #scihub_download(doi, paper_type='doi', out=filename)

        for url in scihub_urls:
            try:
                ScihubTask(doi, 'doi', out=filename)._run(url)

                filesize = os.stat(filename + ".pdf").st_size
                if filesize < 300:
                    os.remove(filename + ".pdf")
                    raise Exception(f"File is too small ({filesize})")

                return None
            except Exception as e:
                print("Not found on", url, ":", e.args[0] if len(e.args) > 0 else "Error didn't have a message")
                continue
        print("Failed to get", doi)
        return doi

    def download_from_ris(filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = rispy.load(f, encoding='utf-8')

        os.chdir(os.path.dirname(filepath))

        failed: list[str] = []

        for doc in data:
            print()
            print('Getting', doc['title'])
            res = PDFScraper.download_with_doi(doc['doi'], doc['title'])
            if res != None:
                failed.append(doc['doi'])

        return failed, len(data)

    def _clean_title(title: str) -> str:
        tmp = title.replace(':', '').replace('\\', '-').replace('/', '-').replace(' ', '_').replace('"', '')
        tmp = re.sub('<.*?>', '', tmp)

        return tmp

class PDFScraper_OLD:
    MOCK_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'

    def __init__(self):
        pass

    def get_publisher_url(self, doi_id: str):
        buffer = BytesIO()

        url = f'https://doi.org/{doi_id}'
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(pycurl.VERBOSE, False)

        try:
            c.perform()

            dest_url: str = c.getinfo(pycurl.EFFECTIVE_URL)
            return urlparse(dest_url).hostname
        except:
            return None


# if __name__ == '__main__':
#     buffer = BytesIO()
#
#     c = pycurl.Curl()
#     c.setopt(pycurl.URL, 'https://www.doi.org/10.1109/ecai50035.2020.9223186')
#     c.setopt(pycurl.WRITEDATA, buffer)
#     c.setopt(pycurl.FOLLOWLOCATION, True)
#     c.setopt(pycurl.CAINFO, certifi.where())
#     c.setopt(pycurl.VERBOSE, False)
#     c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0')
#     c.setopt(pycurl.COOKIEJAR, 'cookie')
#     c.setopt(pycurl.COOKIEFILE, 'cookie')
#     c.perform()
#
#     final_url: str = c.getinfo(pycurl.EFFECTIVE_URL)
#     id: str = final_url.rstrip('/').rsplit('/')[-1]
#
#     print(final_url)
#     print(id)
#
#     import prerunchecks
#
#     prerunchecks.check_network()
#
#     with open('out.pdf', 'wb') as f:
#         c.setopt(pycurl.URL, f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={id}")
#         c.setopt(pycurl.WRITEDATA, f)
#         c.perform()

if __name__ == '__main__':
    risfile = input("Path for the .ris file to import: ").replace('"', '')

    failed_downloads, total = PDFScraper.download_from_ris(risfile)

    print()
    print(" Failed downloads ")
    print("------------------")
    for doi in failed_downloads:
        print("https://doi.org/" + doi)

    print("Total Failed", len(failed_downloads), "/", total )
    print("Try checking the publisher using the addresses above or searching for the DOI in "
          "https://www.researchgate.net/")
