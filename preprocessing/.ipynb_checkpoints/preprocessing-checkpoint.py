import numpy as np
import pandas as pd
import sys



class Preprocessing():

    S_PATTERN_REP = "[\xa0|\n|\.|\(|\)|\;]"
    A_PATTERN_REP = "[\xa0|\n|\.|\(|\)]"
    COST_PATTERN_FIND = "(\d+[\,\.\\s руб. ]*\d*)"
    COST_PATTERN_REP = {",| руб. ":".", " |руб.":""}
    A_PATTERN_REP = "[\xa0|\n|\.|\(|\)]"

    synonyms = "synonyms"
    analysis = "analysis"
    chapter = "chapter"
    analysis_name = "analysis_name"
    analysis_cost = "analysis_cost"

    def __init__(self):
        ...

    def syn_prettify(self, df: pd.DataFrame) -> pd.DataFrame:
        
        add_syn = pd.DataFrame({
                                'synonyms': [" рентген; рентгенография", " экг; электрокардиограмма", " мрт", " кт; компьютерная томография"],
                                'analysis': ["рентгенография", "электрокардиограмма", "магнитно-резонансная томография", "компьютерная томография"]
                                })

        df = df.applymap(str.lower)

        # убираем слово "синонимы"
        df[self.synonyms] = df[self.synonyms].str.split(":").str[1]

        # добавляем в таблицу синонимов еще несколько значений
        df = pd.concat((df, add_syn)).reset_index(drop=True)

        df[self.synonyms] = df[self.synonyms].str.strip()
        df[self.synonyms] = df[self.synonyms].str.replace(self.S_PATTERN_REP, "", regex=True)
        df[self.analysis] = df[self.analysis].str.replace(self.A_PATTERN_REP, "", regex=True)

        return df

    def analysis_prettify(self, df: pd.DataFrame) -> pd.DataFrame:

        df[self.analysis_name] = df[self.analysis_name].str.lower().str.strip()
        df[self.analysis_name] = df[self.analysis_name].str.replace(self.A_PATTERN_REP, "", regex=True)
        df = df.dropna(subset=[self.analysis_name]).reset_index(drop=True)
        
        df[self.chapter] = df[self.chapter].str.replace(self.A_PATTERN_REP, "", regex=True)

        df = df.drop_duplicates(subset = ["source", "analysis_name", "analysis_cost"], keep = 'last').reset_index(drop = True)

        df[self.analysis_cost] = df[self.analysis_cost].str.findall(self.COST_PATTERN_FIND).str[0]

        for pat, rep in self.COST_PATTERN_REP.items():
            df[self.analysis_cost] = df[self.analysis_cost].str.replace(pat, rep, regex=True)

        df = df.dropna(subset=self.analysis_cost).reset_index()
        df[self.analysis_cost] = df[self.analysis_cost].astype(float)
        
        return df


if __name__ == "__main__":

    rp = Preprocessing()

    df_synonyms = pd.read_csv("data/synonyms.csv", index_col=0).reset_index(drop=True)
    df_synonyms = rp.syn_prettify(df=df_synonyms)

    df_analysis = pd.read_csv("data/df_analysis.csv", index_col=0).reset_index(drop=True)
    df_analysis = rp.analysis_prettify(df=df_analysis)

    df_synonyms.to_csv("data/preprocessed_data/df_reg_sys.csv")
    df_analysis.to_csv("data/preprocessed_data/df_analysis.csv")

    print(df_synonyms.shape, "/n" , df_synonyms)
    print(df_analysis.shape, "/n" , df_analysis)
  




        