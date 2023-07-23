from pathlib import Path

from selenium.webdriver.common.by import By

from log import logger
from consts import (
    DATA_DIRECTORY,
    FILE_SUFFIX
)
from parsers.consts import (
    ELEMENT_NOT_FOUND,
    INVALID_COMPANY_INFO,
    COMPANY_NAME_NOT_FOUND,
    COMPANY_DESCRIPTION_NOT_FOUND,
    COMPANY_PROFILE_NOT_FOUND,
    COMPANY_RATING_NOT_FOUND,
    COMPANY_SUBSCRIBERS_NOT_FOUND,
    COMPANY_HUBS_NOT_FOUND,
    COMPANY_ABOUT_NOT_FOUND
)
from selectorsConfig import selectorsConfig
from parsers.parser import Parser
from parsers.parserArticles import ArticleParser


log = logger.getLogger("parsers/parserCompany.py")


class CompanyParser(Parser):
    def __init__(self, url, browser=None):
        super().__init__(url, browser)
        self._url = url
        self._companies = {}
        self._lastPage = None
        self._companyName = None
        self._companyProfile = None

    def _getCountCompanies(self):
        countCompanies = self.findElements(By.CLASS_NAME, selectorsConfig.companiesPage["company"])
        return len(countCompanies) if countCompanies else countCompanies

    def _addCompany(self, companyData):
        self._companies[companyData.pop('Name')] = companyData

    def _getCompanyShortInfoBlock(self, companyID):
        companyShortInfoBlock = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("company", "shortInfoBlock", companyID))
        return companyShortInfoBlock if companyShortInfoBlock else ELEMENT_NOT_FOUND

    def _getCompanyName(self, companyShortInfoBlock):
        companyName = self.findElement(By.CLASS_NAME, selectorsConfig.company["name"], companyShortInfoBlock)
        return companyName.text if companyName else COMPANY_NAME_NOT_FOUND

    def _getCompanyDescription(self, companyShortInfoBlock):
        companyDescription = self.findElement(By.CLASS_NAME, selectorsConfig.company["description"], companyShortInfoBlock)
        return companyDescription.text if companyDescription else COMPANY_DESCRIPTION_NOT_FOUND

    def _getCompanyProfile(self, companyShortInfoBlock):
        companyProfile = self.findElement(By.CLASS_NAME, selectorsConfig.company["profile"], companyShortInfoBlock)
        return companyProfile.get_attribute("href") if companyProfile else COMPANY_PROFILE_NOT_FOUND

    def _getCompanyCountersBlock(self, companyID):
        companyCountersBlock = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("company", "countersBlock", companyID))
        return companyCountersBlock if companyCountersBlock else ELEMENT_NOT_FOUND

    def _getCompanyRating(self, companyCountersBlock, companyID):
        companyRating = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("company", "rating", companyID), companyCountersBlock)
        return float(companyRating.text) if companyRating else COMPANY_RATING_NOT_FOUND

    def _getCompanySubscribers(self, companyCountersBlock, companyID):
        companySubscribers = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("company", "subscribers", companyID), companyCountersBlock)
        if companySubscribers:
            companySubscribers = companySubscribers.text
            return float(companySubscribers.replace("K", "")) * 1000 if "K" in companySubscribers else float(companySubscribers)
        return COMPANY_SUBSCRIBERS_NOT_FOUND

    def _getCompanyHubs(self, companyID):
        companyHubs = []
        companyHubsBlock = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("company", "hubsBlock", companyID))
        if companyHubsBlock:
            companyHubs = [hub.text for hub in self.findElements(By.CLASS_NAME, selectorsConfig.company["hubs"], companyHubsBlock)]
        return companyHubs if companyHubs else COMPANY_HUBS_NOT_FOUND

    def _getCompanyIndustries(self):
        companyIndustries = []
        companyIndustriesBlock = self.findElement(By.CLASS_NAME, selectorsConfig.company["industriesBlock"])
        if companyIndustriesBlock:
            companyIndustries = [industry.text for industry in self.findElements(By.CLASS_NAME, selectorsConfig.company["industries"], companyIndustriesBlock)]
        return companyIndustries if companyIndustries else ELEMENT_NOT_FOUND

    def _getCompanyAbout(self):
        companyAbout = self.findElement(By.XPATH, selectorsConfig.company["about"])
        return companyAbout.text if companyAbout else COMPANY_ABOUT_NOT_FOUND

    def _generateCompanyBlogUrl(self):
        return f'{self._companyProfile.replace("profile", "articles")}page1/'

    def _getInfoAboutCompany(self, companyID):
        companyShortInfoBlock = self._getCompanyShortInfoBlock(companyID)
        if companyShortInfoBlock is None:
            log.error(f"{COMPANY_NAME_NOT_FOUND} с ID<{companyID}/{len(self._companies) + 1}>")
            return INVALID_COMPANY_INFO
        self._companyName = self._getCompanyName(companyShortInfoBlock)
        log.info(f"Получение сведений о компании <{self._companyName}> с ID<{companyID}/{len(self._companies) + 1}>...")
        companyDescription = self._getCompanyDescription(companyShortInfoBlock)
        self._companyProfile = self._getCompanyProfile(companyShortInfoBlock)
        companyCountersBlock = self._getCompanyCountersBlock(companyID)
        if companyCountersBlock:
            companyRating = self._getCompanyRating(companyCountersBlock, companyID)
            companySubscribers = self._getCompanySubscribers(companyCountersBlock, companyID)
        else:
            companyRating = COMPANY_RATING_NOT_FOUND
            companySubscribers = COMPANY_SUBSCRIBERS_NOT_FOUND
        companyHubs = self._getCompanyHubs(companyID)
        self.openPage(self._companyProfile)
        companyIndustries = self._getCompanyIndustries()
        companyAbout = self._getCompanyAbout()
        return {
            "Name": self._companyName,
            "Description": companyDescription,
            "About": companyAbout,
            "Industries": companyIndustries,
            "Rating": companyRating,
            "Subscribers": companySubscribers,
            "Hubs": companyHubs,
            "Profile": self._companyProfile
        }


    def start(self, articles=False, save=False):
        log.debug("Запуск parserCompany")
        self.openPage(self._url)
        self.fingPagination()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            countCompanies = self._getCountCompanies()
            if countCompanies:
                for companyID in range(1, countCompanies + 1):
                    companyInfo = self._getInfoAboutCompany(companyID)
                    if companyInfo:
                        self._addCompany(companyInfo)
                        if articles:
                            companyBlog = self._generateCompanyBlogUrl()
                            articleParser = ArticleParser(companyBlog, self._companyName, self.browser)
                            companyArticles = articleParser.start(save=True)
                            self._companies[self._companyName]["Articles"] = companyArticles
                        self.openPage(self._url)
            self.openNextPage(page)
        log.info(f"Всего компаний проанализировано: {len(self._companies)}")
        log.debug("Парсер завершил работу успешно!")
        if save:
            path = Path(DATA_DIRECTORY / "summary_of_companies").with_suffix(FILE_SUFFIX)
            self.saveData(path, self._companies)


if __name__ == "__main__":
    parser = CompanyParser("https://habr.com/ru/companies/page1/")
    parser.start(articles=True, save=True)
