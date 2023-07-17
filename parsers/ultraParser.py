import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from parsers.parserArticles import ArtricleParser

from log import logger


FILE_SUFFIX = ".json"
DATA_DIRECTORY = Path("data")
log = logger.getLogger(__name__)


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
        log.debug("Получен блок со всеми компаниями")
        return companiesBlock.find_all('div', {'class': 'tm-companies__item tm-companies__item_inlined'})

    def _addCompany(self, companyData):
        self._data[companyData.pop('Name')] = companyData

    def _writeFileSummaryOfCompanies(self):
        path = DATA_DIRECTORY / "ULTRA_summary_of_companies"
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._data, file, indent=4, ensure_ascii=False)
        log.debug("Запись прошла успешно!")

    def _generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Получена ссылка на следующую страницу <{'/'.join(url)}>")
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
            log.warning(f"У компании <{companyName}> нет Хабов")
        browser.get(companyProfile)
        industriesBlock = browser.find_element(By.CLASS_NAME, "tm-company-profile__categories")
        industries = [industry.text for industry in industriesBlock.find_elements(By.CLASS_NAME, "tm-company-profile__categories-wrapper")]
        try:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[2]/dd[1]/span[1]").text
        except:
            companyAbout = browser.find_element(By.XPATH, "//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/section[1]/div[1]/div[1]/dl[3]/dd[1]/span[1]").text
        articlesParser = ArtricleParser(self._getArticlesUrl(browser.current_url))
        articlesParser.start()
        articles = articlesParser.companyArticles
        return {
            "Name": companyName,
            "Description": companyDescription,
            "About": companyAbout,
            "Industries": industries,
            "Rating": companyRating,
            "Subscribers": companySubscribers,
            "Hubs": companyHubs,
            "Profile": companyProfile,
            "Articles": articles
        }

    def _getArticlesUrl(self, url):
        urlSplit = url.split('/')
        urlSplit[-2] = "articles/page1"
        return "/".join(urlSplit)

    def start(self):
        log.debug("Запуск ultraParser")
        self._generateSoup()
        self._browser.get(self._url)
        self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        log.info(f"Последняя страница: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            log.debug(f"Переход на страницу <{page}>")
            try:
                for companyID, company in enumerate(self._getCompanies(), start=1):
                    self._addCompany(self._getInfoAboutCompany(self._browser, companyID))
                    self._browser.get(self._url)
                self._browser.get(self._url)
                self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
                self._url = self._generateNextPageUrl(page)
            except Exception as e:
                print(e)
                if page > self._lastPage:
                    log.error(f"Страница с номером <{page}> не существует!")
                    self._browser.close()
                    break
        log.debug("Парсер завершил работу успешно!")


if __name__ == "__main__":
    parser = Parser("https://habr.com/ru/companies/page1/")
    parser.start()
    parser._writeFileSummaryOfCompanies()
