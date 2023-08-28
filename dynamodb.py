# для удаления данных из таблицы и для загрузки данных из csv в dynamodb в формате str, затем полный скан из БД в DF с преобразованием в необходимый формат
import boto3
import pandas as pd
import os


access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('AWS_REGION')
dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
# Получаем доступ к таблице 
table = dynamodb.Table('test_for_gp_med')

# !!!!!!!!!!!!!! полная очистка таблицы
response = table.scan()
while 'Items' in response:
    items = response['Items']
    for item in items:
        table.delete_item(Key={'index': item['index'], 'source': item['source']})
    try:
        response = table.scan(ExclusiveStartKey=response.get('LastEvaluatedKey'))
    except:
        break


# Чтение файла CSV с помощью библиотеки pandas
df = pd.read_csv('C:/Users/user/PycharmProjects/local_gp_med/gp_med/data/preprocessed_data/df_result_fix.csv')
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
        'similarity': str(row['similarity']),
        'clinic_id': str(row['clinic_id'])
    }
    table.put_item(Item=item)


df.reset_index(inplace=True)
df = df.rename(columns={'source': 'Источник', 'chapter': 'Направление', 'analysis_name':'Название услуги', 'analysis_cost':'Цена услуги (руб)', 'analysis_comment':'Описание услуги'})
df = df.fillna('-')
df = df.astype(str)
items = df.to_dict(orient='records')

# Загрузка данных из датафрейма в таблицу
df.apply(load_data_to_dynamodb, axis=1)





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