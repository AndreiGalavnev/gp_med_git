#from re import A
import pandas as pd
import numpy as np
import nltk
from nltk import RegexpTokenizer
#from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import PlaintextCorpusReader
#import sys
import streamlit as st

#nltk.data.path.append('stopwords')



# Загрузка стоп-слов для определенного языка из файловой системы
#corpus_root = 'C:/Users/user/PycharmProjects/local_gp_med/gp_med/stopwords'
#file_pattern = r'russian\.txt'  # Шаблон имени файла
#corpus = PlaintextCorpusReader(corpus_root, file_pattern)
#stopwords = corpus.words('russian.txt')


# Загрузка стоп-слов и стеммера
#nltk.download('stopwords')
#nltk.download('punkt')


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
        #stop_words = set(stopwords)
        #stop_words = set(stopwords.words('russian'))
        # почему-то работает только с таким способом передачи стоп-слов
        custom_stop_words = ('мы', 'только', 'тем', 'были', 'было', 'много', 'вы', 'кто', 'три', 'будет', 'бы', 'выявление', 'же', 'можно', 'где', 'чего', 'но', 'здесь', 'им', 'определение', 'после', 'даже', 'под', 'эту', 'ж', 'а', 'ну', 'себе', 'вот', 'не', 'моя', 'что', 'ней', 'нее', 'эти', 'от', 'как', 'тогда', 'чтоб', 'со', 'в', 'зачем', 'больше', 'тот', 'нельзя', 'анализы', 'была', 'иногда', 'лучше', 'она', 'чтобы', 'нибудь', 'хорошо', 'есть', 'того', 'какая', 'них', 'мне', 'всю', 'меня', 'анализ', 'быть', 'уж', 'себя', 'через', 'опять', 'ее', 'вам', 'мой', 'этого', 'с', 'раз', 'вдруг', 'тоже', 'этот', 'сейчас', 'свою', 'два', 'этой', 'наконец', 'то', 'без', 'ли', 'ему', 'теперь', 'уже', 'уровень', 'нет', 'когда', 'на', 'тут', 'перед', 'впрочем', 'они', 'может', 'будто', 'чем', 'разве', 'если', 'какой', 'там', 'ты', 'из', 'всех', 'да', 'его', 'их', 'другой', 'потому', 'об', 'нас', 'за', 'по', 'до', 'ничего', 'всегда', 'ей', 'над', 'и', 'него', 'так', 'между', 'консультация', 'все', 'он', 'сам', 'куда', 'про', 'еще', 'ведь', 'ним', 'вас', 'почти', 'конечно', 'этом', 'при', 'ни', 'том', 'надо', 'хоть', 'такой', 'никогда', 'я', 'для', 'более', 'был', 'один', 'у', 'совсем', 'чуть', 'потом', 'к', 'во', 'всего', 'тебя', 'или', 'о')
        #custom_stop_words = ("анализ", "уровень", "определение", "анализы", "консультация", "выявление")
        return set(custom_stop_words)
        #return set(stop_words.union(custom_stop_words))
    
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
        tfidf_df = self.vectorizer.transform(self.preprocessed_documents(df[["analysis_name"]]))
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
        self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_documents(df[["analysis_name", "best_match_synonym"]]))
        tfidf_query = self.vectorizer.transform([self.preprocessed_query(query)])

        similarities = cosine_similarity(tfidf_query, self.tfidf_matrix).flatten()
        # Сортировка документов по убыванию значений сходства
        sorted_indexes = similarities.argsort()[::-1]
        
        df["as"] = similarities            
                
        return df[["source", "analysis_name", "analysis_cost"]].iloc[sorted_indexes].loc[df["as"] >= 0.15]



if __name__ == "__main__":  
    m_tfidf = Model_Tfidf()
    df_result = pd.read_csv("data/preprocessed_data/df_result.csv")
    #print( m_tfidf.get_similar_analysis(df_result, "узи мышц"))

    st.set_page_config(layout="wide")
    
    
    # Заголовок страницы
    st.title("Поиск медуслуг")
    # Строка ввода для поиска
    search_query = st.text_input("Введите название медуслуги на русском языке", value="")
    # Фильтрация данных на основе поискового запроса
    filtered_df = m_tfidf.get_similar_analysis(df_result, search_query)
    # Вывод DataFrame
    #st.write(filtered_df)
    st.dataframe(filtered_df, width=1300)
    