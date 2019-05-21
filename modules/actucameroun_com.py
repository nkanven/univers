from bs4 import BeautifulSoup, element
import requests
from requests.exceptions import ConnectionError
import re
import pickle
from unidecode import unidecode
import traceback


def scrape(batch, scrape_links):
    website_url = "https://actucameroun.com"

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
    categories[1] = website_url+"/category/economie/"
    categories[4] = website_url+"/category/politique/"
    categories[5] = website_url+"/category/sante/"
    categories[6] = website_url+"/category/societe/"
    categories[8] = website_url+"/category/sport/"

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
        _section = soup.find(class_="td-ss-main-content")
        section_articles = _section.find_all(class_="td-block-span6")

        for section_article in section_articles:
            for thumbnail in section_article.find_all(class_="td-module-thumb"):
                article_url = thumbnail.find("a")["href"]
                if article_url in scraped_links:
                    print("Already scraped. Skipped...")
                    continue
                while True:
                    try:
                        print("Scraping article "+article_url)
                        page = requests.get(article_url)
                        article = BeautifulSoup(page.content, "html.parser")

                        title = article.find(class_="td-post-title")\
                            .find("h1").get_text()
                        image = article.find(class_="td-post-featured-image").find("img")["src"]
                        """clean_title_slug = re.sub(
                                '[^a-zA-Z0-9À-ÿ- \n\.]',
                                ' ',
                                unidecode(title)
                            ).replace(" ", "-")
                        image_html = "<p><img src='"+image+"' alt='"\
                            + clean_title_slug + "'></p>\n"
                        """
                        f_description = article.find(
                            class_="td-post-content"
                        ).get_text()
                        # description = image_html+f_description
                        remove_taboola = re.compile("window._taboola(.*\n)*")
                        description = remove_taboola.sub("", f_description)

                        data.append(
                            [
                                "actucameroun.com",
                                title,
                                article_url,
                                description,
                                key,
                                article_url,
                                image,
                                "cameroun",
                                "actucameroun.com"
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