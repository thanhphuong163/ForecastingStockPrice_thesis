# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:29

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

import numpy as np
import pandas as pd
from keras.layers import LSTM, Dense
from keras.models import Sequential

from sklearn.preprocessing import MinMaxScaler


class LSTM_GBM:
	def __init__(self, historical_data, window_size=5, lags=5, n_epochs=100, verbose=False):
		self.target_volatility_scaler = MinMaxScaler(feature_range=(0, 1))
		self.target_drift_scaler = MinMaxScaler(feature_range=(-1, 1))
		self.model_volatility = Sequential()
		self.model_drift = Sequential()
		self.historical_data = historical_data
		self.window_size = window_size
		self.lags = lags
		self.verbose = verbose
		self.n_epochs = n_epochs
		# Initialize
		self.drift_scaler = MinMaxScaler(feature_range=(-1, 1))
		self.volatility_scaler = MinMaxScaler(feature_range=(0, 1))

	def calculate_drift(self, data):
		"""
		Parameters:
			data - np.array : time series data
		Returns:
			drift of the time series data
		"""
		T = len(data) - 1
		sigma = self.calculate_volatility(data)
		S = data
		lograte = (np.log(S[-1]) - np.log(S[0])) / T
		drift = sigma ** 2 / 2 + lograte
		return drift

	@staticmethod
	def calculate_volatility(S):
		"""
		Parameters:
			S - np.array : time series data
		Returns:
			volatility of the time series data
		"""
		dS = np.diff(S)
		S = S[:-1]
		sigma = np.sqrt(np.mean((dS ** 2) / (S ** 2)))
		return sigma

	def extract_drift(self, time_series):
		lst_drift = list()
		for i in range(len(time_series) - self.window_size + 1):
			window = time_series[i:i + self.window_size].values.flatten()
			lst_drift.append(self.calculate_drift(window))
		series_drift = pd.Series(data=lst_drift, index=time_series.index[self.window_size - 1:])
		return series_drift

	def extract_volatility(self, time_series):
		lst_volatility = list()
		for i in range(len(time_series) - self.window_size + 1):
			window = time_series[i:i + self.window_size].values.flatten()
			lst_volatility.append(self.calculate_volatility(window))
		series_volatility = pd.Series(data=lst_volatility, index=time_series.index[self.window_size - 1:])
		return series_volatility

	def transform_to_supervised_data(self, data, index=None):
		# Extract drift and volatility
		series_drift = self.extract_drift(data)
		series_volatility = self.extract_volatility(data)

		# Shift data
		df_lag_drift = pd.DataFrame(index=series_drift.index)
		for i in range(0, self.lags):
			df_lag_drift['Lag_' + str(i)] = series_drift.shift(periods=i)

		df_lag_volatility = pd.DataFrame(index=series_volatility.index)
		for i in range(0, self.lags):
			df_lag_volatility['Lag_' + str(i)] = series_volatility.shift(periods=i)

		# Scale data
		self.drift_scaler.fit(df_lag_drift)
		df_scaled_drift = pd.DataFrame(index=df_lag_drift.index,
		                               columns=df_lag_drift.columns,
		                               data=self.drift_scaler.transform(df_lag_drift))

		self.volatility_scaler.fit(df_lag_volatility)
		df_scaled_volatility = pd.DataFrame(index=df_lag_volatility.index,
		                                    columns=df_lag_volatility.columns,
		                                    data=self.volatility_scaler.transform(df_lag_volatility))

		y_drift = df_scaled_drift['Lag_0'][self.lags:]
		X_drift = df_scaled_drift.drop('Lag_0', axis=1)[self.lags:]

		y_volatility = df_scaled_volatility['Lag_0'][self.lags:]
		X_volatility = df_scaled_volatility.drop('Lag_0', axis=1)[self.lags:]

		df_drift_tmp = pd.DataFrame(df_lag_drift['Lag_0'])
		df_volatility_tmp = pd.DataFrame(df_lag_volatility['Lag_0'])
		self.target_drift_scaler.fit(df_drift_tmp)
		self.target_volatility_scaler.fit(df_volatility_tmp)

		return X_drift, y_drift, X_volatility, y_volatility

	def fit(self):
		# Initialize
		batch_size = 1

		# Transform data
		X_drift, y_drift, X_volatility, y_volatility = self.transform_to_supervised_data(self.historical_data)
		target_drift = y_drift.values
		target_volatility = y_volatility.values

		# Reshape data
		self.input_drift = X_drift.values
		self.input_drift = self.input_drift.reshape(self.input_drift.shape[0], 1, self.input_drift.shape[1])

		self.input_volatility = X_volatility.values
		self.input_volatility = self.input_volatility.reshape(self.input_volatility.shape[0], 1,
		                                                      self.input_volatility.shape[1])

		# Create model
		self.model_drift.add(
			LSTM(100, batch_input_shape=(batch_size, self.input_drift.shape[1], self.input_drift.shape[2]),
			     stateful=True))
		self.model_drift.add(Dense(1, activation='tanh'))
		self.model_drift.compile(loss='mean_squared_error', optimizer='adam')

		self.model_volatility.add(
			LSTM(100, batch_input_shape=(batch_size, self.input_volatility.shape[1], self.input_volatility.shape[2]),
			     stateful=True))
		self.model_volatility.add(Dense(10, activation='relu'))
		self.model_volatility.add(Dense(1, activation='relu'))
		self.model_volatility.compile(loss='mean_squared_error', optimizer='adam')

		# Fit model
		if self.verbose:
			print('Training drift...')
		self.model_drift.fit(self.input_drift, target_drift, epochs=self.n_epochs, batch_size=batch_size, verbose=0,
		                     shuffle=False)
		if self.verbose:
			print('Done.')
			print('Training volatility...')
		self.model_volatility.fit(self.input_volatility, target_volatility, epochs=self.n_epochs, batch_size=batch_size,
		                          verbose=0, shuffle=False)
		if self.verbose:
			print('Done.')

	@staticmethod
	def GBM_sim(S0, r=0.5, sigma=0.5, T=15):
		Z = np.random.normal(0, 0.5, T)  # the sequence of random variables
		t = np.linspace(1, T, T)
		W_t = np.cumsum(Z)  # the Wiener process

		S_t = S0 * np.exp((r - (sigma ** 2) / 2) * t + sigma * W_t)
		return S_t

	def validate(self, test):
		# Add more historical data into test data
		extra_size = self.lags + self.window_size - 1
		test_data = self.historical_data[-extra_size:].append(test)
		self.test = test

		# Initialize
		batch_size = 1

		# Transform data
		X_drift, y_drift, X_volatility, y_volatility = self.transform_to_supervised_data(test_data)
		self.target_drift = self.target_drift_scaler.inverse_transform(
			y_drift.values.reshape(len(y_drift.values), 1)).flatten()
		self.target_volatility = self.target_volatility_scaler.inverse_transform(
			y_volatility.values.reshape(len(y_volatility.values), 1)).flatten()

		# Reshape data
		input_drift = X_drift.values
		input_drift = input_drift.reshape(input_drift.shape[0], 1, input_drift.shape[1])

		input_volatility = X_volatility.values
		input_volatility = input_volatility.reshape(input_volatility.shape[0], 1, input_volatility.shape[1])

		pred_drift = self.model_drift.predict(input_drift, batch_size=batch_size)
		pred_volatility = self.model_volatility.predict(input_volatility, batch_size=batch_size)

		self.pred_drift = self.target_drift_scaler.inverse_transform(pred_drift).flatten()
		self.pred_volatility = self.target_volatility_scaler.inverse_transform(pred_volatility).flatten()

		# Reproduce predicted price
		_test = self.historical_data[-1:].append(test).values.flatten()
		#         print(len(_test))
		#         print(self.pred_drift)
		#         print(self.pred_volatility)
		prediction = list()
		for i in range(len(_test) - 1):
			S_0 = _test[i]
			S_t = self.GBM_sim(S_0, self.pred_drift[i], self.pred_volatility[i], 3)
			prediction.append(S_t[0])

		return self.historical_data[-1:].append(pd.Series(prediction, index=test.index))

	def predict_multi_step_ahead(self, start=None, steps=5, freq='D'):
		extra_size = self.lags + self.window_size
		# Initialize index
		if start is None:
			_start = self.historical_data.index[-1] + pd.Timedelta(value=1, unit=freq)
			past_data = self.historical_data[-extra_size:]
			S_0 = past_data[start]
		else:
			_start = start + pd.Timedelta(value=1, unit=freq)
			data = self.historical_data.append(self.test)
			past_data = data[-extra_size:]
			S_0 = past_data[start]

		datetime_index = pd.date_range(_start, periods=steps, freq=freq)

		# Initialize
		batch_size = 1

		# Transform data
		X_drift, y_drift, X_volatility, y_volatility = self.transform_to_supervised_data(past_data)
		target_drift = y_drift.values
		target_volatility = y_volatility.values

		# Reshape data
		input_drift = X_drift.values
		input_drift = input_drift.reshape(input_drift.shape[0], 1, input_drift.shape[1])

		input_volatility = X_volatility.values
		input_volatility = input_volatility.reshape(input_volatility.shape[0], 1, input_volatility.shape[1])

		# Predict
		pred_drift = self.model_drift.predict(input_drift, batch_size=batch_size)
		pred_volatility = self.model_volatility.predict(input_volatility, batch_size=batch_size)

		descaled_pred_drift = self.target_drift_scaler.inverse_transform(pred_drift).flatten()
		descaled_pred_volatility = self.target_volatility_scaler.inverse_transform(pred_volatility).flatten()

		S_t = self.GBM_sim(S_0, descaled_pred_drift[0], descaled_pred_volatility[0], steps)
		prediction = pd.Series(S_t, index=datetime_index)
		return self.test[-1:].append(prediction)

	def get_insample_prediction(self, start=None, end=None):
		batch_size = 1
		pred_drift = self.model_drift.predict(self.input_drift, batch_size=batch_size)
		pred_volatility = self.model_volatility.predict(self.input_volatility, batch_size=batch_size)

		descaled_pred_drift = self.target_drift_scaler.inverse_transform(pred_drift).flatten()
		descaled_pred_volatility = self.target_volatility_scaler.inverse_transform(pred_volatility).flatten()

		insample_data = self.historical_data[self.window_size + self.lags - 1:]
		prediction = list()
		for i in range(len(insample_data) - 1):
			S_0 = insample_data[i]
			S_t = self.GBM_sim(S_0, descaled_pred_drift[i], descaled_pred_volatility[i], 3)
			prediction.append(S_t[0])
		return pd.Series(prediction, index=insample_data.index[1:])


