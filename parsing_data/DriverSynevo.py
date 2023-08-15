import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod
from WebDriver import WebDriver, Analysis


class DriverSynevo(WebDriver):
    URL = "https://api.synevo.by/preordering/v1.0/Service?contractId=24884&page=1&pageSize=150&clientServiceGroupId="
    NAME = "Synevo.by"

    def __init__(self):

        super().__init__()
        #         self.urls : List[str] = []
        self._chapters: List[str] = []

    def _scan_page(self, url: str):

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoicHJlb3JkZXJpbmdAc3luZXZvLmJ5Iiwicm9sZSI6IiIsImp0aSI6IjIxYTE1YzliLTA1OWYtNGM2ZS1iZTMxLWFkMTdjYjY3NDYyNyIsInNpZCI6IjE3Mi4yNS4yOS4xNyIsImV4cCI6MTcxNzY4OTcxNywiaXNzIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6NDQzMzYvIiwiYXVkIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6NDQzMzYvIn0.K8lZVkSHj5PDpCQY_VtltlUz1qDxN4N32qhNj6r-JdU"
        header = {'Authorization': 'Bearer ' + token}
        r = requests.get(url, headers=header)
        response = r.json()

        return response

    def scan(self):

        URL_cat = 'https://api.synevo.by/preordering/v1.0/ClientServiceGroup'
        categories = self._scan_page(url=URL_cat)
        groups = ([(dct["id"]) for dct in categories])[1:]
        self._chapters = ([(dct["name"]) for dct in categories])[1:]

        for chapter_id in groups:
            url = self.URL + str(chapter_id)
            self.urls.append(url)

        return (self)

    def get_analysis(self):

        self.scan()
        i = 0

        analysis_dict = {}

        for url, chapter in zip(self.urls, self._chapters):

            result = self._scan_page(url=url)

            for dct_analysis in result["services"]:
                analysis_name = dct_analysis["name"]
                analysis_cost = dct_analysis["finalPrice"]
                analysis_comment = dct_analysis["description"] if dct_analysis["description"] else "" + dct_analysis[
                    "remark"] if dct_analysis["remark"] else ""

                analysis = Analysis(DriverSynevo.NAME, chapter, analysis_name, analysis_cost, analysis_comment)
                analysis_dict[i] = analysis.to_dict()

                i += 1

        #             time.sleep(2) # ставим задержку 2 секунды после парсинга каждого раздела
        return analysis_dict