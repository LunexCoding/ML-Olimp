import json
from pathlib import Path


CONFIG_PATH = Path("selectors.json")


class _SelectorsConfig:
    def __init__(self):
        self.__config = self.__loadConfig()

    def __loadConfig(self):
        with CONFIG_PATH.open(encoding="utf-8") as config:
            data = json.load(config)
        return data

    @property
    def page(self):
        return self.__config["page"]

    @property
    def companiesPage(self):
        return self.__config["companiesPage"]

    @property
    def company(self):
        return self.__config["company"]

    @property
    def blog(self):
        return self.__config["blog"]

    @property
    def article(self):
        return self.__config["article"]

    def getXpathByParameters(self, section, name, ID):
        if section == "article" and name == "description":
            xpaths = []
            for xpath in self.__config[section][name]:
                xpaths.append(xpath.replace("articleID", str(ID)))
            return xpaths
        if "companyID" in self.__config[section][name]:
            return self.__config[section][name].replace("companyID", str(ID))
        return self.__config[section][name].replace("articleID", str(ID))


selectorsConfig = _SelectorsConfig()
