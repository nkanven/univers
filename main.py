"""Main boot."""
from modules.youtube_downloader import get_channel_videos
from modules.journalducameroun_com import get_elements
from modules.model import models
from lib import post, config
from lib.fdparser import parse
from unidecode import unidecode
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
        scrape_links = config.saved_scraped_path
        
        if args.env == "ml":
            scrape_links = config.ml_saved_scraped_path

        try:
            with open(scrape_links, "rb") as pkcl:
                scraped_links = pickle.load(pkcl)
        except Exception:
            scraped_links = []

        others = parse.parse_others(args.batch, scrape_links)
        if others:
            for other in others:
                print("Storing article {}".format(other[5]))
                Model.insert_item(other, other[-1], args.env)
                scraped_links.append(other[5])
                with open(scrape_links, "wb") as pkl:
                    pickle.dump(scraped_links, pkl)
        print("Done with others")

        """
        links = Model.get_links()
        for link in links:
            if link[2] == "wordpress":
                for witem in parse.wordpress(link[1]):
                    witem.append(link[3])
                    Model.insert_item(witem, witem[-1], args.env)
            print("Done with wordpress")

            if link[2] == "youtube":
                for yitem in parse.youtube(link[1]):
                    yitem.append(link[3])
                    Model.insert_item(yitem, 'youtube', args.env)
            print("Done with youtube")"""

if args.action == "post":
    if args.env == "dev":
        post_params = {
            "url": config.dev_url,
            "token": config.dev_key
        }
    else:
        post_params = {
            "url": config.prod_url,
            "token": config.prod_key
        }
    items = Model.get_items()
    i = 1
    for item in items:
        # Check if item is ready for post
        if item[10] == 1:
            # Check if item have not been posted and post it
            if item[11] == 1 and item[12] == 0:
                categories = list()
                if item[5] == "youtube":
                    categories = ["1406"]

                categories.append(str(post.get_category_id(
                        post_params["url"],
                        post_params["token"],
                        unidecode(unidecode(item[-1]).lower())
                    ))
                )
                item_dic = {
                    "title": item[2],
                    "description": item[14],
                    "tags": item[9],
                    "slug": item[2],
                    "category": ",".join(categories)
                }

                response = post.wordpress_create_post(item_dic, post_params)
                print("{} successfully posted: ".format(item_dic["title"]))
                print(response)
                if response:
                    Model.update_item(item[0])
                    print("sleeping for 1min")
                    if args.batch == i:
                        break
                    i += 1
                    time.sleep(60)
