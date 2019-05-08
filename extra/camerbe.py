from bs4 import BeautifulSoup, element
import requests
from requests.exceptions import ConnectionError
import re
import pickle
from unidecode import unidecode
from lib.text_summarizer import TextSummarizer


def scrape(batch):
    website_url = "https://www.camer.be"

    """
        1 = Economy
        2 = Humour
        3 = People
        4 = Politics
        5 = Health
        6 = Society
        7 = Culture
    """
    categories = {}
    categories[1] = website_url+"/1/12/1/cameroun-cameroon.html"
    categories[2] = website_url+"/1/15/1/cameroun-cameroon.html"
    categories[3] = website_url+"/1/5/1/cameroun-cameroon.html"
    categories[4] = website_url+"/1/6/1/cameroun-cameroon.html"
    categories[5] = website_url+"/1/13/1/cameroun-cameroon.html"
    categories[6] = website_url+"/1/11/1/cameroun-cameroon.html"
    categories[7] = website_url+"/1/14/21/cameroun-cameroon.html"

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
                page = requests.get(val)
                break
            except ConnectionError:
                print("Max retries exceed. Retrying again")

        soup = BeautifulSoup(page.content, "html.parser")
        article_section = soup.find(class_=re.compile("col-md-8 col-sm-8 col-lg-8 col-xm-8"))

        for sections in article_section:

            if isinstance(sections, element.Tag):
                articles = sections.find_all(class_=re.compile("col-md-6 d-flex flex-wrap"))
                links = []

                for article in articles:
                    print("Getting articles links")
                    links.append(article.find("h5").find("a")["href"])
                for link in links:
                    if link in scraped_links:
                        print("Already scraped. Skipped...")
                        continue
                    while True:
                        try:
                            print("Scraping article "+link)
                            article_page = requests.get(link)
                            article_soup = BeautifulSoup(article_page.content, "html.parser")
                            f_article = article_soup.find("article")
                            image = f_article.find("img")["data-src"]
                            title = article_soup.find("h1").get_text().replace(",", "")
                            f_description = f_article.find(
                                class_=re.compile("text-justify info")
                            )
                            clean_title = unidecode(title).replace(" ", "-")
                            image_html = "<p><img src='"+image+"' alt='"+clean_title+"'></p>\n"
                            description = image_html+"\n"+f_description.get_text()

                            # data = title+" "+description.replace("\n", "")+","+str(key)
                            data.append(
                                [
                                    "camer.be",
                                    title,
                                    link,
                                    description,
                                    key,
                                    link,
                                    "camer.be"
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
