import time
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from log import logger


log = logger.getLogger("parserArticles")


class ArtricleParser:
    def __init__(self, url=None):
        super().__init__(url)
        self._url = url
        self._companyArticles = []
        self._browser = webdriver.Chrome()

    def _generateSoup(self):
        page = requests.get(self._url)
        self._soup = bs(page.text, 'html.parser')

    def _getArticles(self):
        return self._soup.find_all("article", {"class": "tm-articles-list__item"})

    def _addAritcle(self, article):
        self._companyArticles.append(article)

    def _getInfoAboutArticle(self, browser, article, articleID):
        title = article.find("a", {"class": "tm-article-snippet__title-link"}).find("span").text
        date = article.find("time")["title"]
        browser.get("https://habr.com/ru/company/ruvds/blog/page1/")
        rating = int(browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[2]/div[1]/span[1]").text)
        try:
            description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[5]/div[1]/div[1]/div[1]").text
        except NoSuchElementException:
            try:
                description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[4]/div[1]/div[1]/div[1]").text
            except NoSuchElementException:
                description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleID}]/div[1]/div[4]/div[2]/div[1]/div[1]/p[1]").text
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
        self._generateSoup()
        self._browser.get(self._url)
        self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, "tm-pagination__page")][-1])
        log.info(f"Last page number: <{self._lastPage}>")
        for page in range(1, self._lastPage + 1):
            log.debug(f"Jump to page number <{page}>")
            try:
                for articleID, article in enumerate(self._getCompanies(), start=1):
                    self._addAritcle(self._getInfoAboutArticle(self._browser, article, articleID))
                    self._browser.get(self._url)
                self._browser.find_element(By.XPATH, "//a[@id='pagination-next-page']").click()
                self._url = self._generateNextPageUrl(page)
                time.sleep(2)
            except Exception as e:
                print(e)
                if page > self._lastPage:
                    log.error(f"Page number <{page}> does not exist!")
                self._browser.close()
                break

    @property
    def companyArticles(self):
        return self._companyArticles


if __name__ == "__main__":
    parser = ArtricleParser("https://habr.com/ru/company/ruvds/blog/page1/")
    parser.start()

# articles = soup.find_all("article", {"class": "tm-articles-list__item"})
# for articleSerialNumber, article in enumerate(articles, start=1):
#     title = article.find("a", {"class": "tm-article-snippet__title-link"}).find("span").text
#     date = article.find("time")["title"]
#     browser.get("https://habr.com/ru/company/ruvds/blog/page1/")
#     rating = int(browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleSerialNumber}]/div[2]/div[1]/span[1]").text)
#     try:
#         description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleSerialNumber}]/div[1]/div[5]/div[1]/div[1]/div[1]").text
#     except NoSuchElementException:
#         try:
#             description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleSerialNumber}]/div[1]/div[4]/div[1]/div[1]/div[1]").text
#         except NoSuchElementException:
#             description = browser.find_element(By.XPATH, f"/html[1]/body[1]/div[1]/div[1]/div[2]/main[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/article[{articleSerialNumber}]/div[1]/div[4]/div[2]/div[1]/div[1]/p[1]").text
#     companyArticles.append(
#         {
#             "title": title,
#             "description": description,
#             "data": date,
#             "rating": rating
#         }
#     )



