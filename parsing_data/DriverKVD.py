
import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod
from WebDriver import WebDriver, Analysis


class DriverKVD(WebDriver):
    URL = "https://kvd.by/%D0%BF%D0%BB%D0%B0%D1%82%D0%BD%D1%8B%D0%B5-%D1%83%D1%81%D0%BB%D1%83%D0%B3%D0%B8/%D0%BF%D1%80%D0%B5%D0%B9%D1%81%D0%BA%D1%83%D1%80%D0%B0%D0%BD%D1%82%D1%8B-%D0%B4%D0%BB%D1%8F-%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD-%D1%80%D0%B5%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B8-%D0%B1%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C"
    NAME = "kvd.by"

    def __init__(self):
        # Описываем все имеющиеся таблицы:
        # key - количество столбцов в таблице
        # value: 0 - номер столбца, содержащего название анализа
        # value: 1 - номер столбца, содержащего цену
        self.dict_tables = {
            10: (2, 9),
            2: (0, 1),
            7: (1, 6),
            8: (1, 7)
        }

    def get_analysis(self):

        analysis_dict = {}
        soup = self._scan_page(self.URL)
        i = 0
        for tag in soup.find_all(name="div", class_="entry spoiler"):

            #             date_update = tag.find("table").find_previous("p").strong.text
            #             date_update = dt.datetime.strptime(date_update, "%d.%m.%Y")

            chapter = tag.find("h3").get_text(strip=True)

            #     n_td - количество столбцов в таблице, считаю по последней строке
            n_td = len(tag.find(class_="cool-table").find_all("tr")[-1].find_all("td"))
            if (n_td == 1) and (chapter == "Определение ДНК возбудителей методом ПЦР"):
                n_td = 10
            for row in tag.find(class_="cool-table").find_all("tr"):
                if n_td == len(row.find_all("td")):
                    t_columns = row.find_all("td")
                    #             n_td = len(t_columns)
                    analysis_name = t_columns[self.dict_tables[n_td][0]].get_text(strip=True)
                    analysis_cost = t_columns[self.dict_tables[n_td][1]].get_text(strip=True)
                    analysis = Analysis(self.NAME, chapter, analysis_name, analysis_cost, '')
                    analysis_dict[i] = analysis.to_dict()
                    i += 1

        return analysis_dict