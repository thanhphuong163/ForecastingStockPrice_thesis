# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:50
import itertools

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.stattools import pacf, acf

from Models.Arima_Ann import HybridModel, AnnModel, ArimaModel

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

"""
Khi nhan nut Analyze
Truoc tien la nhap 2 tham so:
- lag: lay bao nhien step trong qua khu
- alpha: do tin cay
"""


def calculate_acf(time_series, lag=20, alpha=0.05):
	x = time_series.values
	acf_value, confint = acf(x, nlags=lag, alpha=alpha)
	confint_lower = confint[:, 0] - acf_value
	confint_upper = confint[:, 1] - acf_value
	return acf_value, confint_upper, confint_lower


def calculate_pacf(time_series, lag=20, alpha=0.05):
	x = time_series.values
	pacf_value, confint = pacf(x, nlags=lag, alpha=alpha)
	confint_lower = confint[:, 0] - pacf_value
	confint_upper = confint[:, 1] - pacf_value
	return pacf_value, confint_upper, confint_lower


def mean_absolute_percentage_error(y_true, y_pred):
	return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def root_mean_squared_error(y_true, y_pred):
	return np.sqrt(np.mean((y_true - y_pred) ** 2))


def evaluation(validation):
	mse = mean_squared_error(validation['y'], validation['yhat'])
	rmse = root_mean_squared_error(validation['y'], validation['yhat'])
	mae = mean_absolute_error(validation['y'], validation['yhat'])
	mape = mean_absolute_percentage_error(validation['y'], validation['yhat'])
	result = {
		'mse': mse,
		'rmse': rmse,
		'mae': mae,
		'mape': mape,
	}
	return result


def run_model_with_parameters(time_series: pd.Series, model_selection='ARIMA',
                              start_train=0.85, end_train=0.97, order=(1, 1, 0),
                              lag=2, hidden_layers=(7, 3), steps=60):
	# split data
	time_series = time_series.sort_index()
	time_series = time_series.drop_duplicates()
	size = len(time_series)
	train_start = int(start_train * size)
	train_end = int(end_train * size)
	train, test = time_series[train_start:train_end], time_series[train_end:]

	# Run model
	result = {}
	model = None
	insample_data = None
	if model_selection == 'ARIMA':
		model = ArimaModel(train, order=order)
		insample_data = train[1:]
	elif model_selection == 'ANN':
		model = AnnModel(train, lag=lag, hidden_layers=hidden_layers)
		insample_data = train[lag + 1:]
	elif model_selection == 'Hybrid':
		model = HybridModel(train, order=order, lag=lag, hidden_layers=hidden_layers)
		insample_data = train[lag + 1:]
	else:
		return result

	# Fit model
	model.fit()

	# Evaluation
	train_validate = pd.DataFrame()
	train_validate['y'] = insample_data
	train_validate['yhat'] = model.get_insample_prediction()
	train_result = evaluation(train_validate)
	result['train_evaluation'] = train_result

	test_validate = pd.DataFrame()
	test_validate['y'] = test
	test_validate['yhat'] = model.validate(test)
	test_result = evaluation(test_validate)
	result['test_evaluation'] = test_result
	return result


def gen_order(p, d, q):
	return list(itertools.product(p, d, q))


def gen_ann(lags, hl):
	hl1 = hl
	hl2 = [int(i / 2) for i in hl]
	return list(itertools.product(lags, hl1, hl2))


def run_model_without_parameter(time_series: pd.Series, model_selection='ARIMA',
                                p=range(1, 4), d=range(0, 2), q=range(0, 3), lags=range(1, 5),
                                hl=range(2, 8)):
	pass
