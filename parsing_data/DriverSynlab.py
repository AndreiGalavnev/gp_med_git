import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod
from WebDriver import WebDriver, Analysis


class DriverSynlab(WebDriver):
    URL = "https://www.synlab.by"
    NAME = "Synlab.by"

    def __init__(self):
        super().__init__()
        self._chapters: List[str] = []

    def scan(self):
        url = "https://www.synlab.by/ru/%D0%BF%D1%80%D0%B5%D0%B9%D1%81%D0%BA%D1%83%D1%80%D0%B0%D0%BD%D1%82"
        soup = self._scan_page(url=url)
        tag = soup.find(name="ul", class_="nav menu checkup-menu mod-list")
        for a in tag.find_all("a"):
            url_chapter = DriverSynlab.URL + a.get("href")
            chapter = a.text
            self.urls.append(url_chapter)
            self._chapters.append(chapter)
#             print(f"{url_capter = }, {name_capter = }")
        return (self)

    def get_analysis(self):

        self.scan()
        i = 0
        #         analysis_list = []
        analysis_dict = {}
        for url_chapter, chapter in zip(self.urls, self._chapters):
            soup = self._scan_page(url_chapter)
            for tag in soup.find_all("table"):
                if tag:
                    for tr in tag.find_all("tr"):
                        t_columns = tr.find_all("td")
                        analysis_name = t_columns[0].get_text(strip=True)
                        analysis_cost = t_columns[1].text.strip()
                        if len(t_columns) == 3:
                            analysis_comment = t_columns[2].get_text(strip=True)
                        analysis = Analysis(DriverSynlab.NAME, chapter, analysis_name, analysis_cost, analysis_comment)
                        analysis_dict[i] = analysis.to_dict()
                        #                         analysis_list.append(analysis)
                        i += 1
            time.sleep(2)  # ставим задержку 2 секунды после парсинга каждого раздела
        return analysis_dict

