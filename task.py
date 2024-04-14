import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from concurrent.futures import ThreadPoolExecutor


class BookScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        self.book_info_list = []

    def get_url(self, count):
        url = f"https://books.toscrape.com/catalogue/page-{count}.html"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
        for link in data:
            book_url = "https://books.toscrape.com/catalogue/" + link.find("a").get("href")
            yield book_url

    def scrape_book_info(self, book_url):
        try:
            book_info = {}
            response = requests.get(book_url, headers=self.headers)
            sleep(1)
            soup = BeautifulSoup(response.text, "html.parser")
            data = soup.find("div", class_="content")
            book_name = data.find("h1").text
            price = float(soup.find("p", class_="price_color").text[2:])
            description = soup.find("meta", attrs={"name": "description"})["content"].strip()
            stock = int(soup.find("p", class_="instock availability").text.split()[2][1:])
            book_url_img = "https://books.toscrape.com/" + data.find("img").get("src").replace("../", "")
            book_info = {"book_name": book_name, "price": price, "description": description, "stock": stock,
                         "book_url": book_url}
            self.book_info_list.append(book_info)
            print(book_info)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def scrape_books(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for count in range(1, 51):
                urls = self.get_url(count)
                executor.map(self.scrape_book_info, urls)

        with open('book_info.json', 'w') as f:
            json.dump(self.book_info_list, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    scraper = BookScraper()
    scraper.scrape_books()
