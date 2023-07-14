import string
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from log import logger
from selectorsConfig import selectorsConfig


DATA_DIRECTORY = Path("data")
FILE_SUFFIX = ".json"
log = logger.getLogger(__name__)


class ArticleParser:
    def __init__(self, url=None, browser=None, save=False):
        self._url = url
        self._companyArticles = []
        self._companyName = None
        self._lastPage = None
        if browser is not None:
            self._browser = browser
        else:
            self._browser = webdriver.Chrome()
            self._browser.maximize_window()
        self._save = save

    def _writeFileCompanyArticles(self):
        path = DATA_DIRECTORY / "articles" / self._companyName.translate(str.maketrans('', '', string.punctuation))
        with path.with_suffix(FILE_SUFFIX).open('w', encoding='utf-8') as file:
            json.dump(self._companyArticles, file, indent=4, ensure_ascii=False)
        log.debug("Данные успешно записаны")

    def _getArticles(self):
        return self._browser.find_elements(By.CLASS_NAME, selectorsConfig.blog["articles"])

    def _addAritcle(self, articleData):
        self._companyArticles.append(articleData)

    def __getDescriptionXPATH(self, article, articleID):
        xpaths = selectorsConfig.getXpathByParameters("article", "description", articleID)
        for xpath in xpaths:
            try:
                return article.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                continue

    def _getInfoAboutArticle(self, article, articleID):
        title = article.find_element(By.CLASS_NAME, selectorsConfig.article["title"]).text
        date = article.find_element(By.TAG_NAME, selectorsConfig.article["date"]).get_attribute("title")
        rating = int(article.find_element(By.XPATH, selectorsConfig.getXpathByParameters("article", "rating", articleID)).text)
        description = self.__getDescriptionXPATH(article, articleID)
        log.debug(f"Статья <{articleID}/{len(self._companyArticles) + 1}>: {title[:50] + '...'}")
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
            log.debug(f"Получена ссылка на следующую страницу <{'/'.join(url)}>")
            return "/".join(url)

    def _fingPagination(self):
        try:
            self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        except:
            self._lastPage = 1
        log.info(f"Последняя страница с номером: <{self._lastPage}>")

    def start(self):
        log.debug("Старт ArticleParser")
        self._browser.get(self._url)
        self._companyName = self._browser.find_element(By.XPATH, selectorsConfig.article["companyCardInfo"]).find_element(By.TAG_NAME, "a").text
        self._fingPagination()
        for page in range(1, self._lastPage + 1):
            log.debug(f"Переход на страницу с номером <{page}>")
            articles = self._getArticles()
            for articleID, article in enumerate(articles, start=1):
                self._addAritcle(self._getInfoAboutArticle(article, articleID))
            if page > self._lastPage:
                log.error(f"Страницы с номером <{page}> не существует!")
                self._browser.close()
                break
            self._browser.find_element(By.XPATH, selectorsConfig.page["nextPage"]).click()
            self._url = self._generateNextPageUrl(page)
            self._browser.get(self._url)
        log.debug(f"У компании {self._companyName}: {len(self._companyArticles)} статей")
        log.debug("Парсер завершил работу успешно!")
        if self._save:
            self._writeFileCompanyArticles()

    @property
    def companyArticles(self):
        return self._companyArticles


if __name__ == "__main__":
    parser = ArticleParser("https://habr.com/ru/companies/ruvds/articles/page1/")
    parser.start()
    parser._writeFileCompanyArticles()
