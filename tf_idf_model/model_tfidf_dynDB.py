import pandas as pd
import numpy as np
from nltk import RegexpTokenizer
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import boto3
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
import os


class Model_Tfidf():


    def __init__(self, 
                stemmer: SnowballStemmer = SnowballStemmer(language="russian"), 
                tokenizer: RegexpTokenizer = RegexpTokenizer(r"\w+"),
                vectorizer: TfidfVectorizer = TfidfVectorizer()
                ):
        self.stemmer = stemmer
        self.tokenizer = tokenizer
        self.vectorizer = vectorizer
        self.tfidf_matrix = np.ndarray([])
        self.df = pd.DataFrame()
    
    @classmethod
    def stop_words(cls) -> set:
        # stop_words = ('мы', 'только', 'тем', 'были', 'было', 'много', 'вы', 'кто', 'три', 'будет', 'бы', 'выявление', 'же', 'можно', 'где', 'чего', 'но', 'здесь', 'им', 'определение', 'после', 'даже', 'под', 'эту', 'ж', 'а', 'ну', 'себе', 'вот', 'не', 'моя', 'что', 'ней', 'нее', 'эти', 'от', 'как', 'тогда', 'чтоб', 'со', 'в', 'зачем', 'больше', 'тот', 'нельзя', 'анализы', 'была', 'иногда', 'лучше', 'она', 'чтобы', 'нибудь', 'хорошо', 'есть', 'того', 'какая', 'них', 'мне', 'всю', 'меня', 'анализ', 'быть', 'уж', 'себя', 'через', 'опять', 'ее', 'вам', 'мой', 'этого', 'с', 'раз', 'вдруг', 'тоже', 'этот', 'сейчас', 'свою', 'два', 'этой', 'наконец', 'то', 'без', 'ли', 'ему', 'теперь', 'уже', 'уровень', 'нет', 'когда', 'на', 'тут', 'перед', 'впрочем', 'они', 'может', 'будто', 'чем', 'разве', 'если', 'какой', 'там', 'ты', 'из', 'всех', 'да', 'его', 'их', 'другой', 'потому', 'об', 'нас', 'за', 'по', 'до', 'ничего', 'всегда', 'ей', 'над', 'и', 'него', 'так', 'между', 'консультация', 'все', 'он', 'сам', 'куда', 'про', 'еще', 'ведь', 'ним', 'вас', 'почти', 'конечно', 'этом', 'при', 'ни', 'том', 'надо', 'хоть', 'такой', 'никогда', 'я', 'для', 'более', 'был', 'один', 'у', 'совсем', 'чуть', 'потом', 'к', 'во', 'всего', 'тебя', 'или', 'о')
        custom_stop_words = ("уровень", "определение", "анализ", "консультация", "выявление", "исследование", "кол", "опред", "тест")
        return custom_stop_words
    
    def concatenate_values(self, row):
        return ' '.join(row)

    def get_documents(self, df: pd.DataFrame) -> list:
        # Получение текстовых данных из определенных колонок DataFrame
        df["concatenated"] = df.apply(self.concatenate_values, axis=1)
        return df["concatenated"].tolist()

        # Функция для предобработки текста
    def preprocess_text(self, text):
        tokens = self.tokenizer.tokenize(text.lower())
        tokens = [token for token in tokens if token not in self.stop_words()]
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        return stemmed_tokens

    # Предобработка текстовых данных
    def preprocessed_documents(self, df: pd.DataFrame):
        documents = self.get_documents(df)
        return [' '.join(self.preprocess_text(doc)) for doc in documents]

    # Предобработка запроса 
    def preprocessed_query(self, query:str):
        return ' '.join(self.preprocess_text(query))

    def get_similar_synonyms(self, df: pd.DataFrame, df_synonyms: pd.DataFrame):
        tfidf_synonyms = self.vectorizer.fit_transform(self.preprocessed_documents(df_synonyms[["analysis"]])) 
        tfidf_df = self.vectorizer.transform(self.preprocessed_documents(df[["Название услуги"]]))
        syn_indexes = []
        syn_similarity = []
        # Вычисление сходства между запросом и текстовыми данными
        for vec in tfidf_df:
            similarities = cosine_similarity(vec, tfidf_synonyms).flatten()
            # Сортировка документов по убыванию значений сходства
            sorted_indexes = similarities.argsort()[::-1]
            syn_indexes.append(sorted_indexes[0])
            syn_similarity.append(similarities[sorted_indexes[0]])

        df_similarity = pd.DataFrame({
                                        "best_match_synonym": df_synonyms["synonyms"].iloc[syn_indexes].values,
                                        "best_match_analysis": df_synonyms["analysis"].iloc[syn_indexes].values,
                                        "similarity": syn_similarity
                                    }, index=df.index).sort_index(ascending=False)
        
        df_result = pd.concat((df, df_similarity), axis=1)
        df_result.loc[(df_result["similarity"] < 0.58), ("best_match_synonym", "best_match_analysis")] = ""
        return df_result

    # def model_a_prepare(self, df:pd.DataFrame):
    #     df.loc[(df["best_match_synonym"].isnull()), ("best_match_synonym", "best_match_analysis")] = ""
    #     self.df = df.copy()
    #     # self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_documents(df[["Название услуги", "best_match_synonym"]]))
    #     self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_documents(df[["Название услуги"]]))
    #     return(self)
    def jaccard_score(self, A: str, B: str) -> float:
        set_A = set(A.split(" "))
        set_B = set(B.split(" "))
        intersection = len(set_A.intersection(set_B))
        union = len(set_A.union(set_B))
        return intersection / union

    def model_prepare(self, df:pd.DataFrame):
        df.loc[(df["best_match_synonym"].isnull()), ("best_match_synonym", "best_match_analysis")] = ""
        self.df = df.copy()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_documents(df[["Название услуги", "best_match_synonym"]]))
        return(self)

    def get_similar_analysis(self, query: str ):
        tfidf_query = self.vectorizer.transform([self.preprocessed_query(query)])
        similarities = cosine_similarity(tfidf_query, self.tfidf_matrix).flatten()
        # Сортировка документов по убыванию значений сходства
        sorted_indexes = similarities.argsort()[::-1]
        self.df["as"] = similarities  
        self.df["IoU"] = self.df.apply(axis=1, func=lambda ser: self.jaccard_score(ser["Название услуги"] + " " + ser["best_match_synonym"], query))
        
        df_as = self.df[["clinic_id", "source", "Название услуги", "Цена услуги (руб)", "as", "IoU"]].iloc[sorted_indexes].loc[self.df["as"]>0.23]
        df_IoU = self.df[["clinic_id", "source", "Название услуги", "Цена услуги (руб)", "as", "IoU"]].loc[self.df["IoU"]>0.1].sort_values("IoU", ascending=False)

        return (df_IoU.head(10) if df_as.shape[0] == 0 else df_as.head(10))



