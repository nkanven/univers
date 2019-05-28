from bs4 import BeautifulSoup, element
import requests
from requests.exceptions import ConnectionError
import re
import pickle
from unidecode import unidecode
import traceback


def scrape(batch, scrape_links):
    website_url = "http://seneweb.com"

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
    categories[4] = website_url+"/news/politique/"
    categories[6] = website_url+"/news/societe/"
    categories[6] = website_url+"/news/faits-divers/"
    categories[8] = website_url+"/news/sport/"

    try:
        with open(scrape_links, "rb") as pkcl:
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
                print("Max retries exceed for {}. Retrying again".format(val))
        
        soup = BeautifulSoup(page.content, "html.parser")
        _section = soup.find("ul", class_="module_news_list")
        section_articles = _section.find_all(class_="module_news_item_content")

        for section_article in section_articles:
            article_url = website_url+section_article.find("a")["href"]

            if article_url in scraped_links:
                print("Already scraped. Skipped...")
                continue
            while True:
                try:
                    print("Scraping article "+article_url)
                    page = requests.get(article_url)
                    article = BeautifulSoup(page.content, "html.parser")

                    title = article.find("h1").get_text()
                    try:
                        og_img = article.find("meta", property="og:image")
                        image = og_img["content"]
                    except TypeError:
                        break

                    f_description = article.find(
                        class_="single_post_content_wrapper"
                    )
                    paragraphs = f_description.find_all("p")

                    if not paragraphs:
                        print("Not article")
                        break

                    f_description = f_description.get_text()

                    # description = image_html+f_description
                    remove_taboola = re.compile("window._taboola(.*\n)*")
                    description = remove_taboola.sub("", f_description)
                    analytics_pattern = re.compile("\(.+}\);")
                    description = analytics_pattern.sub("", description)

                    data.append(
                        [
                            "seneweb.com",
                            title,
                            article_url,
                            description,
                            key,
                            article_url,
                            image,
                            "senegal",
                            "seneweb.com"
                        ]
                    )

                    if i == batch:
                        return data
                    i += 1
                    break
                except ConnectionError:
                    print(
                        "Max retries exceed for {}. Retrying again".format(
                            article_url
                        )
                    )
                except AttributeError:
                    scraped_links.append(article_url)
                    with open(scrape_links, "wb") as pkl:
                        pickle.dump(scraped_links, pkl)
                    print(traceback.format_exc())