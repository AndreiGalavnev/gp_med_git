# парсит инвитро
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd
from datetime import date

class DriverInvitro():
    def __init__(self):
        ...

    def get_analysis(self):

        # создаем экземпляр ChromeOptions и добавляем опцию для скрытия окна браузера
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        # инициализируем драйвер браузера Chrome
        driver = webdriver.Chrome(options=chrome_options)

        #  URL страниц всех анализов и страницы всех медуслуг
        url = ['https://invitro.by/analizes/for-doctors/', 'https://invitro.by/radiology/uzi/', 'https://invitro.by/analizes/profi/']
        list_services = []
        list_prices = []


        driver.get(url[0]) # начнем с анализов (их много)

        #жмет на кнопку "показать ещё" пока она не переставнет появляться
        for i in range(88):
            i += 1
            try:
                sleep(1)
                
                button = driver.find_element(By.ID, "showMore")
                button.click()
                #print(i)     #  для  дебаггинга
                sleep(5)    
            except:
                print(f'No more [ID showMore]  in {i}')     # для  дебаггинга
                continue

        # извлекаем список услуг и цен

        for service in driver.find_elements(By.XPATH, './/div[contains(@class, "items-row")]'):
            for names in service.find_elements(By.CLASS_NAME, 'result-item__title'):
                list_services.append([names.text])

            for prices in service.find_elements(By.CLASS_NAME, 'result-item__price'):
                list_prices.append([prices.text])



        driver.get(url[1]) # повторяем всё для медуслуг

        for i in range(8):
            i += 1
            try:
                sleep(1)
                button = driver.find_element(By.ID, "showMore")
                button.click()
                #print(i)    # элемент для дебаггинга
                sleep(5)    
            except:
                print(f'No more [ID showMore]  in {i}') 
                continue

        # извлекаем список услуг и цен

        for service in driver.find_elements(By.XPATH, './/div[contains(@class, "items-row")]'):
            for names in service.find_elements(By.CLASS_NAME, 'result-item__title'):
                list_services.append([names.text])

            for prices in service.find_elements(By.CLASS_NAME, 'result-item__price'):
                list_prices.append([prices.text])



        driver.get(url[2]) # и ещё раз для комплексов анализов

        for i in range(10):
            i += 1
            try:
                sleep(1)
                button = driver.find_element(By.ID, "showMore")
                button.click()
                #print(i)    # элемент для  дебаггинга
                sleep(5)    
            except:
                print(f'No more [ID showMore] in {i}') 
                continue

        # извлекаем список услуг и цен 

        for service in driver.find_elements(By.XPATH, './/div[contains(@class, "items-row")]'):
            for names in service.find_elements(By.CLASS_NAME, 'result-item__title'):
                list_services.append([names.text])

            for prices in service.find_elements(By.CLASS_NAME, 'result-item__price'):
                list_prices.append([prices.text])

        # сохраняем в услуги и цены в словарь
        i = 0
        analysis_dict = {}
        for analysis_name, analysis_cost in zip(list_services, list_prices):
            analysis_dict[i] = {
                                "source": "invitro.by",
                                "chapter": "",
                                "analysis_name": analysis_name[0],
                                "analysis_cost": analysis_cost[0],
                                "analysis_comment": ""
                                }
            i += 1

        return analysis_dict