import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By

from log import logger
from selectorsConfig import selectorsConfig


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger(__name__)


class CompanyParser:
    def __init__(self, url=None, browser=None, save=False):
        self._url = url
        self._soup = None
        self._data = {}
        self._lastPage = None
        if browser is not None:
            self._browser = browser
        else:
            self._browser = webdriver.Chrome()
            self._browser.maximize_window()
        self._save = save

    def _generateSoup(self):
        page = requests.get(self._url)
        self._soup = bs(page.text, 'html.parser')

    def _fingPagination(self):
        try:
            self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        except:
            self._lastPage = 1
        log.info(f"Последняя страница с номером: <{self._lastPage}>")

    def _getCompanies(self):
        companiesBlock = self._soup.find('div', {'class': selectorsConfig.companiesPage["companiesBlock"]})
        log.debug("Получен блок со всеми компаниями")
        return companiesBlock.find_all('div', {'class': selectorsConfig.companiesPage["companies"]})

    def _addCompany(self, companyData):
        self._data[companyData.pop('Name')] = companyData

    def _writeFileSummaryOfCompanies(self):
        path = DATA_DIRECTORY / "summary_of_companies"
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._data, file, indent=4, ensure_ascii=False)
        log.debug("Запись прошла успешно!")

    def _generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Получена ссылка на следующую страницу page <{'/'.join(url)}>")
            return "/".join(url)

    def _getCompanySubscribers(self, companyCountersBlock, companyID):
        companySubscribers = companyCountersBlock.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "subscribers", companyID)).text
        if "K" in companySubscribers:
            return float(companySubscribers.replace("K", "")) * 1000
        return float(companySubscribers)

    def _getCompanyHubs(self, browser, companyID):
        try:
            companyHubsBlock = browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "hubsBlock", companyID))
            return [hub.text for hub in companyHubsBlock.find_elements(By.CLASS_NAME, selectorsConfig.company["hubs"])]
        except:
            return None

    def _getCompanyAbout(self, browser):
        try:
            return browser.find_element(By.XPATH, selectorsConfig.company["about"][0]).text
        except:
            return browser.find_element(By.XPATH, selectorsConfig.company["about"][1]).text

    def _getInfoAboutCompany(self, browser, companyID):
        companyShortInfoBlock = browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "shortInfoBlock", companyID))
        companyName = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["name"]).text
        log.debug(f"Получение сведений о компании <{companyName}> с ID<{companyID}>...")
        companyDescription = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["description"]).text
        companyProfile = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["profile"]).get_attribute("href")
        companyCountersBlock = browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "countersBlock", companyID))
        companyRating = float(companyCountersBlock.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "rating", companyID)).text)
        companySubscribers = self._getCompanySubscribers(companyCountersBlock, companyID)
        companyHubs = self._getCompanyHubs(browser, companyID)
        if companyHubs is None:
            log.warning(f"У компании <{companyName}> нет Хабов")
        browser.get(companyProfile)
        industriesBlock = browser.find_element(By.CLASS_NAME, selectorsConfig.company["industriesBlock"])
        industries = [industry.text for industry in industriesBlock.find_elements(By.CLASS_NAME, selectorsConfig.company["industries"])]
        companyAbout = self._getCompanyAbout(browser)
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
        log.debug("Запуск parserCompany")
        self._generateSoup()
        self._browser.get(self._url)
        self._fingPagination()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            log.debug(f"Переход на страницу <{page}>")
            for companyID, company in enumerate(self._getCompanies(), start=1):
                self._addCompany(self._getInfoAboutCompany(self._browser, companyID))
                self._browser.get(self._url)
            self._browser.get(self._url)
            self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
            self._url = self._generateNextPageUrl(page)
            if page > self._lastPage:
                log.error(f"Страницы с номером <{page}> не существует!")
            self._browser.close()
            break
        log.debug("Парсер завершил работу успешно!")
        if self._save:
            self._writeFileSummaryOfCompanies()


if __name__ == "__main__":
    parser = CompanyParser("https://habr.com/ru/companies/page1/")
    parser.start()
    parser._writeFileSummaryOfCompanies()
