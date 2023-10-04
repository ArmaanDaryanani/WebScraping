from GetData import GetData
from SalesMetrics import SalesMetrics
from SpreadsheetCreator import SpreadsheetCreator

class ScraperDriver:
    def __init__(self):
        self.get_data = GetData()
        self.spreadsheet_creator = SpreadsheetCreator("NewDataSheet.xlsx")
        self.sales_metrics = SalesMetrics("https://www.ebay.com/sh/research?marketplace=EBAY-US&tabName=SOLD", "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&ru=https%3A%2F%2Fwww.ebay.com%2Fsh%2Fresearch%3Fmarketplace%3DEBAY-US%26tabName%3DSOLD")
        #self.run1()
        self.run2()


    def run1(self):
        searchterm = "ps2 games"
        categoryName = "Game Name"
        enableLots = False
        pageNumber = 1

        attrs = self.get_data.getAllAttributes(searchterm, categoryName, enableLots, pageNumber)

        init_data = ["Game Name", "Price", "Shipping Price", "Url"]
        data = []
        sheetname = "PS2 Platform"
        self.spreadsheet_creator.deleteSheet(sheetname)
        self.spreadsheet_creator.createNewSheet(sheetname, init_data)
        self.spreadsheet_creator.nextRow()

        for i in attrs:
            if i == "ffx0":
                self.spreadsheet_creator.appendDataToSheet(sheetname, data)
                self.spreadsheet_creator.nextRow()
                data = []
                continue
            data.append(i)

        self.spreadsheet_creator.autosizeColumns(sheetname)
        print("Finished")

    def run2(self):
        pass




ScraperDriver()