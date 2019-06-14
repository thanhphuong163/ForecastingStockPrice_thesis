# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:50
import asyncio
import itertools

import numpy as np
import pandas as pd
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.stattools import pacf, acf
from tqdm import tqdm_notebook as tqdm

from Models.Arima_Ann import HybridModel, AnnModel, ArimaModel
# from Models.Lstm_geo_hybrid import LSTM_GBM
from src.config_tickets import ticket_lst
from src.scraping import WebScraping

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


def run_model_with_parameters(train: pd.Series, test: pd.Series,
                              model_selection='ARIMA', order=(2, 1, 2),
                              lag=1, hidden_layers=(4, 3),
                              window_size=10):
	# split data
	# time_series = time_series.sort_index()
	# time_series = time_series.drop_duplicates()
	# size = len(time_series)
	# train_start = int(start_train * size)
	# train_end = int(end_train * size)
	# train, test = time_series[train_start:train_end], time_series[train_end:]

	# Run model
	result = {}
	model = None
	insample_data = None
	try:
		if model_selection == 'ARIMA':
			model = ArimaModel(train, order=order)
			insample_data = train[1:]
			result['order'] = order
		elif model_selection == 'ANN':
			model = AnnModel(train, lag=lag, hidden_layers=hidden_layers)
			insample_data = train[lag + 1:]
			result['lag'] = lag
			result['hidden_layers'] = hidden_layers
		elif model_selection == 'Hybrid':
			model = HybridModel(train, order=order, lag=lag, hidden_layers=hidden_layers)
			insample_data = train[lag + 1:]
			result['order'] = order
			result['lag'] = lag
			result['hidden_layers'] = hidden_layers
		# elif model_selection == 'LSTM+GBM':
		# 	model = LSTM_GBM(train, window_size=window_size, lags=lag)
		# 	insample_data = train[window_size + lag:]
		# 	result['window_size'] = window_size
		# 	result['lag'] = lag

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
		result['status'] = True
		result['model_name'] = model_selection
		result['model'] = model
	except Exception as e:
		print(e)
		result['status'] = False

	return result


def gen_order(p, d, q):
	return list(itertools.product(p, d, q))


def gen_ann(lags, hl):
	hl1 = hl
	hl2 = [int(i / 2) for i in hl]
	return list(itertools.product(lags, hl1, hl2))


def gen_lstm(window_size, lags):
	return list(itertools.product(window_size, lags))


def choose_model(lst_result):
	mae = lst_result[0]['test_evaluation']['mae']
	result_selection = lst_result[0]
	for result in lst_result[1:]:
		if mae > result['test_evaluation']['mae']:
			mae = result['test_evaluation']['mae']
			result_selection = result
	return result_selection


def run_model_without_parameters(train: pd.Series, test: pd.Series, model_selection='ARIMA',
                                 p=range(1, 4), d=range(0, 2), q=range(0, 3),
                                 lags=range(1, 4), hl=range(3, 8), window_size=range(5, 11)):
	# Generate parameters
	lst_order = gen_order(p, d, q)
	lst_ann_param = gen_ann(lags, hl)
	lst_lstm = gen_lstm(window_size, lags)

	# Run model
	lst_result = list()
	if model_selection == 'ARIMA':
		for order in tqdm(lst_order):
			result = run_model_with_parameters(train, test, model_selection=model_selection,
			                                   order=order)
			if result['status']:
				lst_result.append(result)
	elif model_selection == 'ANN':
		for ann_param in tqdm(lst_ann_param):
			result = run_model_with_parameters(train, test, model_selection=model_selection,
			                                   lag=ann_param[0], hidden_layers=ann_param[1:])
			if result['status']:
				lst_result.append(result)
	elif model_selection == 'Hybrid':
		# Choose the best ARIMA model
		lst_arima_result = list()
		for order in tqdm(lst_order, desc='Choosing ARIMA'):
			result = run_model_with_parameters(train, test, model_selection='ARIMA', order=order)
			if result['status']:
				lst_arima_result.append(result)
		_result = choose_model(lst_arima_result)
		chosen_order = _result['order']

		# Choose the best ANN model
		for ann_param in tqdm(lst_ann_param, desc='Choosing ANN'):
			result = run_model_with_parameters(train, test, model_selection=model_selection,
			                                   lag=ann_param[0], hidden_layers=ann_param[1:],
			                                   order=chosen_order)
			if result['status']:
				lst_result.append(result)
	# elif model_selection == 'LSTM+GBM':
	# 	for lstm_param in lst_lstm:
	# 		result = run_model_with_parameters(train, test, model_selection='LSTM+GBM',
	# 		                                   window_size=lstm_param[0], lag=lstm_param[1])
	# 		if result['status']:
	# 			lst_result.append(result)

	# Model selection: model is selected based on MAE of test result
	result_selection = choose_model(lst_result)

	return result_selection, lst_result


def request_2_website():
	options = Options()
	options.add_argument("--headless")
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option("prefs", prefs)
	drivers = list()
	print('Requesting...')
	for ticket in ticket_lst:
		driver = webdriver.Chrome(options=options)
		driver.get(ticket['url'])
		drivers.append(driver)
	print('Requesting completed.')
	return drivers


def update_database(client: MongoClient, years=5):
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	scraper.scrape_historical_data(years=years)


def get_real_time_data(client: MongoClient, on=True):
	print('blah blah')
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)

	loop = asyncio.get_event_loop()
	asyncio.ensure_future(scraper.start_scraping())
	if on:
		loop.run_forever()
	else:
		loop.stop()
