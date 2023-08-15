import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from WebDriver import WebDriver, Analysis


class DriverMedart(WebDriver):
    URL = "https://medart.by/price/"
    NAME = "medart.by/"

    def __init__(self):
        ...

    def get_analysis(self):

        analisys_dict = {}
        i = 0
        soup = self._scan_page(self.URL)

        ID = ["sect_6", "sect_5", "sect_7", "sect_8", "sect_10", "sect_11", "sect_12", "sect_13", "sect_14",
              "sect_15", "sect_16", "sect_17", "sect_19", "sect_146"
              ]

        for k in ID:
            tag = soup.find('div', class_='section_filter', id=f"{k}")
            # print(k)
            # print(type(tag),len(tag),tag[0])

            R = tag.find(class_='pricemain-title_left sticky').text.strip()
            V = tag.find(class_='title').text.strip()
            S = tag.find(class_='categoriesmain_price-table').find('table')
            #             print(R,V)

            # Находим все строки таблицы, кроме первой (заголовочной)
            rows = S.find_all("tr")  # [1:]
            for row in rows:
                #                 Проверяем, есть ли у элемента row атрибут colspan
                if row.find("td").has_attr('colspan'):
                    V = row.find("td", class_="title").text
                    continue

                #                 Иначе продолжаем как обычно

                name_elem = row.find("td", class_="name")
                if name_elem is None:
                    print("Элемент name не найден!")
                    continue
                name = name_elem.get_text(strip=True)

                link = row.find("td", class_="name").find('a').get('href')

                price_elem = row.find("td", class_="price")
                if price_elem is None:
                    print("Элемент price не найден!")
                    continue
                price = price_elem.get_text(strip=True)

                chapter = (R, V)
                analisys_name = name
                analisys_cost = price
                analisys_comment = "https://medart.by" + link
                analisys = Analysis(self.NAME, chapter, analisys_name, analisys_cost, analisys_comment)
                analisys_dict[i] = (analisys.to_dict())
                i += 1
        
        return analisys_dict
