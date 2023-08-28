# парсит адреса и тел.номера медцентров
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import re
from geopy.geocoders import Nominatim


# создаем экземпляр ChromeOptions и добавляем опцию для скрытия окна браузера
chrome_options = Options()
chrome_options.add_argument('--headless')
# инициализируем драйвер браузера Chrome
driver = webdriver.Chrome(options=chrome_options)

#  URL страниц Лодэ, Синево-Минск, Синево-Гомель, Синлаб, КВД, 1 ГКБ, Санте и Макаёнка
url = ['https://www.lode.by/contacts/', 'https://helix.by/centers-addresses/',
'https://helix.by/centers-addresses/gomel/', 'https://www.synlab.by/branch-address-ru', 'https://kvd.by/',
'https://6gkb.by/kontakty', 'https://sante.by/contacts',
'https://makaenka17med.by/contacts/','https://medart.by/contacts/' , 'https://diaglab.by/offices/' , 'https://invitro.by/offices/minsk/']

# создаем исходный DF
df_contacts = pd.DataFrame(data={"clinic_id": [], 'Клиника': [], 'Город': [], 'Улица': [], 'Дом': [], 'Телефоны': []})


# добавляет новые контакты в наш DF
def to_df(id1, s1, l1, l2, l3, l4):
    list_id = []
    list_name = []
    for i in range(len(l1)):
        list_id.append(id1)
        list_name.append(s1)
    data_dict = [{"clinic_id": i,'Клиника': a, 'Город': b, 'Улица': c, 'Дом': d, 'Телефоны': e} for i, a, b, c, d, e in
                zip(list_id, list_name, l1, l2, l3, l4)]
    df = pd.DataFrame(data_dict)
    return df


# начинаем парсинг
driver.get(url[0])  # ЛОДЭ
clinic_id = "Лодэ"
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
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[1])  # СИНЭВО-МИНСК
clinic_id = "Хеликс"
clinic_name = 'Helix'
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
    street.append(temp_split[1].replace("В.", ""))
    number.append(temp_split[2])

# поиск номеров телефонов
tels = driver.find_elements(By.XPATH, "//div [@class='footer-phone-num']")
for tel in tels:
    phone.append(tel.text)
phone = [", ".join(phone) for i in range(len(city))]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[2])  # СИНЭВО-ГОМЕЛЬ
clinic_id = "Хеликс"
clinic_name = 'Helix'
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
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[3])  # СИНЛАБ
clinic_id = 'Синлаб'
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
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[4])  # МГКЦД
clinic_id = "КВД"
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
number.append(temp_split[2].replace("д.", ""))

# поиск телефона
tels = driver.find_element(By.CSS_SELECTOR, 'a[href*=tel]')
phone.append(tels.text)

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[5])  # 6-ГКБ
clinic_id = "6-ГКБ"
clinic_name = '6-Я ГОРОДСКАЯ КЛИНИЧЕСКАЯ БОЛЬНИЦА'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса 1gkb
#adr = driver.find_element(By.XPATH, "//span [@class='address']")
#temp_split = adr.text[10:].split(',')
#city.append(temp_split[0])
#street.append(temp_split[1])
#number.append(temp_split[2])

# поиск телефона
#tels = driver.find_element(By.CSS_SELECTOR, 'a[href*=tel]')
#phone.append(tels.text[2:])


# поиск адреса
adr = driver.find_element(By.XPATH, "//p [@class='header__address uk-animation-fade']")
temp_split = adr.text.split(',')
city.append(temp_split[0].replace("г.", ""))
street.append(temp_split[1].replace("ул.", ""))
number.append(temp_split[2][:2])

# поиск телефона
tels = driver.find_elements(By.XPATH, "//span [@class='uk-h5 uk-text-bold uk-text-success']") 
phone.append(tels[10].text)

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[6])  # Санте
clinic_id = 'Sante'
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
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)

driver.get(url[7])  # макаенка
clinic_id = "РЦМРиБ"
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
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)



driver.get(url[8])  # Общество с ограниченной ответственностью «МедАрт»     
clinic_id = "Медарт"
clinic_name = ' Общество с ограниченной ответственностью «МедАрт» '
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr_title = driver.find_element(By.XPATH , '//*[@id="my-content"]/section/div/div/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/p')
adr = adr_title.text.split(',')
city.append(adr[0])
street.append(adr[1])
number.append(adr[2])


