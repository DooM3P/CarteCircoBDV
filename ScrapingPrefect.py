import requests
from bs4 import BeautifulSoup
import pandas as pd
def listurl(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
    response = requests.request("GET", url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all("a", {"class": "link-download"})
    listurl=[]
    for i in table:
        if "AP" not in i.get("href"):
            listurl.append(i.get("href"))
    return set(listurl)
