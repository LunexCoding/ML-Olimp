import string
from pathlib import Path
import time

from selenium.webdriver.common.by import By

from log import logger
from const import (
    ARTICLE_TITLE_NOT_FOUND,
    ARTICLE_DESCRIPTION_NOT_FOUND,
    ARTICLE_PUBLICATION_DATE_NOT_FOUND,
    ARTICLE_RATING_NOT_FOUND
)
from selectorsConfig import selectorsConfig
from parsers.parser import Parser


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger(__name__)


class ArticleParser(Parser):
    def __init__(self, companyName=None, url=None, browser=None):
        super().__init__(url, browser)
        self._companyName = companyName
        self._companyArticles = []


    def _getArticles(self):
        return self.findElements(By.CLASS_NAME, selectorsConfig.blog["articles"])

    def _addAritcle(self, articleData):
        self._companyArticles.append(articleData)

    def _getInfoAboutArticle(self, article, articleID):
        title = self.__getTitle(article)
        date = self.__getDate(article)
        rating = self.__getRating(article, articleID)
        description = self.__getDescription(article, articleID)
        log.debug(f"Статья <{articleID}/{len(self._companyArticles) + 1}>: {title[:50]}...")
        return {
            "title": title,
            "description": description,
            "data": date,
            "rating": rating
        }

    def __getCompanyName(self):
        if self._companyName is None:
            companyCardInfo = self.findElement(By.XPATH, selectorsConfig.article["companyCardInfo"])
            self._companyName = self.findElement(By.TAG_NAME, "a", companyCardInfo).text

    def __getTitle(self, article):
        title = self.findElement(By.CLASS_NAME, selectorsConfig.article["title"], article).text
        return title if title else ARTICLE_TITLE_NOT_FOUND

    def __getDescription(self, article, articleID):
        description = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("article", "description", articleID), article).text
        return description if description else ARTICLE_DESCRIPTION_NOT_FOUND

    def __getRating(self, article, articleID):
        rating = int(self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("article", "rating", articleID), article).text)
        return rating if rating else ARTICLE_RATING_NOT_FOUND

    def __getDate(self, article):
        date = self.findElement(By.TAG_NAME, selectorsConfig.article["date"], article).get_attribute("title")
        return date if date else ARTICLE_PUBLICATION_DATE_NOT_FOUND


    def start(self, save=False):
        log.debug("Старт ArticleParser")
        self._browser.get(self._url)
        self.fingPagination()
        self.__getCompanyName()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(148, self._lastPage + 1):
            log.debug(f"Переход на страницу с номером <{page}>")
            for articleID, article in enumerate(self._getArticles(), start=1):
                self._addAritcle(self._getInfoAboutArticle(article, articleID))
            self.checkNextPage(page)
        log.debug(f"У компании {self._companyName}: {len(self._companyArticles)} статей")
        log.debug("Парсер завершил работу успешно!")
        if save:
            path = Path(DATA_DIRECTORY / "articles" / self._companyName.translate(str.maketrans('', '', string.punctuation))).with_suffix(FILE_SUFFIX)
            self.saveData(path, self._companyArticles)

    @property
    def companyArticles(self):
        return self._companyArticles


if __name__ == "__main__":
    start_time = time.time()
    parser = ArticleParser(url="https://habr.com/ru/companies/ruvds/articles/page148/")
    parser.start(save=True)
    print(round((time.time() - start_time) / 60, 2))
