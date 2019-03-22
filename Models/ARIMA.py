# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:11

from statsmodels.tsa.arima_model import ARIMA

__author__ = 'ntphuong163'
__email__ = 'thanhphuong.its@gmail.com'


class ARIMAMODEL:
	def __init__(self, data, order=(0, 1, 0)):
		self.model = ARIMA(data, order)
		self.model_fit = None

	def fit(self):
		self.model_fit = self.model.fit()

	def predict(self, start, end):
		fmt = '%Y-%m-%d'
		predictions = self.model_fit.predict(
			start=start,
			end=end,
		)
		return predictions
