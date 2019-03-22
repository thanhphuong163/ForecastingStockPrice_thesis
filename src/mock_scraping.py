# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:10
import time

from pymongo import MongoClient

from src.settings import DATABASE, HOST, IndColl

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

mockColl = 'MockCollection'
date_fmt = '%Y-%m-%d %H:%M:%S.%f'

if __name__ == '__main__':
	client = MongoClient(HOST)
	database = client.get_database(DATABASE)
	mock_collection = database[mockColl]
	indices_collection = database[IndColl]
	start = 1553221822
	end = 1553244511

	docs = indices_collection.find({'time': {'$gte': start, '$lt': end}, 'name': 'VN 30 (VNI30)'})
	for doc in docs:
		print(doc)
		mock_collection.insert_one(doc)
		time.sleep(10)
