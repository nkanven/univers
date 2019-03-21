"""Facebook user page scraper."""
from bs4 import BeautifulSoup
import requests


def get_content(link):
    """Parse Facebook user page and return key elements as a list.

    argnument:
        link (str): user page link
    return list [username, time, title, description, media]
    """
    try:
        fbk = requests.get(link)
        soup = BeautifulSoup(fbk.content, 'html.parser')
        soup.find("div")
    except ConnectionError as e:
        print(e)
