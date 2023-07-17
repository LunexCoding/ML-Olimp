import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

from log import logger
from selectorsConfig import selectorsConfig
from parsers.parser import Parser


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger(__name__)


class CompanyParser(Parser):
    def __init__(self, url=None, browser=None):
        super().__init__(url, browser)
        self._url = url
        self._data = {}
        self._lastPage = None

    def _getCountCompanies(self):
        count = 0
        companyID = 1
        while True:
            try:
                self._browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("companiesPage", "companies", companyID))
                count += 1
                companyID += 1
            except NoSuchElementException:
                return count

    def _addCompany(self, companyData):
        self._data[companyData.pop('Name')] = companyData

    def _getCompanyShortInfoBlock(self, companyID):
        try:
            return self._browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[1]/div[1]")
        except NoSuchElementException:
            return self._browser.find_element(By.XPATH, f"//body/div[@id='app']/div[1]/div[2]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[{companyID}]/div[1]/div[1]")

    def _getCompanySubscribers(self, companyCountersBlock, companyID):
        companySubscribers = companyCountersBlock.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "subscribers", companyID)).text
        if "K" in companySubscribers:
            return float(companySubscribers.replace("K", "")) * 1000
        return float(companySubscribers)

    def _getCompanyHubs(self, companyID):
        try:
            companyHubsBlock = self._browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "hubsBlock", companyID))
            return [hub.text for hub in companyHubsBlock.find_elements(By.CLASS_NAME, selectorsConfig.company["hubs"])]
        except NoSuchElementException:
            return None

    def _getCompanyAbout(self):
        xpaths = selectorsConfig.company["about"]
        for xpath in xpaths:
            try:
                return self._browser.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                pass


    def _getInfoAboutCompany(self, companyID):
        companyShortInfoBlock = self._getCompanyShortInfoBlock(companyID)
        companyName = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["name"]).text
        log.debug(f"Получение сведений о компании <{companyName}> с ID<{companyID}>...")
        companyDescription = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["description"]).text
        companyProfile = companyShortInfoBlock.find_element(By.CLASS_NAME, selectorsConfig.company["profile"]).get_attribute("href")
        companyCountersBlock = self._browser.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "countersBlock", companyID))
        companyRating = float(companyCountersBlock.find_element(By.XPATH, selectorsConfig.getXpathByParameters("company", "rating", companyID)).text)
        companySubscribers = self._getCompanySubscribers(companyCountersBlock, companyID)
        companyHubs = self._getCompanyHubs(companyID)
        if companyHubs is None:
            log.warning(f"У компании <{companyName}> нет Хабов")
        self._browser.get(companyProfile)
        industriesBlock = self._browser.find_element(By.CLASS_NAME, selectorsConfig.company["industriesBlock"])
        industries = [industry.text for industry in industriesBlock.find_elements(By.CLASS_NAME, selectorsConfig.company["industries"])]
        companyAbout = self._getCompanyAbout()
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

    def start(self, save=False):
        log.debug("Запуск parserCompany")
        self._browser.get(self._url)
        self.fingPagination()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            log.debug(f"Переход на страницу с номером <{page}>")
            for companyID in range(1, self._getCountCompanies() + 1):
                self._addCompany(self._getInfoAboutCompany(companyID))
                self._browser.get(self._url)
            self.checkNextPage(page)
            log.debug(f"Переход на страницу <{page + 1}>")
            time.sleep(2)
        log.info(f"Всего компаний проанализировано: {len(self._data)}")
        log.debug("Парсер завершил работу успешно!")
        if save:
            path = Path(DATA_DIRECTORY / "summary_of_companies").with_suffix(FILE_SUFFIX)
            self.saveData(path, self._data)


if __name__ == "__main__":
    parser = CompanyParser("https://habr.com/ru/companies/page1/")
    parser.start(save=True)
