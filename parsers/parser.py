import json

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from log import logger
from parsers.consts import ELEMENT_NOT_FOUND
from selectorsConfig import selectorsConfig


log = logger.getLogger("parsers/parser.py")


class Parser:
    def __init__(self, url, browser=None):
        self._url = url
        self._lastPage = 1
        if browser is not None:
            self._browser = browser
        else:
            options = Options()
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_experimental_option(
                'prefs',
                {
                    'profile.managed_default_content_settings.javascript': 2,
                    'profile.managed_default_content_settings.images': 2,
                    'profile.managed_default_content_settings.mixed_script': 2,
                    'profile.managed_default_content_settings.media_stream': 2,
                    'profile.managed_default_content_settings.stylesheets': 2
                }
            )
            self._browser = webdriver.Chrome(options=options)
            self._browser.maximize_window()

    def openPage(self, url):
        self._browser.get(url)
        log.debug(f"Переход на страницу <{url}>")

    def fingPagination(self):
        try:
            self._lastPage = int([el.text for el in self._browser.find_elements(By.CLASS_NAME, selectorsConfig.page["pagination"])][-1])
        except:
            self._lastPage = 1

    def generateNextPageUrl(self, page):
        if page < self._lastPage:
            url = self._url.split('/')
            url[-2] = f"page{page + 1}"
            log.debug(f"Получена ссылка на следующую страницу page <{'/'.join(url)}>")
            return "/".join(url)

    def openNextPage(self, page):
        if page != self._lastPage:
            self._url = self.generateNextPageUrl(page)
            try:
                self.openPage(self._url)
            except TimeoutException:
                self._browser.refresh()

    def refresh(self):
        self._browser.refresh()

    def findElement(self, locator, selector, parent=None):
        return self.__findElement(locator, selector, parent, all=False)

    def findElements(self, locator, selector, parent=None):
        return self.__findElement(locator, selector, parent, all=True)

    def __checkSelectorIsIterator(self, selector):
        return isinstance(selector, list)

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
                return ELEMENT_NOT_FOUND

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

    @property
    def url(self):
        return self._url

    @property
    def browser(self):
        return self._browser
