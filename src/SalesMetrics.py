import requests
from bs4 import BeautifulSoup
from GetData import GetData

class SalesMetrics:
    def __init__(self):
        self.get_data = GetData()

    #gets average price from the 5 first listings (listingNumber) on the page. Ensures the listings are the correct name
    #if low to high == false, auto high to low search
    def getAveragePrice(self, item_name, if_sold_and_completed, if_low_to_high, platform_name="", if_sealed = False):
        num_listings = 5

        search_term = item_name + platform_name
        if if_sealed:
            search_term += "sealed"

        if if_low_to_high:
            url = self.get_data.getEbayUrl(search_term, 1, if_sold_and_completed, True, False)
        else:
            url = self.get_data.getEbayUrl(search_term, 1, if_sold_and_completed, False, True)

        soup = BeautifulSoup(self.get_data.fetchPage(url), 'html.parser')

        titles = []
        prices = []
        shippings = []

        for i in range(1, num_listings):
            listing = soup.find("li", {"data-view":f'mi:1686|iid:{i}'}) #1686 might change

            #EXTRACT TITLE
            title_tag = listing.find("div", class_="s-item__title")
            if title_tag:
                titles.append(title_tag.get_text().strip())
            else:
                titles.append(None)
                print("Title tag not found")

            # EXTRACT PRICE
            price_tag = listing.find("span", class_="s-item__price")
            if price_tag:
                prices.append(price_tag.get_text().strip())
            else:
                prices.append(None)

            # EXTRACT SHIPPING PRICE
            shipping_tag = listing.find("span", class_="s-item__shipping")
            if shipping_tag:
                shippings.append(shipping_tag.get_text().strip())
            else:
                shippings.append(None)







#item_name, category name and searches through top 5 listings with the same name and averages the price