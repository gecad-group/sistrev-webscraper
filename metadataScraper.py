import re

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
    download_path = os.getenv("temp") + '\\SistRev\\'

    url = "https://www.webofscience.com/wos/woscc/basic-search"

    driver: selenium.webdriver.firefox.webdriver.WebDriver | None

    def __init__(self):
        self.driver = None
        self.config = ConfigParser()
        self.config.read('config.ini')

        os.makedirs(metadataScraper.download_path, exist_ok=True)

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

        # Deny the cookies (It's useless to store them, they get reset on each scrape)
        try:
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_deny_cookies')).click()
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
        # I will leave a longer one here in case you don't lose it:  –
        #                                    (See? It's longer)      -
        n_articles = int(driver.title.split(' – ')[1].replace(',', ''))

        print("Number of articles: ", n_articles)

        file_list = []

        for i in range(1, n_articles, 1000):
            # This refreshes the page, resetting the input box ids
            driver.refresh()

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
            start.send_keys(str(i))

            # Fill end of range
            end = driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_records_range_end'))
            end.clear()
            end.send_keys(str(i+999))

            # Info to export
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_info_sel')).click()
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_info_abst_btn')).click()

            # Click the export button
            driver.find_element(By.XPATH, self.config.get('metaScraper', 'xpath_export_btn')).click()

            print(f"Downloading the metadata ({i} to {i+999})...", end='')

            while not os.path.exists(self.download_path + "/savedrecs.ris"):
                time.sleep(2)

            final_filename = self.download_path + f"/{search.lower().replace(' ', '_')}_{i}_{i+999}.ris"

            os.rename(self.download_path + "/savedrecs.ris", final_filename)

            file_list.append(final_filename)

            print("  (DONE)")

        return final_filename


    def quit_driver(self):
        if self.driver is not None:
            self.driver.quit()

    def getListOfRanges(total: int) -> list[tuple[int, int]]:
        output = []
        for i in range(1, total, 1000):
            output.append((i, i+999))

        return output


if __name__ == "__main__":
    metadataScraper = metadataScraper()
    # metadataScraper.scrape("Machine Learning")
    # metadataScraper.scrape("Artificial Intelligence")
    metadataScraper.scrape("GPT-2")
    metadataScraper.scrape("Machine Learning Java")

    metadataScraper.quit_driver()
