import requests
import re
import json
from bs4 import BeautifulSoup
url = "https://www.riksdagen.se/sv/ledamoter-och-partier/ledamoterna/"
response =requests.get(url)
html_content = response.text

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)

commisioner_list = []
if match:
    json_data = match.group(1)
    data = json.loads(json_data)
    for commissioner in data["props"]["pageProps"]["contentApiData"]["commissioners"]:
        json_obj = {}
        calling_name = commissioner['callingName']
        surname = commissioner['surname']
        json_obj["namn"] = f"{calling_name} {surname}"
        json_obj["plats"] = 0
        json_obj["url"] = commissioner["url"]
        if commissioner["party"] == "-":
            json_obj["vilde"] = True
        else:    
            json_obj["parti"] =  commissioner["party"]
            json_obj["vilde"] = False
        commisioner_list.append(json_obj)

def scrape_representative_profile_links(url, comissioner):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find_all('dd', attrs={'class': "sc-8f482e4e-2 opzdv"})

    if commisioner["vilde"]:
        comissioner["valkrets"] = section[0].text.strip().split(", ")[1].split(" ")[0]
        commisioner["plats"] = section[0].text.strip().split(", ")[1].split(" ")[1]
    else:
        comissioner["valkrets"] = section[1].text.strip().split(", ")[1].split(" ")[0]
        commisioner["plats"] = section[1].text.strip().split(", ")[1].split(" ")[1]


for commisioner in commisioner_list:

    scrape_representative_profile_links(commisioner["url"], commisioner)

