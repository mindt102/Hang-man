import requests
import json
from bs4 import BeautifulSoup

url = "https://1000mostcommonwords.com/1000-most-common-french-words/"
response = requests.get(url)

content = response.content

soup = BeautifulSoup(content, "html.parser")

french = {
    "word": [],
    "inEnglish": [],
}

table = soup.find("table")
all_tr = soup.find_all("tr")
for i in range(1,len(all_tr)):
    all_td = all_tr[i].find_all("td")
    french["word"].append(all_td[1].get_text())
    french["inEnglish"].append(all_td[2].get_text())

with open('data.json','w',encoding="ascii") as f:
    json.dump(french,f)