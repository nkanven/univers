"""Main boot."""
from modules.youtube_downloader import get_channel_videos
from modules.journalducameroun_com import get_elements
from modules.feedparser import wordpress
import argparse


print(wordpress.parse("https://www.journalducameroun.com/feed/"))
print(get_elements("https://www.journalducameroun.com/fr/cameroun-la-banque-mondiale-menace-de-suspendre-ses-financements-cameroun/"))
parser = argparse.ArgumentParser(
    description="Scrap parameters for Univers scraper")
parser.add_argument(
    "--frequence",
    dest="freq",
    type=int,
    default=100,
    help="Set the scrap frequency. Number of loop")

# https://www.youtube.com/watch?v=1iLsJUXOHmo&list=PLeC6RbnPN_tuQOdAYexo9qlIjgtOGOYZx

# print(get_info('https://www.youtube.com/watch?v=uSosZCcLr_U'))

yt = [links for links in open("res/youtube_channels.txt", "r")]

if yt:
    for link in yt:
        get_channel_videos(link)
print(yt)
# print(get_channel_videos())
