import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class GetData:
    def __init__(self):
        self.session = requests.Session()

    #Returns main URL from the desired searchTerm (ex: 'ps3 video games')
    def getEbayUrl(self, searchTerm, pageNumber):
        return f'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2510209.m570.l1313&_nkw={searchTerm}&_sacat=0&_ipg=240&_pgn={pageNumber}'

    #From searchTerm, returns every link to a product on a single page
    def getPageListingUrls(self, searchTerm, pageNumber):
        url = self.getEbayUrl(searchTerm, pageNumber)

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
                        # If found, print in terminal and append to return array (optional printout)
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
        itermediary_text = soup.find('div', class_="x-price-primary")
        price = itermediary_text.find('span', class_="ux-textspans").text
        return price[3:]

    def getAverageSoldPrice(self, ):


    def getAverageSellingPrice(self, ):


    #Returns all attributes of the given listing
    def getAllAttributes(self, searchTerm, categoryName, enableLots, pageNumber):
        links = self.getPageListingUrls(searchTerm, pageNumber)

        # Fetch pages concurrently
        with ThreadPoolExecutor() as executor:
            pages = list(executor.map(self.fetchPage, links))

        for link, content in zip(links, pages):
            name = self.getItemNames(content, categoryName, enableLots, link)
            price = self.getItemPrice(content)
            url = link

            #if lots are found (since name returns empty string if so)
            if len(name) == 0:
                continue

            print(name, price)


    #When unable to fetch item name from category description, return url
    def nameFromTitle(self, listing_url):
        soup = BeautifulSoup(self.fetchPage(listing_url), 'html.parser')
        game_title = soup.find('span', class_="ux-textspans ux-textspans--BOLD").text
        return game_title






