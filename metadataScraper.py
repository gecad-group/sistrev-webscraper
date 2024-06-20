import shutil
import selenium.webdriver.firefox.webdriver
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time
from configparser import ConfigParser

import prerunchecks


class metadataScraper:
    url = "https://www.webofscience.com/wos/woscc/basic-search"

    driver: selenium.webdriver.firefox.webdriver.WebDriver | None

    def __init__(self, download_path: str = os.getenv("temp") + '\\SistRev\\' if os.name == 'nt' else "/tmp/SistRev/", ignore_limits=False):
        self.driver = None
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.download_path = os.path.abspath(download_path)
        self.ignore_limits = ignore_limits

        shutil.rmtree(self.download_path, ignore_errors=True)
        os.makedirs(self.download_path, exist_ok=True)

        self.options = webdriver.FirefoxOptions()
        self.options.set_preference("browser.download.folderList", 2)
        self.options.set_preference("browser.download.dir", self.download_path)
        self.options.set_preference("browser.helperApps.neverAsk.saveToDisk", "*")
        if self.config.getboolean('metaScraper', 'headless_driver'):
            self.options.add_argument("--headless")
            print("Running headless")

    def scrape(self, search: str) -> list[str]:
        prerunchecks.check_network()

        if self.driver is None:
            self.driver = webdriver.Firefox(options=self.options)

        driver = self.driver

        # setup the wait
        wait = WebDriverWait(driver, 10)

        # clear any savedrecs.ris that might remain from previous executions
        if os.path.isfile(self.download_path + '/savedrecs.ris'):
            os.remove(self.download_path + '/savedrecs.ris')

        # Go to the url
        driver.get(self.url)

        # Waiting for the cookies accept/deny box
        try:
            wait.until(
                EC.visibility_of_element_located((By.XPATH, self.config.get('metaScraper', 'xpath_search_box'))))
        except TimeoutException:
            print("Check if you are connected to the VPN. If you are, WoS might be down")

        # The animations take some time to allow me to click the buttons
        time.sleep(2)

        # Accept the cookies (It's useless to store them, they get reset on each scrape, but it makes the site happy)
        try:
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_accept_cookies')).click()
        except NoSuchElementException:
            pass

        # Type the search into the correct box
        search_box = driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_search_box'))
        search_box.clear()
        search_box.send_keys(search)

        # Hack to click the accept button, as the interaction blocker still exists, although invisible
        driver.execute_script("arguments[0].click()",
                              driver.find_element(
                                  By.XPATH,
                                  self.config.get('metaScraper', 'xpath_search_btn')
                              )
                              )

        wait.until(
            EC.visibility_of_element_located((By.XPATH, self.config.get('metaScraper', 'xpath_export_sel'))))

        print("We are on", driver.title)

        # This is not the regular - ! It's slightly longer, pay attention to that when editing the script
        # I will leave the longer one here in case you don't lose it:  –
        #                                      (See? It's longer)      -
        n_articles = int(driver.title.split(' – ')[1].replace(',', ''))

        print("Number of articles: ", n_articles)

        n_limit = self.config.getint('metaScraper', 'article_limit')

        if n_articles > n_limit:
            print("WARNING: Number of articles is larger than the limit")
            if self.ignore_limits is True:
                r = input(f"Number of articles ({n_articles}) larger than the set limit of {n_limit}!\n"
                          f"How many to download? (0 for all, -1 for none, ENTER for {n_limit}): ")
                if len(r) == 0:
                    n_articles = n_limit
                elif int(r) == 0:
                    print("WARNING: This might take a while...")
                elif int(r) < 0:
                    return []
                else:
                    n_articles = int(r)
            else:
                n_articles = n_limit

        print(f"Downloading {n_articles}.")

        file_list = []

        for i in metadataScraper.getListOfRanges(n_articles):
            # This refreshes the page, resetting the input box ids
            driver.refresh()
            time.sleep(2)

            wait.until(EC.visibility_of_element_located((By.XPATH, self.config.get('metaScraper', 'xpath_export_sel'))))

            # Click the export dropdown
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_export_sel')).click()

            # Click on the export ris option
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_export_ris')).click()

            # Select download range of data
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_records_range')).click()

            # Fill start of range
            start = driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_records_range_start'))
            start.clear()
            start.send_keys(str(i[0]))

            # Fill end of range
            end = driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_records_range_end'))
            end.clear()
            end.send_keys(str(i[1]))

            # Info to export
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_info_sel')).click()
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_info_abst_btn')).click()
            # Click the export button
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_export_btn')).click()

            print(f"Downloading the metadata ({i[0]} to {i[1]})...", end='')

            time.sleep(2)

            while not os.path.exists(self.download_path + "/savedrecs.ris"):
                time.sleep(5)

            final_filename = self.download_path + f"/{search.lower().replace(' ', '_').replace('"', '')}_{i[0]}_{i[1]}.ris"

            time.sleep(2)

            os.rename(os.path.abspath(self.download_path + "/savedrecs.ris"), final_filename)

            file_list.append(final_filename)

            print("  (DONE)")

        return file_list

    def quit_driver(self):
        if self.driver is not None:
            self.driver.quit()

    def getListOfRanges(total: int) -> list[tuple[int, int]]:
        output = []
        for i in range(1, total, 1000):
            output.append((i, i + 999 if (i+999) < total else total))

        return output


if __name__ == "__main__":
    scraper = metadataScraper(download_path="downloads")
    keyword = input("What will we research today? ")

    scraper.scrape(keyword)

    print(f"Check {scraper.download_path} for your files.")

    scraper.quit_driver()
