# для загрузки данных из csv в dynamodb в формате str, затем полный скан из БД в DF с преобразованием в необходимый формат
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import boto3
import streamlit as st
import pandas as pd


dynamodb = boto3.resource('dynamodb', region_name='eu-west-2',  aws_access_key_id='AKIAQR4LORUH4YRUT22Z', aws_secret_access_key='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')

# Получаем доступ к таблице 
table = dynamodb.Table('test_for_gp_med')
# Чтение файла CSV с помощью библиотеки pandas
df = pd.read_csv('C:/Users/user/PycharmProjects/local_gp_med/gp_med/data/preprocessed_data/df_result.csv')
columns_to_drop = ['Unnamed: 0.1', 'Unnamed: 0']
df = df.drop(columns=columns_to_drop)

def load_data_to_dynamodb(row):
    item = {
        'index': str(row['index']),
        'source': row['Источник'],
        'Направление': row['Направление'],
        'Название услуги': row['Название услуги'],
        'Цена услуги (руб)': str(row['Цена услуги (руб)']),
        'Описание услуги': row['Описание услуги'],
        'best_match_synonym': row['best_match_synonym'],
        'best_match_analysis': row['best_match_analysis'],
        'similarity': str(row['similarity'])
    }
    table.put_item(Item=item)



df = df.rename(columns={'source': 'Источник', 'chapter': 'Направление', 'analysis_name':'Название услуги', 'analysis_cost':'Цена услуги (руб)', 'analysis_comment':'Описание услуги'})
df = df.fillna('-')
df = df.astype(str)
items = df.to_dict(orient='records')
# Загрузка данных из датафрейма в таблицу
df.apply(load_data_to_dynamodb, axis=1)



# Создание клиента DynamoDB
dynamodb = boto3.client('dynamodb', region_name='eu-west-2')

# Получение всех элементов из таблицы
def scan_table(table_name):
    response = dynamodb.scan(TableName=table_name)
    items = response['Items']
    
    # Если в таблице есть ещё элементы, получаем их все
    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(TableName=table_name, ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    return items


table_name = 'test_for_gp_med'

# Вызов функции для получения всех элементов из таблицы
all_items = scan_table(table_name)
# преобразование DF
df = pd.DataFrame(all_items)
df = df.apply(lambda x: x.apply(lambda y: list(y.values())[0]))
df['similarity'] = df['similarity'].astype(float)
# Переиндексация столбцов в новом порядке
new_order = ['index','source','Направление','Название услуги', 'Цена услуги (руб)', 'Описание услуги', 'best_match_synonym', 'best_match_analysis', 'similarity']
df = df[new_order]