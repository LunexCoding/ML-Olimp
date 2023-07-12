from parsers.ultraParser import Parser


if __name__ == "__main__":
    parser = Parser("https://habr.com/ru/companies/page1/")
    try:
        parser.start()
    except KeyboardInterrupt:
        parser._writeFileSummaryOfCompanies()