from GetData import GetData

class ScraperDriver:
    def __init__(self):
        self.urls = GetData()
        self.run()
        #self.test()

    def run(self):
        searchterm = "ps2 games"
        categoryName = "Game Name"
        enableLots = False
        pageNumber = 1

        attrs = self.urls.getAllAttributes(searchterm, categoryName, enableLots, pageNumber)

        print(attrs)

    def test(self):
        return 0

ScraperDriver()