import pandas as pd
import json
import re
import difflib as dif
import numpy as np
import sqlalchemy
import psycopg2
import logging

russia_reg = json.load(open('russia_geojson_wgs84.geojson', 'r'))
russia_reg_map = {}
for i in russia_reg['features']:
    i["id"] = i["properties"]["id"]
    russia_reg_map[i['properties']['name']] = i['properties']['id']

# con_str = 'oraclesql+psycopg2://<USER>:<PASS>@<HOST>:<PORT>/<DBNAME>'
# engine = sqlalchemy.create_engine(con_str)
# connect = engine.connect()
# df = pd.read_sql('<sqlscript>',connect)
df = pd.read_excel('~/Desktop/tst.xlsx')

months_dict = {1: 'Январь', 2: 'Февраль', 3: 'Март',  4: 'Апрель',
               5: 'Май',   6: 'Июнь',  7: 'Июль', 8: 'Август', 9: 'Сентябрь',
               10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
df['MONTH'] = df['MONTH_CONC'].map(months_dict)
df = df[df[['ADDRESS']].notnull().all(1)]

# для наших исходных данных сделаем отдельную таблицу с уникальными адресами
df_addr = df[['ADDRESS']].drop_duplicates().reset_index(drop=True)
try:
    df_addr['ADDRESS'] = df_addr['ADDRESS'].apply(lambda x: x.lower())
except:
    logging.info()

# Находим регион путем сравнения адреса и имен регионов
# Поиск по геокодеру дает худший результат и более сложный код

d = dif.Differ()
exceptions = ['обл', 'область', 'ская', 'тская', 'ирск', 'скаяобласть']

for i in range(len(df_addr)):
    the_best_fit = ''
    the_best_fit_key = 78  # заменить на 78
    if len(re.findall(r'москва', df_addr.iloc[i]['ADDRESS'])) > 0:
        df_addr.at[i, 'id'] = 78
        df_addr.at[i, 'state'] = 'Москва'
        continue
    else:

        for (j, h) in zip(russia_reg_map.keys(), russia_reg_map.values()):
            cur_addr = df_addr.iloc[i]['ADDRESS']
            diff = d.compare(cur_addr, j.lower())
            str1 = ''
            lst_of_str1 = []
            for k in diff:
                if k.startswith(' '):
                    str1 += k.replace(' ', '')
                elif len(str1) > 3 and str1 not in exceptions:
                    lst_of_str1.append(str1)
                    str1 = ''
                else:
                    str1 = ''
                    continue

            if len(lst_of_str1) > 0:
                if len(sorted(lst_of_str1)[-1]) > len(the_best_fit):
                    the_best_fit = sorted(lst_of_str1)[-1]
                    the_best_fit_key = h
                    state = j
                else:
                    continue
            else:
                continue

        df_addr.at[i, 'id'] = the_best_fit_key
        df_addr.at[i, 'state'] = state

df['ADDRESS'] = df['ADDRESS'].apply(lambda x: x.lower())
df = df.merge(df_addr, on = 'ADDRESS', how = 'left')
df.id = df.id.astype(int)
# Суммарная премия по регионам
df['PREM_SUM_REG'] = df.groupby('id')['SUM_POLIS_PREM'].transform('sum')
# Количество полисов по регионам
df['POL_COUNT'] = df.groupby('id')['ID'].transform('count')
# Средняя премия по регионам
df['AVG_SUM_PREM_REG']= df['PREM_SUM_REG']/df['POL_COUNT']
# Логарифмированная премия для более читаемой карты
df['LOG_PREM'] = df['PREM_SUM_REG'].apply(lambda x: np.log10(x))
# Логарифмированное кол-во полисов для более читаемой карты
df['LOG_POL_COUNT'] = df['POL_COUNT'].apply(lambda x: np.log10(x))
# Логарифмированная премия для более читаемой карты
df['LOG_AVG_SUM_PREM_REG'] = df['AVG_SUM_PREM_REG'].apply(lambda x: np.log10(x))
