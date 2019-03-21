"""Journal du cameroun website parser method."""
from bs4 import BeautifulSoup
import requests


def get_elements(link):
    """Get elements from journalducameroun.com.

    Arguments:
        link {str} -- link to be scraped
    """
    while True:
        try:
            page = requests.get(link)

            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                title = soup.find("h1").get_text()
                description = soup.find(
                    "div", class_="post-content").get_text()
                article = soup.find("article", class_="post-full").children
                img = list(article)[5].find("img")["src"]
                cat = soup.find("p", class_="page-title-category")
                category = cat.get_text().replace("\n", "").replace("\t", "")

                return title, description, img, category
        except ConnectionError:
            print("Connection error. Retry")
