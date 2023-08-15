
import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod
from WebDriver import WebDriver, Analysis

class DriverMakaenka(WebDriver):
    URL = "https://makaenka17med.by/prices/"
    NAME = "makaenka17med.by"

    def __init__(self):
        ...

    def get_analysis(self):
        analysis_dict = {}
        i = 0
        soup = self._scan_page(self.URL)
        for tag in soup.find_all(name="div", class_="dropdown-item"):
            analysis_name_add = ""
            chapter = tag.find(name="button").text

            for row in tag.find(name="tbody").find_all("tr"):
                if row.find(name="div", class_="table-list__title"):
                    analysis_name_add = row.find(name="div", class_="table-list__title").get_text(strip=True)
                else:
                    columns = row.find_all("td")

                    analysis_name = analysis_name_add + " " + columns[0].get_text(strip=True)
                    analysis_cost = columns[1].get_text(strip=True)
                    analysis = Analysis(self.NAME, chapter, analysis_name, analysis_cost, "")
                    analysis_dict[i] = analysis.to_dict()
                    i += 1

        return analysis_dict

