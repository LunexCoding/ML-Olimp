import time

from helpers.fileSystem import FileSystem
from parsers.parserCompany import CompanyParser
from consts import PATHS_TO_CREATE_DIRECTORIES
from log import logger


log = logger.getLogger(__name__)


if __name__ == "__main__":
    startTime = time.time()
    for path in PATHS_TO_CREATE_DIRECTORIES:
        FileSystem.makeDir(path, recreate=True)

    parser = CompanyParser("https://habr.com/ru/companies/page16/")
    parser.start(articles=True, save=True)
    log.debug(f"Затраченное время: <{round((time.time() - startTime) / 60, 2)} минут>")
