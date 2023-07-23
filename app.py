import time

from log import logger
from consts import PATHS_TO_CREATE_DIRECTORIES, DATA_DIRECTORY
from parsers.consts import EMAIL, EMAIL_SUBJECT, EMAIL_MESSAGE, EMAIL_FILES
from parsers.parserCompany import CompanyParser
from helpers.fileSystem import FileSystem
from helpers.emailSender import emailSender


log = logger.getLogger(__name__)


if __name__ == "__main__":
    startTime = time.time()
    for path in PATHS_TO_CREATE_DIRECTORIES:
        FileSystem.makeDir(path, recreate=True)

    parser = CompanyParser("https://habr.com/ru/companies/page1/")
    parser.start(articles=True, save=True)
    log.debug(f"Затраченное время: <{round((time.time() - startTime) / 60, 2)} минут>")

    FileSystem.createArchive("data", DATA_DIRECTORY, f"{DATA_DIRECTORY}.zip")
    emailSender.sendEmail(
        email=EMAIL,
        subject=EMAIL_SUBJECT,
        message=EMAIL_MESSAGE,
        files=EMAIL_FILES
    )