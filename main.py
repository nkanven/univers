"""Main boot."""
from modules.youtube_downloader import get_channel_videos
from modules.journalducameroun_com import get_elements
from modules.model import models
from lib import post, config
from lib.fdparser import parse
import argparse
import pickle
import time

# print(parse.wordpress("https://www.journalducameroun.com/feed/"))
# print(get_elements("https://www.journalducameroun.com/fr/cameroun-la-banque-mondiale-menace-de-suspendre-ses-financements-cameroun/"))
parser = argparse.ArgumentParser(
    description="Scrap parameters for Univers scraper")

parser.add_argument(
    "--batch",
    dest="batch",
    type=int,
    default=10,
    help="Max page to scrap")

parser.add_argument(
    "--action",
    dest="action",
    type=str,
    default="scrape",
    help="Define action the program should launch. --action=scrape or --action=post")

parser.add_argument(
    "--env",
    dest="env",
    type=str,
    default="dev",
    help="Define the environment for the execution")

args = parser.parse_args()

# https://www.youtube.com/watch?v=1iLsJUXOHmo&list=PLeC6RbnPN_tuQOdAYexo9qlIjgtOGOYZx

# print(get_info('https://www.youtube.com/watch?v=uSosZCcLr_U'))

Model = models()

if args.action == "scrape":
    while True:
        try:
            with open("scraped_links.pkl", "rb") as pkcl:
                scraped_links = pickle.load(pkcl)
        except Exception:
            scraped_links = []

        others = parse.parse_others(args.batch)
        if others:
            for other in others:
                Model.insert_item(other, other[-2])
                scraped_links.append(other[5])
                with open("scraped_links.pkl", "wb") as pkl:
                    pickle.dump(scraped_links, pkl)
        print("Done with others")

        """
        links = Model.get_links()
        for link in links:
            if link[2] == "wordpress":
                for witem in parse.wordpress(link[1]):
                    witem.append(link[3])
                    Model.insert_item(witem, witem[-1])
            print("Done with wordpress")

            if link[2] == "youtube":
                for yitem in parse.youtube(link[1]):
                    yitem.append(link[3])
                    Model.insert_item(yitem, 'youtube')
            print("Done with youtube")"""

if args.action == "post":
    if args.env == "dev":
        post_params = {
            "url": config.dev_post_url,
            "token": config.dev_post_key
        }
    else:
        post_params = {
            "url": config.prod_post_url,
            "token": config.prod_post_key
        }
    items = Model.get_items()
    for item in items:
        # Check if item is ready for post
        if item[10] == 1:
            # Check if item have not been posted and post it
            if item[11] == 1 and item[12] == 0:
                item_dic = {
                    "title": item[2],
                    "description": item[-1],
                    "tags": item[9]+",1394",
                    "slug": item[2]
                }
                print(item_dic)
                response = post.wordpress_create_post(item_dic, post_params)
                print(response)
                if response:
                    Model.update_item(item[0])
                    print("sleeping for 1min")
                    time.sleep(60)
