# парсит адреса и тел.номера медцентров
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import re

# создаем экземпляр ChromeOptions и добавляем опцию для скрытия окна браузера
chrome_options = Options()
chrome_options.add_argument('--headless')
# инициализируем драйвер браузера Chrome
driver = webdriver.Chrome(options=chrome_options)

#  URL страниц Лодэ, Синево-Минск, Синево-Гомель, Синлаб, КВД, 1 ГКБ, Санте и Макаёнка
url = ['https://www.lode.by/contacts/', 'https://helix.by/centers-addresses/',
       'https://helix.by/centers-addresses/gomel/', 'https://www.synlab.by/branch-address-ru', 'https://kvd.by/',
       'https://1gkb.by/%D0%BA%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82%D1%8B', 'https://sante.by/contacts',
       'https://makaenka17med.by/contacts/']

# создаем исходный DF
df_contacts = pd.DataFrame(data={'Клиника': [], 'Город': [], 'Улица': [], 'Дом': [], 'Телефоны': []})


# добавляет новые контакты в наш DF
def to_df(s1, l1, l2, l3, l4):
    list_name = []
    for i in range(len(l1)):
        list_name.append(s1)
    data_dict = [{'Клиника': a, 'Город': b, 'Улица': c, 'Дом': d, 'Телефоны': e} for a, b, c, d, e in
                 zip(list_name, l1, l2, l3, l4)]
    df = pd.DataFrame(data_dict)
    return df


# начинаем парсинг
driver.get(url[0])  # ЛОДЭ
clinic_name = 'Лодэ'
city = []
street = []
number = []
phone = []


# для чистки строк с адресами (функции отличаются, т.к. у разных медцентров разные способы записи адресов)
def split_text_lode(text):
    # Удалить текст до символов "г."
    if not text.startswith("г. "):
        text = re.sub(r'^.*г\.', 'г.', text)
    # Разбить текст по запятым
    text = text[2:]
    parts = text.split(',')
    result = []
    for part in parts:
        # Отделить цифры (вместе с буквой, если она есть) от текста
        subparts = re.split(r'(\d+[а-яА-Я]?)', part)
        result.extend(subpart.strip() for subpart in subparts if subpart.strip())
    return result


# сам парсинг
for slides in driver.find_elements(By.XPATH, "//div [@class='slide__content']"):
    # поиск адресов
    adr = slides.find_element(By.XPATH, ".//div[@class='name']")
    # поиск номеров телефонов
    for tel in slides.find_elements(By.XPATH, ".//div[@class='box']")[:2]:
        pattern = r"\+375\s\(\d{2}\)\s\d{3}-\d{2}-\d{2}"
        phone_numbers = re.findall(pattern, tel.text)
        phone += phone_numbers
    temp_split = split_text_lode(adr.text)
    city.append(temp_split[0])
    street.append(temp_split[1])
    number.append(temp_split[2])

# приводим в божеский вид данные
city.pop()
street.pop()
number.pop()
phone = phone[:-3]
phone = [phone[i:i + 3] for i in range(0, len(phone), 3)]
phone = [', '.join(x) for x in phone]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[1])  # СИНЭВО-МИНСК
clinic_name = 'Синэво/Helix'
city = []
street = []
number = []
phone = []


# для чистки строк
def split_text_syn(address):
    idx = address.find("(")
    if idx != -1:
        address = address[:idx]
    parts = address.split(',')
    return parts


# поиск адресов
for adr in driver.find_elements(By.XPATH, "//a [@class='map__lists-title-addrees']"):
    temp_split = split_text_syn(adr.text)
    city.append(temp_split[0])
    street.append(temp_split[1])
    number.append(temp_split[2])

# поиск номеров телефонов
tels = driver.find_elements(By.XPATH, "//div [@class='footer-phone-num']")
for tel in tels:
    phone.append(tel.text)
phone = [", ".join(phone) for i in range(len(city))]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[2])  # СИНЭВО-ГОМЕЛЬ
clinic_name = 'Синэво/Helix'
city = []
street = []
number = []
phone = []

# поиск адресов
for adr in driver.find_elements(By.XPATH, "//a [@class='map__lists-title-addrees']"):
    temp_split = split_text_syn(adr.text)
    city.append(temp_split[0])
    street.append(temp_split[1])
    number.append(temp_split[2])

# поиск номеров телефонов
tels = driver.find_elements(By.XPATH, "//div [@class='footer-phone-num']")
for tel in tels:
    phone.append(tel.text)
phone = [", ".join(phone) for i in range(len(city))]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[3])  # СИНЛАБ
clinic_name = 'Синлаб'
city = []
street = []
number = []
phone = []
links = []


