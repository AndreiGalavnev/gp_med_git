import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import unicodedata 

from WebDriver import WebDriver, Analysis


class Driver6gkb(WebDriver):
    URL = "https://www.6gkb.by" 
    NAME = "6gkb.by"

    def __init__(self):
        super().__init__()
        self._chapters: List[str] = []

    def scan(self):

        #забираем ссылки на подразделы анализов hrefs
        url = "https://6gkb.by/uslugi/prejskuranty-dlya-grazhdan-respubliki-belarus"
        
        soup = self._scan_page(url=url)

        tags = soup.find(name="div", class_ = "uk-grid uk-grid-small uk-grid-match")

        for tag in tags.find_all(name="div", class_ = "uk-width-small-2-3 uk-width-medium-3-4"):

            for a in tag.find_all("a"):

                url_capter = Driver6gkb.URL + a.get("href")
                name_capter = a.get_text(strip=True)
                self.urls.append(url_capter)
                self._chapters.append(name_capter)
    
        return (self)

    def get_analysis(self):

        self.scan()
        i = 0
        #         analysis_list = []
        analysis_dict = {}
        url = self.urls[19]
        soup = self._scan_page(url)
        n_td = 6
            
        for tag in soup.find_all("table"):
            chapter = tag.find_all("tr")[3].text
    
            for row in tag.find_all("tr"):        

                if n_td == len(row.find_all("td")):
                    t_columns = row.find_all("td")
                    analysis_name = t_columns[1].get_text(strip=True)
                    analysis_cost = t_columns[5].get_text(strip=True)
                    analysis_comment = ""
                    analysis = Analysis(Driver6gkb.NAME, chapter, analysis_name, analysis_cost, analysis_comment)
                    analysis_dict[i] = analysis.to_dict()
                    i += 1            
        return analysis_dict