import string
from pathlib import Path

from selenium.webdriver.common.by import By

from log import logger
from consts import (
    DATA_DIRECTORY,
    FILE_SUFFIX
)
from parsers.consts import (
    ARTICLE_TITLE_NOT_FOUND,
    ARTICLE_DESCRIPTION_NOT_FOUND,
    ARTICLE_PUBLICATION_DATE_NOT_FOUND,
    ARTICLE_RATING_NOT_FOUND
)
from selectorsConfig import selectorsConfig
from parsers.parser import Parser


log = logger.getLogger("parsers/parserArticles.py")


class ArticleParser(Parser):
    def __init__(self, url, companyName=None, browser=None):
        super().__init__(url, browser)
        self._companyName = companyName
        self._companyArticles = []

    def _getArticles(self):
        return self.findElements(By.CLASS_NAME, selectorsConfig.blog["articles"])

    def _addAritcle(self, articleData):
        self._companyArticles.append(articleData)

    def _getInfoAboutArticle(self, article, articleID):
        title = self._getTitle(article)
        date = self._getDate(article)
        rating = self._getRating(article, articleID)
        description = self._getDescription(article, articleID)
        log.info(f"Статья <{articleID}/{len(self._companyArticles) + 1}>: {title[:50]}...")
        return {
            "title": title,
            "description": description,
            "data": date,
            "rating": rating
        }

    def _getCompanyName(self):
        if self._companyName is None:
            companyCardInfo = self.findElement(By.XPATH, selectorsConfig.article["companyCardInfo"])
            self._companyName = self.findElement(By.TAG_NAME, "a", companyCardInfo).text

    def _getTitle(self, article):
        title = self.findElement(By.CLASS_NAME, selectorsConfig.article["title"], article)
        return title.text if title else ARTICLE_TITLE_NOT_FOUND

    def _getDescription(self, article, articleID):
        description = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("article", "description", articleID), article)
        return description.text if description else ARTICLE_DESCRIPTION_NOT_FOUND

    def _getRating(self, article, articleID):
        rating = self.findElement(By.XPATH, selectorsConfig.getXpathByParameters("article", "rating", articleID), article)
        return int(rating.text) if rating else ARTICLE_RATING_NOT_FOUND

    def _getDate(self, article):
        date = self.findElement(By.TAG_NAME, selectorsConfig.article["date"], article).get_attribute("title")
        return date if date else ARTICLE_PUBLICATION_DATE_NOT_FOUND


    def start(self, save=False):
        log.debug("Запуск ArticleParser")
        self.openPage(self._url)
        self.fingPagination()
        self._getCompanyName()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            articles = self._getArticles()
            if articles:
                for articleID, article in enumerate(articles, start=1):
                    self._addAritcle(self._getInfoAboutArticle(article, articleID))
                self.checkNextPage(page)
            else:
                log.error(f"Не удалось получить статьи на странице <{page}>")
        log.info(f"У компании {self._companyName}: {len(self._companyArticles)} статей")
        log.debug("Парсер завершил работу успешно!")
        if save:
            path = Path(DATA_DIRECTORY / "articles" / self._companyName.translate(str.maketrans('', '', string.punctuation))).with_suffix(FILE_SUFFIX)
            self.saveData(path, self._companyArticles)
        return self._companyArticles

    @property
    def companyArticles(self):
        return self._companyArticles


if __name__ == "__main__":
    parser = ArticleParser(url="https://habr.com/ru/companies/ruvds/articles/page148/")
    parser.start(save=True)

