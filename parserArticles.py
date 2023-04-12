import string
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from log import logger


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger("parserArticles")


class ArtricleParser:
    def __init__(self, url=None):
        self._url = url
        self._companyArticles = []
        self._companyName = None
        self._browser = webdriver.Chrome()
        self._browser.maximize_window()

    def _writeFileCompanyArticles(self):
        path = DATA_DIRECTORY / "articles" / self._companyName.translate(str.maketrans('', '', string.punctuation))
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._companyArticles, file, indent=4, ensure_ascii=False)
        log.debug("Data writing was successful")

    def _getArticles(self):
        return self._browser.find_elements(By.CLASS_NAME, "tm-articles-list__item")

    def _addAritcle(self, article):
        self._companyArticles.append(article)

    def __getDescriptionXPATH(self, article, articleID):
        xpaths = [
            f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[5]/div[1]/div[1]/div[1]",
            f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[5]/div[2]/div[1]/div[1]",
            f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[4]/div[1]/div[1]/div[1]",
            f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[5]/div[1]/div[1]/div[1]",
        ]
        for xpath in xpaths:
            try:
                return article.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                continue

    def _getInfoAboutArticle(self, browser, article, articleID):
        title = article.find_element(By.CLASS_NAME, "tm-title__link").find_element(By.TAG_NAME, "span").text
        date = article.find_element(By.TAG_NAME, "time").get_attribute("title")
        rating = article.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[2]/div[1]/span[1]").text
        description = self.__getDescriptionXPATH(article, articleID)
        return {
            "title": title,
            "description": description,
            "data": date,
            "rating": rating
        }

    def _generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Received a link to the following page <{'/'.join(url)}>")
            return "/".join(url)

    def start(self):
        log.debug("ArticleParser run")
        self._browser.get(self._url)
        self._companyName = self._browser.find_element(By.CLASS_NAME, "tm-company-card__name").text
        try:
            self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        except:
            self._lastPage = 1
        log.info(f"Last page number: <{self._lastPage}>")
        for page in range(self._lastPage, 1 + 1):
            log.debug(f"Jump to page number <{page}>")
            try:
                for articleID, article in enumerate(self._getArticles(), start=1):
                    self._addAritcle(self._getInfoAboutArticle(self._browser, article, articleID))
                self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
                self._url = self._generateNextPageUrl(page)
                time.sleep(2)
                self._browser.get(self._url)
            except Exception as e:
                if page > self._lastPage:
                    log.error(f"Page number <{page}> does not exist!")
                    self._browser.close()
                    break
        log.debug("ArticlesParser completed")

    @property
    def companyArticles(self):
        return self._companyArticles


if __name__ == "__main__":
    parser = ArtricleParser("https://habr.com/ru/companies/evateam/articles/page1/")
    parser.start()
    parser._writeFileCompanyArticles()
