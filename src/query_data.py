# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 17:21
import pandas as pd
from pymongo import MongoClient

from src.settings import DATABASE, History_data

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


class QueryData:
	def __init__(self, dbClient: MongoClient):
		self.database = dbClient[DATABASE]

	def get_historical_data(self, lst_symbol: list, start=None, end=None):
		"""
		To get historical data from database
		:param lst_symbol: a list of requested symbols
		:param start:
		:param end:
		:return: a pd.DataFrame
		"""
		his_data_coll = self.database[History_data]
		query = {
			'name': {'$in': lst_symbol},
			'date': {}
		}
		if start is not None:
			query['date']['$gte'] = start
		if end is not None:
			query['date']['$lte'] = end
		cursor = his_data_coll.find(query)
		df = pd.DataFrame(data=list(cursor))
		df = df.drop(['_id'], axis=1)
		df = df.set_index('date')
		return df

	@staticmethod
	def resample_data(data: pd.DataFrame, rule='D'):
		df = pd.DataFrame()
		# df['name'] = data['name'].resample(rule)
		df['price'] = data['price'].resample(rule).mean().fillna(method='ffill')
		df['high'] = data['high'].resample(rule).max().fillna(method='ffill')
		df['low'] = data['low'].resample(rule).min().fillna(method='ffill')
		df['open'] = data['open'].resample(rule).mean().fillna(method='ffill')
		df['volume'] = data['volume'].resample(rule).sum().fillna(method='ffill')
		return df

	def get_list_ticket(self, index='VN 30 (VNI30)'):
		his_data_coll = self.database[History_data]
		cursor = his_data_coll.find({'index': {'$eq': index}})
		df = pd.DataFrame(data=list(cursor))
		lst_ticket = list(df['name'].drop_duplicates())
		return lst_ticket
