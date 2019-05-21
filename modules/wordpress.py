from bs4 import BeautifulSoup
from modules.model import models
import requests

def parse():
    Model = models()
    links = Model.get_news_links()

    for link in links:
        page = requests.get(link[1])
        soup = BeautifulSoup(page.content, "html.parser")
        title = mw_parser_output = soup.find("title").get_text()
        print(title)
        input()