class GBM:
	def __init__(self, historical_data, window_size=5, verbose=False):
		self.historical_data = historical_data
		self.window_size = window_size
		self.verbose = verbose
		# Initialize
		self.drift_scaler = MinMaxScaler(feature_range=(-1, 1))
		self.volatility_scaler = MinMaxScaler(feature_range=(0, 1))

	def calculate_drift(self, data):
		"""
		Parameters:
			data - np.array : time series data
		Returns:
			drift of the time series data
		"""
		T = len(data) - 1
		sigma = self.calculate_volatility(data)
		S = data
		lograte = (np.log(S[-1]) - np.log(S[0])) / T
		drift = sigma ** 2 / 2 + lograte
		return drift

	@staticmethod
	def calculate_volatility(S):
		"""
		Parameters:
			S - np.array : time series data
		Returns:
			volatility of the time series data
		"""
		S_t = S[1:]
		S_t1 = S[:-1]
		k = len(S) - 1
		sigma = np.sqrt(np.sum(np.log(S_t / S_t1) ** 2) / k)
		return sigma

	@staticmethod
	def GBM_sim(S0, mu=0.5, sigma=0.5, T=15):
		Z = np.random.normal(0, 0.5, T)  # the sequence of random variables
		t = np.linspace(1, T, T)
		W_t = np.cumsum(Z)  # the Wiener process

		S_t = S0 * np.exp((mu - (sigma ** 2) / 2) * t + sigma * W_t)
		return S_t

	def validate(self, test):
		self.test = test
		extra_data = self.historical_data[-self.window_size:].append(test).values.flatten()
		prediction = list()
		for i in range(len(test)):
			data = extra_data[i:i + self.window_size]
			S_0 = data[-1]
			mu = self.calculate_drift(data)
			sigma = self.calculate_volatility(data)
			predicted_value = self.GBM_sim(S_0, mu, sigma)[0]
			prediction.append(predicted_value)
		series_prediction = pd.Series(data=prediction, index=test.index)
		return self.historical_data[-1:].append(series_prediction)

	def predict_multi_step_ahead(self, start=None, steps=5, freq='D'):
		# Initialize index
		if start is None:
			_start = self.historical_data.index[-1] + pd.Timedelta(value=1, unit=freq)
		else:
			_start = start + pd.Timedelta(value=1, unit=freq)

		datetime_index = pd.date_range(_start, periods=steps, freq=freq)

		data = self.test[-self.window_size:].values
		S_0 = data[-1]
		mu = self.calculate_drift(data)
		sigma = self.calculate_volatility(data)
		prediction = self.GBM_sim(S_0, mu, sigma, T=steps)
		return self.test[-1:].append(pd.Series(prediction, index=datetime_index))
