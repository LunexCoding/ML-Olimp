from decouple import config


class _SettingsConfig:
    def __init__(self):
        self.__settingsConfig = self.__loadSettings()

    def __loadSettings(self):
        __settings = {}
        __settings["SMTP"] = dict(
            host=config("SMTP_HOST"),
            port=config("SMTP_PORT", cast=int),
            email=config("SMTP_EMAIL"),
            password=config("SMTP_PASSWORD")
        )
        return __settings

    @property
    def SMTPSettings(self):
        return self.__settingsConfig["SMTP"]


settingsConfig = _SettingsConfig()