# local launch
#access_key = os.environ.get('AWS_ACCESS_KEY_ID')
#secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
#region = os.environ.get('AWS_REGION')
#dynamodb = boto3.client('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)



# Создание клиента DynamoDB
access_key = st.secrets["aws"]["access_key"]
secret_key = st.secrets["aws"]["secret_key"]
dynamodb = boto3.client('dynamodb', region_name='eu-west-2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

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
#new_order = ['index','source','Направление','Название услуги', 'Цена услуги (руб)', 'Описание услуги', 'best_match_synonym', 'best_match_analysis', 'similarity', 'clinic_id']
#df = df[new_order]



if __name__ == "__main__":  
    url = 'https://raw.githubusercontent.com/AndreiGalavnev/gp_med_git/master/data/df_contacts_new_with_coordinates.csv'
    df_coord = pd.read_csv(url)
    # for local deploy
    #df_coord = pd.read_csv('C:/Users/user/PycharmProjects/local_gp_med/gp_med/data/df_contacts_new_with_coordinates.csv')
    m_tfidf = Model_Tfidf().model_prepare(df)
    #m_tfidf = Model_Tfidf()
    st.set_page_config(layout="wide")
    # Заголовок страницы
    st.title("Поиск медицинских услуг")
    # Строки ввода
    search_query = st.text_input("Введите название медицинской услуги на русском языке", value="", key="med_input")
    geolocator = Nominatim(user_agent='my-app')
    geo_search_query = st.text_input("Введите свой адрес (город, улица, дом)", value="", key="address_input")
    button = st.button('Отправить запрос')

    if button:
    # Действия, выполняемые при нажатии кнопки
        filtered_df = m_tfidf.get_similar_analysis(search_query)
        filtered_df = filtered_df.rename(columns={'source': 'Источник'})
        filtered_df = filtered_df.drop(['as', 'IoU'], axis=1)
        filtered_df_copy = filtered_df.copy(deep=True)
        filtered_df_copy = filtered_df_copy.rename(columns={'clinic_id': 'Название клиники'})
        st.dataframe(filtered_df_copy, width=1300, hide_index=True)

        df_coord_filtered = pd.merge(filtered_df, df_coord, on='clinic_id')
        m = folium.Map(location=[53.9005, 27.5666], zoom_start=14)  # Начальные координаты для карты
        # Отображение точек с местоположением медцентров и подписями
        for index, row in df_coord_filtered.iterrows():
            popup_text = f"Клиника: {row['Клиника']} \nАдрес: {row['адрес']} \nТелефоны: {row['Телефоны']}"
            folium.Marker([row['lat'], row['lng']], popup=popup_text, icon=folium.Icon(color='black')).add_to(m)
        # Вывод карты на страницу Streamlit
        #folium_static(m)
        # Геокодирование введенного адреса
        location = geolocator.geocode(geo_search_query, country_codes='BY')
        
        if location:
            # Добавление маркера с местоположением введенного адреса
            folium.Marker([location.latitude, location.longitude], popup='Ваш адрес').add_to(m)
            # Центрирование карты на местоположении введенного адреса
            m.location = [location.latitude, location.longitude]
            # Вывод обновленной карты на страницу Streamlit
            folium_static(m)
        else:
            st.write('Адрес не найден')
    

    
    