# для чистки строк
def split_text_syn(address):
    address = address[2:]
    if address.count(',') == 2:
        parts = address.split(',')
    else:
        match = re.search(r'\d+[A-Za-zА-Яа-я]*', address)
        number = match.group()
        parts = address[:-2].split(',')
        parts.append(number)
    return parts


# поиск адресов
adr = driver.find_elements(By.CSS_SELECTOR, 'a[style="color: #003765;"]')
for elem in adr:
    if elem.get_attribute("href") and "minsk" in elem.get_attribute("href"):
        links.append(elem.get_attribute('href'))
        temp_split = split_text_syn(elem.text)
        if temp_split[0] != "Минск":
            temp_split[0] = "Минск"
        city.append(temp_split[0])
        street.append(temp_split[1])
        number.append(temp_split[2])
    elif elem.get_attribute("href") and "gomel" in elem.get_attribute("href"):
        links.append(elem.get_attribute('href'))
        temp_split = split_text_syn(elem.text)
        city.append(temp_split[0])
        street.append(temp_split[1])
        number.append(temp_split[2])

# поиск номеров телефонов
for i in links:
    driver.get(i)
    search_string = "(0"
    tels = driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(search_string))
    try:
        temp_tel = tels.text
        temp_tel = temp_tel.replace("\n", ", ")
    except:
        pass
    phone.append(temp_tel)

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[4])  # МГКЦД
clinic_name = 'Минский клинический центр дерматовенерологии'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr = driver.find_element(By.XPATH, "//div [@class='address']")
temp_split = adr.text[9:].split(',')
city.append(temp_split[0][1:])
street.append(temp_split[1])
number.append(temp_split[2])

# поиск телефона
tels = driver.find_element(By.CSS_SELECTOR, 'a[href*=tel]')
phone.append(tels.text)

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[5])  # 1-ГКБ
clinic_name = '1-Я ГОРОДСКАЯ КЛИНИЧЕСКАЯ БОЛЬНИЦА'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr = driver.find_element(By.XPATH, "//span [@class='address']")
temp_split = adr.text[10:].split(',')
city.append(temp_split[0])
street.append(temp_split[1])
number.append(temp_split[2])

# поиск телефона
tels = driver.find_element(By.CSS_SELECTOR, 'a[href*=tel]')
phone.append(tels.text[2:])

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[6])  # Санте
clinic_name = 'Sante'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr = driver.find_element(By.CSS_SELECTOR, "dd.StyledContact__Desc-sc-1gjsfgv-4.hYbNGA")
temp_split = adr.text.split(',')
city.append(temp_split[1][1:])
street.append(temp_split[2])
number.append(temp_split[3])

# поиск телефона
tels = driver.find_elements(By.CSS_SELECTOR, 'a[href*=tel]')
for tel in tels[17:20]:
    phone.append(tel.text)
phone = [", ".join(phone)]
# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[7])  # макаенка
clinic_name = 'Республиканский центр медицинской реабилитации и бальнеолечения'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr_title = driver.find_element(By.XPATH, '//h2[text()="Адрес"]')
adr = adr_title.find_element(By.XPATH, './following-sibling::p')
temp_split = adr.text[32:].split(',')
city.append(temp_split[0])
street.append(temp_split[1])
number.append(temp_split[2])

# поиск телефона
tels_element = driver.find_element(By.XPATH, "//div [@class='contacts__col']")
tels = tels_element.find_elements(By.CSS_SELECTOR, 'a[href*=tel]')
for tel in tels:
    phone.append(tel.text)
phone = [", ".join(phone)]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

import http.client, urllib.parse
import json


def get_coord(street: str, num: str, city: str = "Минск"):
    conn = http.client.HTTPConnection('api.positionstack.com')
    params = urllib.parse.urlencode({
        'access_key': '8e1b0fa23899d457d26cfe214071282a',
        'query': " ".join([street, num]),
        'region': city,
        'limit': 1,
    })

    conn.request('GET', '/v1/forward?{}'.format(params))
    res = conn.getresponse().read()
    data = json.loads(res.decode("utf-8"))

    return data["data"][0]["latitude"], data["data"][0]["longitude"]


# Исключаю гомель из датасета т.к. нужно убрать букву г.
df = df_contacts.loc[(df_contacts["Город"] == "Минск")]
# df1 = df_contacts.loc[(df_contacts["Город"] == "г. Минск")]
# df = pd.concat([df2, df1])
df

# добавляем широту и долготу в датасет
df["lat"] = df.apply(lambda x: get_coord(x['Улица'], x['Дом'])[0], axis=1)

df["lng"] = df.apply(lambda x: get_coord(x['Улица'], x['Дом'])[1], axis=1)
df
