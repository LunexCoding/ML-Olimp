from pathlib import Path


from consts import DATA_DIRECTORY


ELEMENT_NOT_FOUND = None

INVALID_COMPANY_INFO = None
COMPANY_NAME_NOT_FOUND = "Название компании не удалось получить"
COMPANY_DESCRIPTION_NOT_FOUND = "Описание компании не удалось получить"
COMPANY_PROFILE_NOT_FOUND = "Профиль компании не удалось получить"
COMPANY_RATING_NOT_FOUND = "Рейтинг компании не удалось получить"
COMPANY_SUBSCRIBERS_NOT_FOUND = "Количество подписчиков компании не удалось получить"
COMPANY_HUBS_NOT_FOUND = "Хабы компании не удалось получить"
COMPANY_ABOUT_NOT_FOUND = "Описание компании не удалось получить"

ARTICLE_TITLE_NOT_FOUND = "Название статьи не удалось получить"
ARTICLE_DESCRIPTION_NOT_FOUND = "Текст статьи не удалось получить"
ARTICLE_PUBLICATION_DATE_NOT_FOUND = "Дата публикации статьи удалось получить"
ARTICLE_RATING_NOT_FOUND = "Рейтинг статьи не удалось получить"

EMAIL = "hxtk1@mail.ru"
EMAIL_SUBJECT = "ML-Olimp Parsing System"
EMAIL_MESSAGE = "ML-Olimp Parsing System завершила свою работу"
EMAIL_FILES = [
    Path(DATA_DIRECTORY.parent) / "data.zip",
    Path(DATA_DIRECTORY) / "log.md"
]