# поиск телефона
tels_element = driver.find_elements(By.CSS_SELECTOR, "div.contact-info-text")
tels = tels_element[2].text.split('\n')[1:]
for tel in tels:
    phone.append(tel)

phone = [", ".join(phone)]

# print(clinic_name, city, street, number, phone)

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)
pd.set_option('display.max_colwidth', None)



driver.get('https://diaglab.by/offices/minsk/')  # ООО "ПрофЛабДиагностика    
clinic_id = "Диаглаб"
clinic_name = ' ООО "ПрофЛабДиагностика"'
city = []
street = []
number = []
phone = []
links = []

# поиск адреса
adr_title = driver.find_element(By.XPATH , '/html/body/main/div/div[1]/div[2]/div[2]/div/div/div/a[1]/div')
adr = adr_title.text.replace('Лаборатория «ПрофЛабДиагностика» на Семашко\n','').split(',')
city.append(adr[0].replace('г.','').strip())
street.append(adr[1])
number.append(adr[2])


# поиск телефона
tels_element = driver.find_element(By.CSS_SELECTOR, "body > footer > div > div.row > div:nth-child(4) > div")
tels = tels_element.text.split('\n')[1:-2]
for tel in tels:
    phone.append(tel)

phone = [", ".join(phone)]

# print(clinic_name, city, street, number, phone)


# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)
pd.set_option('display.max_colwidth', None)



driver.get(url[10])  # Инвитро
clinic_id = 'Инвитро'
clinic_name = 'Инвитро'
city = []
street = []
number = []
phone = []
links = []

def split_address(string):
    # Разделить строку на адресные компоненты и номер телефона
    parts = re.split(r',|\n', string)
    # Удалить начальные и конечные пробелы из каждой части
    parts = [part.strip() for part in parts]
    # Исключить номер телефона, начинающийся с "8("
    parts = [part for part in parts if not part.startswith('8(')]
    if len(parts) == 4:
        last_item = parts[-1]
        second_last_item = parts[-2]
        merged_item = f"{second_last_item}, {last_item}"
        parts = parts[:-2] + [merged_item]
    return parts


for adr in driver.find_elements(By.XPATH, "//p [@class='map-panel__result-address showOnMap']"):
    s = adr.text
    spl_adr= split_address(s)
    city.append(spl_adr[0].replace('г.','').strip())
    fixst = spl_adr[1]
    fixst = fixst.replace("пр-кт Партизанский", "Партызанскі праспект")
    fixst = fixst.replace("пр-т", "")
    fixst = fixst.replace("С.", "")
    fixst = fixst.replace("ул.", "")
    fixst = fixst.replace("Звезда", "Звязда")
    street.append(fixst)
    fixst = spl_adr[2]
    fixst = fixst.replace("д.", "")
    fixst = fixst.replace("пом. 1Н.", "")
    fixst = fixst.replace("к. 1", "")
    number.append(fixst)
    
    
for tel in driver.find_elements(By.XPATH, "//a [@class='header-phone__link']"):
    phone.append(tel.text)
phone = [", ".join(phone) for i in range(len(city))]

# применяем функцию для создания dataframe
temp_call_df = to_df(clinic_id, clinic_name, city, street, number, phone)
df_contacts = pd.concat([df_contacts, temp_call_df], ignore_index=True)
pd.set_option('display.max_colwidth', None)

#df_contacts.to_csv("C:/Users/user/PycharmProjects/gp_med/data/df_contacts_new.csv")
#print(df_contacts)
# Создание геокодера
geolocator = Nominatim(user_agent='my_app')

# Функция для получения координат адреса
def get_coordinates(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if json_data:
            latitude = json_data[0]['lat']
            longitude = json_data[0]['lon']
            return latitude, longitude
    return None, None

# Применение функции к каждой строке датафрейма
df_contacts['адрес'] = df_contacts['Город'] + ', ' + df_contacts['Улица'] + ', ' + df_contacts['Дом']
df_contacts[['lat', 'lng']] = df_contacts['адрес'].apply(get_coordinates).apply(pd.Series)


if __name__ == "__main__":
    print(df_contacts)
    df_contacts.to_csv("data/df_contacts_new_with_coordinates.csv")
