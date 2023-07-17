import string
from pathlib import Path
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from log import logger
from selectorsConfig import selectorsConfig
from parsers.parser import Parser


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger(__name__)


class ArticleParser(Parser):
    def __init__(self, url=None, browser=None):
        super().__init__(url, browser)
        self._url = url
        self._companyArticles = []
        self._companyName = None

    def _getArticles(self):
        return self._browser.find_elements(By.CLASS_NAME, selectorsConfig.blog["articles"])

    def _addAritcle(self, articleData):
        self._companyArticles.append(articleData)

    def __getTitle(self, article):
        try:
            return article.find_element(By.CLASS_NAME, selectorsConfig.article["title"]).text
        except NoSuchElementException:
            return None

    def __getDescriptionXPATH(self, article, articleID):
        xpaths = selectorsConfig.getXpathByParameters("article", "description", articleID)
        for xpath in xpaths:
            try:
                return article.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                pass

    def _getInfoAboutArticle(self, article, articleID):
        title = self.__getTitle(article)
        date = article.find_element(By.TAG_NAME, selectorsConfig.article["date"]).get_attribute("title")
        rating = int(article.find_element(By.XPATH, selectorsConfig.getXpathByParameters("article", "rating", articleID)).text)
        description = self.__getDescriptionXPATH(article, articleID)
        if title is not None:
            log.debug(f"Статья <{articleID}/{len(self._companyArticles) + 1}>: {title[:50] + '...'}")
        else:
            log.warning(f"Статья <{articleID}/{len(self._companyArticles) + 1}>: <Нет названия>")
        return {
            "title": title,
            "description": description,
            "data": date,
            "rating": rating
        }

    def start(self, save=False):
        log.debug("Старт ArticleParser")
        self._browser.get(self._url)
        self._companyName = self._browser.find_element(By.XPATH, selectorsConfig.article["companyCardInfo"]).find_element(By.TAG_NAME, "a").text
        self.fingPagination()
        log.info(f"Последняя страница с номером: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
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
    parser = ArticleParser("https://habr.com/ru/companies/ruvds/articles/page1/")
    parser.start(save=True)
    print(round((time.time() - start_time) / 60, 2))
