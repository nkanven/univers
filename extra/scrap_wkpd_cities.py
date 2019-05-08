"""for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
    print link.get('href')"""

from bs4 import BeautifulSoup
import requests
import re

wikipedia = "https://en.wikipedia.org/wiki/List_of_municipalities_of_Cameroon"
website = requests.get(wikipedia)
soup = BeautifulSoup(website.content, "html.parser")
mw_parser_output = soup.find(class_=re.compile("div-col columns column-width"))

li = mw_parser_output.find("ul").find_all("li")

for cities in li:
    with open("cameroun_cities.txt", "a+", encoding="utf-8") as cities_f:
        cities_f.write(cities.get_text()+",")
    print(cities.get_text())

#print(mw_parser_output.find("ul").find_all("li"))

