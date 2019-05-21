from bs4 import BeautifulSoup, element
import requests
from requests.exceptions import ConnectionError
import re
import pickle
from unidecode import unidecode
from lib.text_summarizer import TextSummarizer


def scrape(batch):
    website_url = "https://news.abidjan.net/"

    """
        1 = Economy
        2 = Humour
        3 = People
        4 = Politics
        5 = Health
        6 = Society
        7 = Culture
        8 = Sport
    """
    categories = {}
    categories[1] = website_url+"rubriques/economie.asp"
    categories[4] = website_url+"rubriques/politique.asp"
    categories[6] = website_url+"rubriques/societe.asp"
    categories[6] = website_url+"rubriques/faitsdivers.asp"
    categories[6] = website_url+"rubriques/region.asp"
    categories[7] = website_url+"rubriques/artculture.asp"
    categories[8] = website_url+"rubriques/sport.asp"

    try:
        with open("scraped_links.pkl", "rb") as pkcl:
            scraped_links = pickle.load(pkcl)
    except Exception:
        scraped_links = []
    print(scraped_links)
    data = list()
    i = 1

    for key, val in categories.items():
        while True:
            try:
                print("Scraping {}".format(val))
                page = requests.get(val)
                break
            except ConnectionError:
                print("Max retries exceed. Retrying again")

        soup = BeautifulSoup(page.content, "html.parser")
        news_links_section = soup.find_all(class_="LiNewsPol")
        # print(news_links_section)

        links = []

        print("Getting articles links")
        for news_link in news_links_section:
            print(news_link.find("a")["href"])
            links.append(news_link.find("a")["href"])
            
        for link in links:
            if link in scraped_links:
                print("Already scraped. Skipped...")
                continue
            while True:
                try:
                    print("Scraping article "+link)
                    article_page = requests.get(link)
                    article_soup = BeautifulSoup(article_page.content, "html.parser")
                    try:
                        og_img = article_soup.find("meta", property="og:image")
                        image = og_img["content"]
                    except TypeError:
                        break
                    title = article_soup.find("h1").get_text()
                    description = article_soup.find(class_="FullArticleTexte").get_text()
                    
                    data.append(
                        [
                            "news.abidjan.net",
                            title,
                            link,
                            description,
                            key,
                            link,
                            image,
                            "côte d'ivoire",
                            "news.abidjan.net"
                        ]
                    )

                    if i == batch:
                        return data
                    i += 1
                    break
                except ConnectionError:
                    print("Max retries exceed. Retrying again")
                except AttributeError as e:
                    print(e)
    return data
