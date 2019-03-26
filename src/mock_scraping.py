# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:10

import pandas as pd
from pymongo import MongoClient

from src.settings import DATABASE, HOST, IndColl, DATA_PATH

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

mockColl = 'MockCollection'
date_fmt = '%Y-%m-%d %H:%M:%S.%f'

if __name__ == '__main__':
    client = MongoClient(HOST)
    database = client.get_database(DATABASE)
    mock_collection = database[mockColl]
    indices_collection = database[IndColl]

    df = pd.read_csv(DATA_PATH + 'vn30_20190322.csv')
    df = df.drop(df.columns[0], axis=1)
    for i in df.index:
        row = dict(df.loc[i, :])
        mock_collection.insert_one(row)
        # time.sleep(10)
