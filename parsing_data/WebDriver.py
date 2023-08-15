import datetime as dt
from typing import List, Optional
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod


class Analysis:
    
    def __init__(self, source: str, chapter: str|None, analysis_name: str, analysis_cost:str, analysis_comment: str,):              

        self.source    = source
        self.chapter     = chapter
        self.analysis_name   = analysis_name
        self.analysis_cost   = analysis_cost
        self.analysis_comment  = analysis_comment

    def __repr__(self) -> str:
        return f"source = {self.source}, chapter = {self.chapter}, analysis_name = {self.analysis_name}, analysis_cost = {self.analysis_cost}, analysis_comment = {self.analysis_comment}"
    
    def to_dict(self) -> dict:
        return self.__dict__



class WebDriver(ABC):

    def __init__(self):
        self.urls: List[str] = []

    def _scan_page(self, url: str):
        # Прописываем нестандартный заголовок, чтобы сайт не принял нас за бота, который парсит его данные :)
        # headers = requests.utils.default_headers()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        }
        response = requests.get(url=url, headers=headers)

        if not response.ok:
            raise ValueError("no content to parse")

        return BeautifulSoup(response.content.decode(), "lxml")

    @abstractmethod
    def get_analysis(self):
        ...
