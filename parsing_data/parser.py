import datetime as dt
from typing import Iterable, List, Optional
import numpy as np
import pandas as pd

from Driver6gkb import Driver6gkb
from DriverKVD import DriverKVD
from DriverMakaenka import DriverMakaenka
from DriverMedart import DriverMedart
from DriverSynevo import DriverSynevo
from DriverSynlab import DriverSynlab
from DriverInvitro import DriverInvitro
from DriverLode import DriverLode
from DriverSynonyms import DriverSynonyms

def get_data(clinics:list) -> pd.DataFrame:
    dct_analysis = {}
    df = pd.DataFrame()
    
    for clinic in clinics:
        obj = clinic()
        dct_analysis = obj.get_analysis()
        df_analysis = pd.DataFrame(dct_analysis.values())
        df = pd.concat((df, df_analysis), ignore_index=True)
    return df


if __name__ == "__main__":

    lst_clinics = [Driver6gkb, DriverKVD, DriverMakaenka, DriverMedart, DriverSynevo, DriverSynlab, DriverInvitro, DriverLode]
    df = get_data(lst_clinics)
    df.to_csv("data/df_analysis.csv")

    df_synonyms = get_data([DriverSynonyms])
    df_synonyms.to_csv("data/df_synonyms.csv")






