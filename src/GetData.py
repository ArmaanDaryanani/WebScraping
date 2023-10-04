import requests
import pyshorteners
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class GetData:
    def __init__(self):
        self.session = requests.Session()

    #Returns main URL from the desired searchTerm (ex: 'ps3 video games')
    def getEbayUrl(self, searchTerm, pageNumber, ifSold=False, ifCompleted=False, ifLowToHigh=False, ifHighToLow=False):
        soldNum = 0  # 0 for unsold
        completedNum = 0  # 0 for not completed
        ascendVal = 0
        if ifLowToHigh:
            ascendVal = 15
        elif ifHighToLow:
            ascendVal = 16
        if ifSold:
            soldNum = 1
        if ifCompleted:
            completedNum = 1
        return f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={searchTerm}&_sacat=0&_ipg=240&rt=nc&LH_Sold={soldNum}&LH_Complete={completedNum}&_pgn={pageNumber}&_sop={ascendVal}'

    #From searchTerm, returns every link to a product on a single page
    def getPageListingUrls(self, searchTerm, pageNumber, ifSold=False, ifCompleted=False, ifLowToHigh=False, ifHighToLow=False):
        url = self.getEbayUrl(searchTerm, pageNumber, ifSold, ifCompleted, ifLowToHigh, ifHighToLow)

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        links = []
        #html for link
        for i in soup.select('a.s-item__link[href]'):
            links.append(i['href'])

        #removes top link(garbage link)
        links.pop(0)
        return links

    #For concurrent requests
    def fetchPage(self, link):
        with requests.Session() as session:
            return session.get(link).content

    #Returns all the names from a searchTerm and category (under item specifics, "Game Name" for example)
    def getItemNames(self, content, categoryName, enableLots, link):
        soup = BeautifulSoup(content, 'html.parser')

        #checks for lots listing
        if(enableLots == False and soup.find('span', class_='x-msku__select-box-wrapper')):
            return ""

        else:
            # Hunts text for given category name, ex: "Game Name" -> "Legend of Zelda"
            name_label = soup.find('span', class_='ux-textspans', string=str(categoryName))
            if name_label:
                # For every category name is a common parent. Each parent has 2 children: Category Name and the actual text associated with it
                parent_div = name_label.find_parent('div', class_='ux-layout-section-evo__col')
                if parent_div:
                    # Once parent is found, look for child with values__values label as it contains the actual text
                    name_element = parent_div.find('div', class_='ux-labels-values__values') \
                        .find('span', class_='ux-textspans')

                    if name_element:
                        if name_element.text == "Does not apply":
                            return self.nameFromTitle(link)
                        return name_element.text

                    else:
                        print('Game name element not found within parent div', f'Url:{link}')
                else:
                    print("'ux-layout-section-evo__col' parent div not found", f'Url:{link}')
            else:
                return self.nameFromTitle(link)

    #returns item prices given the html content
    def getItemPrice(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        intermediary_text = soup.find('div', class_="x-price-primary")
        price = intermediary_text.find('span', class_="ux-textspans").text
        if "US" not in price:
            pass
        return price[3:]

    #returns shipping cost for a given item
    def getItemShipping(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        intermediary_text = soup.find('div', class_="vim d-shipping-minview")
        try:
            shipping_price = intermediary_text.find('span', class_="ux-textspans ux-textspans--BOLD").text
            if "Free" in shipping_price:
                return "Free"
            if "," in shipping_price:
                return "Free"
            if "US" not in shipping_price:
                pass
            return shipping_price[3:]
        except AttributeError:
            return "No Shipping Price Found"


    #Returns all attributes of the given listing
    def getAllAttributes(self, searchTerm, categoryName, enableLots, pageNumber, number_of_listings=0, ifSold=False, ifCompleted=False, ifLowToHigh=False, ifHighToLow=False):
        links = self.getPageListingUrls(searchTerm, pageNumber, ifSold, ifCompleted, ifLowToHigh, ifHighToLow)

        all_attr = []

        # Fetch pages concurrently with threads
        with ThreadPoolExecutor() as executor:
            pages = list(executor.map(self.fetchPage, links))

        if number_of_listings == 0:
            for link, content in zip(links, pages):
                name = self.getItemNames(content, categoryName, enableLots, link)
                price = self.getItemPrice(content)
                shipping = self.getItemShipping(content)
                url = link

                # if lots are found (since name returns empty string if so)
                if len(name) == 0:
                    continue

                all_attr.append(name)
                all_attr.append(price)
                all_attr.append(shipping)
                all_attr.append(self.shortenUrl(url))
                all_attr.append("ffx0")

        else:
            for link, content in zip(links, pages):
                for i in range(number_of_listings):
                    name = self.getItemNames(content, categoryName, enableLots, link)
                    price = self.getItemPrice(content)
                    shipping = self.getItemShipping(content)
                    url = link

                    # if lots are found (since name returns empty string if so)
                    if len(name) == 0:
                        continue

                    all_attr.append(name)
                    all_attr.append(price)
                    all_attr.append(shipping)
                    all_attr.append(self.shortenUrl(url))
                    all_attr.append("ffx0")
        return all_attr

    #When unable to fetch item name from category description, return url
    def nameFromTitle(self, listing_url):
        soup = BeautifulSoup(self.fetchPage(listing_url), 'html.parser')
        game_title = soup.find('span', class_="ux-textspans ux-textspans--BOLD").text
        return game_title

    #shortens urls
    def shortenUrl(self, url):
        s = pyshorteners.Shortener()
        return s.tinyurl.short(url)



