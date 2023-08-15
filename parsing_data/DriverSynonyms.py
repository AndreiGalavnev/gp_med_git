import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import unicodedata 
from WebDriver import WebDriver

class DriverSynonyms(WebDriver):

    URL = "https://www.invitro.ru/analizes/for-doctors"
    NAME = "https://www.invitro.ru"

    def __init__(self):

        super().__init__()
        self.analysis : List[str] = []

    def scan(self):
        soup = self._scan_page(url=SynonimsDriver.URL)
        for res in soup.find_all(name="div", class_="analyzes-item__title"):
            self.urls.append(SynonimsDriver.NAME + res.find("a").get("href"))
            self.analysis.append(res.find("a").get_text(strip=True))

        return (self)

    def get_analysis(self):

        self.scan()

        i = 0
        synonyms = []
        analysis_names = []

        for url, name in zip(self.urls[:10], self.analysis[:10]):
            time.sleep(3)
            for name_cat in ["div", "p"]:
                soup = self._scan_page(url)
                for tag in soup.find_all(name=name_cat, style="text-align: justify;"):
                    for b in tag.find_all("b"):
                        syn = b.get_text(strip=True).lower()
                        if (syn == "синонимы:") or (syn == "синонимы") or (syn == "синонимы: "):
                            synonyms.append(tag.get_text(strip=True))
                            analysis_names.append(name)
                
        return list(zip(synonyms, analysis_names))


