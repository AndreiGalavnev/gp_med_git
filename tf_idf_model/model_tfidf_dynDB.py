import pandas as pd
import numpy as np
from nltk import RegexpTokenizer
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import boto3

access_key = st.secrets["aws"]["access_key"]
secret_key = st.secrets["aws"]["secret_key"]

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
    
    @classmethod
    def stop_words(cls) -> set:
        # почему-то работает только с таким способом передачи стоп-слов
        custom_stop_words = ('мы', 'только', 'тем', 'были', 'было', 'много', 'вы', 'кто', 'три', 'будет', 'бы', 'выявление', 'же', 'можно', 'где', 'чего', 'но', 'здесь', 'им', 'определение', 'после', 'даже', 'под', 'эту', 'ж', 'а', 'ну', 'себе', 'вот', 'не', 'моя', 'что', 'ней', 'нее', 'эти', 'от', 'как', 'тогда', 'чтоб', 'со', 'в', 'зачем', 'больше', 'тот', 'нельзя', 'анализы', 'была', 'иногда', 'лучше', 'она', 'чтобы', 'нибудь', 'хорошо', 'есть', 'того', 'какая', 'них', 'мне', 'всю', 'меня', 'анализ', 'быть', 'уж', 'себя', 'через', 'опять', 'ее', 'вам', 'мой', 'этого', 'с', 'раз', 'вдруг', 'тоже', 'этот', 'сейчас', 'свою', 'два', 'этой', 'наконец', 'то', 'без', 'ли', 'ему', 'теперь', 'уже', 'уровень', 'нет', 'когда', 'на', 'тут', 'перед', 'впрочем', 'они', 'может', 'будто', 'чем', 'разве', 'если', 'какой', 'там', 'ты', 'из', 'всех', 'да', 'его', 'их', 'другой', 'потому', 'об', 'нас', 'за', 'по', 'до', 'ничего', 'всегда', 'ей', 'над', 'и', 'него', 'так', 'между', 'консультация', 'все', 'он', 'сам', 'куда', 'про', 'еще', 'ведь', 'ним', 'вас', 'почти', 'конечно', 'этом', 'при', 'ни', 'том', 'надо', 'хоть', 'такой', 'никогда', 'я', 'для', 'более', 'был', 'один', 'у', 'совсем', 'чуть', 'потом', 'к', 'во', 'всего', 'тебя', 'или', 'о')
        return set(custom_stop_words)
        
    
    def concatenate_values(self, row):
        return ' '.join(row)

    def get_documents(self, df: pd.DataFrame) -> list:
        # Получение текстовых данных из определенных колонок DataFrame
        df['concatenated'] = df.apply(self.concatenate_values, axis=1)
        return df["concatenated"].tolist()

        # Функция для предобработки текста
    def preprocess_text(self, text):
        tokens = self.tokenizer.tokenize(text.lower())
        tokens = [token for token in tokens if token not in Model_Tfidf.stop_words()]
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
        df_result.loc[(df_result["similarity"] < 0.64), ("best_match_synonym", "best_match_analysis")] = ""
        return df_result
    
    def get_similar_analysis(self, df: pd.DataFrame, query: str ):
        
        df.loc[(df["best_match_synonym"].isnull()), ("best_match_synonym", "best_match_analysis")] = ""
        self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_documents(df[["Название услуги", "best_match_synonym"]]))
        tfidf_query = self.vectorizer.transform([self.preprocessed_query(query)])

        similarities = cosine_similarity(tfidf_query, self.tfidf_matrix).flatten()
        # Сортировка документов по убыванию значений сходства
        sorted_indexes = similarities.argsort()[::-1]
        
        df["as"] = similarities            
                
        return df[["source", "Название услуги", "Цена услуги (руб)"]].iloc[sorted_indexes].loc[df["as"] >= 0.15]



# Создание клиента DynamoDB
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
new_order = ['index','source','Направление','Название услуги', 'Цена услуги (руб)', 'Описание услуги', 'best_match_synonym', 'best_match_analysis', 'similarity']
df = df[new_order]



if __name__ == "__main__":  
    m_tfidf = Model_Tfidf()
    st.set_page_config(layout="wide")
    # Заголовок страницы
    st.title("Поиск медуслуг")
    # Строка ввода для поиска
    search_query = st.text_input("Введите название медуслуги на русском языке", value="")
    # Фильтрация данных на основе поискового запроса
    filtered_df = m_tfidf.get_similar_analysis(df, search_query)
    filtered_df = filtered_df.rename(columns={'source': 'Источник'})
    # Вывод DataFrame
    st.dataframe(filtered_df, width=1300, hide_index=True)
    