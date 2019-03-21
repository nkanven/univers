"""Wordpress rss feed parser method."""
import feedparser


def parse(link):
    news_feed = feedparser.parse(link)

    entries = news_feed.entries[1]

    print(entries.title, entries.id, entries.summary, entries.category)

    return entries.title
