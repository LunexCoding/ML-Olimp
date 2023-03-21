import json
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from log import logger


FILE_SUFFIX = ".json"
DATA_DIRECTORY = Path("data")
log = logger.getLogger("parser")


class Parser:
    def __init__(self, url=None):
        self._url = url
        self._soup = None
        self._data = {}
        self._lastPage = None
        self._browser = webdriver.Chrome()
        self._browser.maximize_window()

    def _generateSoup(self):
        page = requests.get(self._url)
        self._soup = bs(page.text, 'html.parser')

    def _getCompanies(self):
        companiesBlock = self._soup.find('div', {'class': 'tm-companies'})
        log.debug("Received a block with all enterprises")
        return companiesBlock.find_all('div', {'class': 'tm-companies__item tm-companies__item_inlined'})

    def _addCompany(self, companyData):
        self._data[companyData.pop('Name')] = companyData

    def _writeFileSummaryOfCompanies(self):
        path = DATA_DIRECTORY / "summary_of_companies"
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._data, file, indent=4, ensure_ascii=False)
        log.debug("Data writing was successful")

    def _generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Received a link to the following page <{'/'.join(url)}>")
            return "/".join(url)

    def _getInfoAboutCompany(self, browser, companyID):
        companyShortInfoBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[1]/div[1]")
        companyName = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__title").text
        log.debug(f"Parsing a company with a name <{companyName}> with ID<{companyID}>")
        companyDescription = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__description").text
        companyProfile = companyShortInfoBlock.find_element(By.CLASS_NAME, "tm-company-snippet__title").get_attribute("href")
        companyCountersBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]")
        companyRating = float(companyCountersBlock.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]/span[1]").text)
        companySubscribers = companyCountersBlock.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[2]/span[2]").text
        if "K" in companySubscribers:
            companySubscribers = float(companySubscribers.replace("K", "")) * 1000
        else:
            companySubscribers = float(companySubscribers)
        try:
            companyHubsBlock = browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[2]")
            companyHubs = [hub.text for hub in companyHubsBlock.find_elements(By.CLASS_NAME, "tm-companies__hubs-item")]
        except:
            companyHubs = []
            log.warning(f"Company <{companyName}> has no hubs")
        browser.get(companyProfile)
        industriesBlock = browser.find_element(By.CLASS_NAME, "tm-company-profile__categories")
        industries = [industry.text for industry in industriesBlock.find_elements(By.CLASS_NAME, "tm-company-profile__categories-wrapper")]
        try:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[2]/dd[1]/span[1]").text
        except:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[3]/dd[1]/span[1]").text
        return {
            "Name": companyName,
            "Description": companyDescription,
            "About": companyAbout,
            "Industries": industries,
            "Rating": companyRating,
            "Subscribers": companySubscribers,
            "Hubs": companyHubs,
            "Profile": companyProfile
        }

    def start(self):
        log.debug("Parser run")
        self._generateSoup()
        self._browser.get(self._url)
        self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        log.info(f"Last page number: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            log.debug(f"Jump to page number <{page}>")
            try:
                for companyID, company in enumerate(self._getCompanies(), start=1):
                    self._addCompany(self._getInfoAboutCompany(self._browser, companyID))
                    self._browser.get(self._url)
                self._browser.get(self._url)
                self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
                self._url = self._generateNextPageUrl(page)
                time.sleep(2)
            except Exception as e:
                if page > self._lastPage:
                    log.error(f"Page number <{page}> does not exist!")
                self._browser.close()
                break
        self._writeFileSummaryOfCompanies()
        log.debug("Parser completed")


if __name__ == "__main__":
    parser = Parser("https://habr.com/ru/companies/page1/")
    parser.start()