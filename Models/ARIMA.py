# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:11
from datetime import datetime

from statsmodels.tsa.arima_model import ARIMA

__author__ = 'ntphuong163'
__email__ = 'thanhphuong.its@gmail.com'


class ARIMAMODEL:
	def __init__(self, data, order=(0, 1, 0)):
		self.model = ARIMA(data, order)
		self.model_fit = None

	def fit(self):
		self.model_fit = self.model.fit()

	def predict(self):
		fmt = '%Y-%m-%d'
		predictions = self.model.predict(
			start=datetime.strptime('2016-03-1', fmt),
			end=datetime.strptime('2016-03-30', fmt)
		)
		return predictions
