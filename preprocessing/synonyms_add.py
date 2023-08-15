import pandas as pd
import sys, os

sys.path.insert(0, os.getcwd())

from tf_idf_model.model_tfidf import Model_Tfidf

if __name__ == "__main__":
    df_synonyms = pd.read_csv("data/preprocessed_data/df_reg_sys.csv")
    df_analysis = pd.read_csv("data/preprocessed_data/df_analysis.csv")

    # Добавим синонимы в таблицу анализов, для этого запустим модель 
    m_tfidf = Model_Tfidf()
    df_result = m_tfidf.get_similar_synonyms(df=df_analysis, df_synonyms=df_synonyms)

    df_result.to_csv("data/preprocessed_data/df_result.csv")