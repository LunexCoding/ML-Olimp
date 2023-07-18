import json
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from log import logger
from const import ELEMENT_NOT_FOUND
from selectorsConfig import selectorsConfig


log = logger.getLogger(__name__)


class Parser:
    def __init__(self, url=None, browser=None):
        self._url = url
        self._lastPage = None
        if browser is not None:
            self._browser = browser
        else:
            options = Options()
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            self._browser = webdriver.Chrome(options=options)
            self._browser.maximize_window()

    def fingPagination(self):
        try:
            self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, selectorsConfig.page["pagination"])][-1])
        except NoSuchElementException:
            self._lastPage = 1

    def generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Получена ссылка на следующую страницу page <{'/'.join(url)}>")
            return "/".join(url)

    def checkNextPage(self, page):
        if page == self._lastPage:
            self._browser.quit()
        else:
            self._url = self.generateNextPageUrl(page)
            try:
                self._browser.get(self._url)
            except TimeoutException:
                self._browser.refresh()

    def refresh(self):
        self._browser.refresh()

    def __checkSelectorIsIterator(self, selector):
        if isinstance(selector, list):
            return True
        return False

    def findElement(self, locator, selector, parent=None):
        return self.__findElement(locator, selector, parent, all=False)

    def findElements(self, locator, selector, parent=None):
        return self.__findElement(locator, selector, parent, all=True)

    def __findElement(self, locator, selector, parent=None, all=False):
        if self.__checkSelectorIsIterator(selector):
            return self.__findElementByIterSelector(locator, selector, parent)
        else:
            element = parent if parent is not None else self._browser
            try:
                if all:
                    return element.find_elements(locator, selector)
                return element.find_element(locator, selector)
            except NoSuchElementException:
                return False

    def __findElementByIterSelector(self, locator, selector, parent=None):
        element = parent if parent is not None else self._browser
        for xpath in selector:
            try:
                needSelector = element.find_element(locator, xpath)
                if needSelector:
                    return needSelector
            except NoSuchElementException:
                pass
        return ELEMENT_NOT_FOUND

    @staticmethod
    def saveData(path, data):
        with path.open('w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        log.debug("Данные успешно записаны")


if __name__ == "__main__":
    parser = Parser()
    time.sleep(5)