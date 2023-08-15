# основано на создании карты сайта (потому что на сайте нет общей страницы для всех услуг), 
# затем перебор всех страниц и поиск нужных элементов услуги и цены, а также комментария
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from usp.tree import sitemap_tree_for_homepage
import pandas as pd
from datetime import date


class DriverLode():

    def __init__(self):
        ...

    def get_analysis(self):

        # создаем экземпляр ChromeOptions и добавляем опцию для скрытия окна браузера
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        # инициализируем драйвер браузера Chrome
        driver = webdriver.Chrome(options=chrome_options)

        # строим карту сайта, убираем повторы, кидаем их в список
        tree = sitemap_tree_for_homepage('https://www.lode.by')
        list_url = []
        for page in tree.all_pages():
            list_url.append(page.url)
        set_url = set(list_url)
        list_url = list(set_url)

        services = []   # тут будут услуги
        comments = []   # тут будут описания
        prices = []    # тут будут цены

        # берем по очереди url из листа и загружаем ее в браузер
        for url in list_url:
            value = ''
            text = ''
            #print(url) #  отображение адресов (для отладки)
            driver.get(url)


            # достаем элемент с ценой (лабораторные исследования)
            try:
                p2_element = driver.find_element(By.CLASS_NAME, 'analizes-info__price') 
                value = p2_element.text
            except:
                print(f"There is no [analizes-info__price] in {url}.")
            
            
            # достаем элемент с услугой (лабораторные исследования)
            try:
                s2_element = driver.find_element(By.CSS_SELECTOR, 'h1.mt0.lh1.analizes-detail__title [itemprop="name"]')
                text = s2_element.get_attribute("content")
            except:
                print(f"There is no //meta[@itemprop='name' in {url}.")

            
            if text != '' and value != '': #  проверка на пустые значения и выгрузка описания (комментария), 
                # т.к. на некоторых страницах может быть один из элементов, обозначающий что-то совершенно другое
                # на правильных страницах есть оба элемента
                services.append(text)
                prices.append(value)
                c_element = driver.find_element(By.CLASS_NAME, "text-guide__alt") 
                comments.append(c_element.text)
                continue
            else:           # далее здесь идет парсинг программ, направлений и диагностики 
                value = ''
                text = ''
                try:
                # element = driver.find_element(By.XPATH, "//meta[@itemprop='price']")
                # value = element.get_attribute("content")    # эти две строчки берут минимальную цену, если есть интервал цен, или само значение цены
                    p_element = driver.find_element(By.CSS_SELECTOR, "div.strong.color--text") # достаем элемент с ценой
                    value = p_element.text
                except:
                    print(f"There is no [div.strong.color--text] in {url}.")
                    continue
            
                try:
                    element = driver.find_element(By.XPATH, "//h1[@class=' ']") # достаем элемент с услугой (заголовком)
                    text = element.text
                except:
                    print(f"There is no [h1[@class=' '] in {url}.")
                
            
            if text != '' and value != '': #  проверка на пустые значения и выгрузка описания (комментария), 
                # т.к. на некоторых страницах может быть один из элементов, обозначающий что-то совершенно другое
                # на правильных страницах есть оба элемента
                services.append(text)
                prices.append(value)
                c_element = driver.find_element(By.CSS_SELECTOR, 'div.col-12.col-lg-8.text-guide.readmore')  # ищет текст описания  (для программ, диагностики и направл)
                paragraphs = c_element.find_elements(By.TAG_NAME, "p") # на сайте ЛОДЭ описание разбито на абзацы, поэтому его надо собрать
                temp_list_parags = []
                for paragraph in paragraphs:
                    temp_list_parags.append(paragraph.text)
                str_parags = ' '.join(temp_list_parags)     
                comments.append(str_parags)

            # # Трансформируем  в DataFrame
            # lode_result_df = pd.DataFrame({'lode_service': services, 'lode_price': prices, 'lode_service_comment': comments})     
            # # добавляем дату парсинга к датафрейму
            # lode_result_df = lode_result_df.assign(lode_pars_date=date.today())

        # сохраняем услуги и цены в словарь
            analysis_dict = {}
            for i in range(len(services)):
                analysis_dict[i] = {
                                    "source": "Lode.by",
                                    "chapter": "",
                                    "analysis_name": services[i],
                                    "analysis_cost": prices[i],
                                    "analysis_comment": comments[i]
                                    }
                i += 1

        return analysis_dict    
