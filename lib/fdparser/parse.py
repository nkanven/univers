"""Wordpress rss feed parser method."""
import feedparser
from extra import camerbe
from modules import actucameroun_com, news_abidjan_net
import re

def wordpress(link):
    """Parse wordpress rss feed
    
    Arguments:
        link {str} -- Wordpress rss feed link
    """
    wordpress_data = []
    news_feed = feedparser.parse(link)
    source = link.split("/")[2] if "" in link.split("/") else link.split("/")[0]
    entries = news_feed.entries

    if entries:
        for entry in entries:
            wordpress_data.append(
                [
                    entry.author,
                    entry.title,
                    entry.id,
                    entry.summary,
                    0,
                    entry.link,
                    source
                ]
            )

    return wordpress_data


def youtube(link):
    """Get necessary element from youtube rss feed

    Arguments:
        link {str} -- Youtube channel rss feed link
    """
    youtube_data = []
    news_feed = feedparser.parse(link)
    entries = news_feed.entries

    if entries:
        for entry in entries:
            clen_title = re.sub('[^a-zA-Z0-9À-ÿ- \n\.]', ' ', entry.title)
            image_url = entry.media_thumbnail[0]["url"]
            image_html = "<img width='1' height='1' src='"+image_url+"' alt='""'>"
            youtube_data.append(
                [
                    entry.author,
                    entry.title,
                    entry.yt_videoid,
                    entry.summary+"<br>"+image_html,
                    2,
                    entry.link
                ]
            )

    return youtube_data


def parse_others(batch, scrape_links):
    bulky = [
        news_abidjan_net.scrape(batch, scrape_links),
        actucameroun_com.scrape(batch, scrape_links),
        camerbe.scrape(batch, scrape_links)
    ]
    bulky_data = list()

    for scraped_data in bulky:
        if scraped_data:
            if scraped_data:
                bulky_data.extend(scraped_data)
    
    return bulky_data
