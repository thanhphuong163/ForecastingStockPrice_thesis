# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:11

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

__author__ = 'ntphuong163'
__email__ = 'thanhphuong.its@gmail.com'


class ArimaModel:
	def __init__(self, historical_data: pd.Series, order=(1, 1, 0)):
		self.historical_data = historical_data
		self.order = order

	def fit(self):
		self.historical_data = pd.Series(self.historical_data)

		# Fit model
		model = sm.tsa.SARIMAX(self.historical_data, order=self.order, enforce_stationarity=False)
		self.model_result = model.fit()

		# Get residuals
		predictions = self.model_result.get_prediction()
		pred_mean = predictions.predicted_mean[1:]
		real_values = self.historical_data[1:]
		residuals = real_values - pred_mean[1:]
		self.residuals = pd.Series(residuals, index=real_values.index).fillna(0)

	def get_insample_prediction(self, start=None, end=None):
		if start is None or end is None:
			predictions = self.model_result.get_prediction()
			pred_mean = predictions.predicted_mean
		else:
			index = self.historical_data.index
			start_index = index.get_loc(start)
			end_index = index.get_loc(end)
			predictions = self.model_result.get_prediction(start=start_index, end=end_index).fillna(0)
			pred_mean = predictions.predicted_mean
		return pred_mean

	def validate(self, test_data):
		historical_data = list(self.historical_data)
		predictions = list()

		# Predict one step ahead
		for t in range(len(test_data)):
			model = sm.tsa.SARIMAX(historical_data, order=self.order, enforce_stationarity=False)
			model_fit = model.fit(disp=0)
			output = model_fit.forecast()
			predictions.append(output[0])
			historical_data.append(test_data[t])
		return pd.Series(predictions, index=test_data.index).fillna(0)

	def predict_multi_step_ahead(self, start=None, steps=5, freq='D'):
		# Initialize index
		if start is None:
			start = self.historical_data.index[-1] + pd.Timedelta(value=1, unit=freq)

		datetime_index = pd.date_range(start, periods=steps, freq=freq)

		# Get forecasting values
		pred = self.model_result.get_forecast(steps=steps)
		pred_mean = pred.predicted_mean
		series = pd.Series(data=pred_mean.values, index=datetime_index)
		return series


class AnnModel:
	def __init__(self, historical_data: pd.Series, lag=5, hidden_layers=(5,)):
		self.historical_data = historical_data
		self.lag = lag
		self.scaler = MinMaxScaler(feature_range=(-1, 1))
		self.model = MLPRegressor(solver='adam', alpha=1e-5,
		                          hidden_layer_sizes=hidden_layers,
		                          activation='tanh', random_state=1)

	def transform_to_supervised_data(self, data, index=None):
		# Scaled data
		self.scaler.fit(data)
		scaled_data = self.scaler.transform(data)
		if index is None:
			series = pd.Series(scaled_data.flatten(), index=self.historical_data.index).fillna(0)
		else:
			series = pd.Series(scaled_data.flatten(), index=index).fillna(0)

		# Transform into supervised data
		df_data = pd.DataFrame(index=series.index)
		for i in range(self.lag + 1):
			df_data['lag_' + str(i)] = series.shift(periods=i)

		return df_data.drop(df_data.index[:self.lag])

	def fit(self):
		# Initialize
		data = np.reshape(self.historical_data.values, (len(self.historical_data), 1))

		# Transform data
		supervised_data = self.transform_to_supervised_data(data)

		# Fit model
		self.y = supervised_data['lag_0']
		self.x = supervised_data.drop('lag_0', axis=1)
		self.model.fit(self.x, self.y)

	def get_insample_prediction(self, start=None, end=None):
		yhat = self.model.predict(self.x)
		descaled_yhat = self.scaler.inverse_transform(np.reshape(yhat, (len(yhat), 1)))
		series_yhat = pd.Series(descaled_yhat.flatten(), index=self.y.index).fillna(0)
		return series_yhat

	def validate(self, testing_data):
		# Transform data
		data = self.historical_data[-self.lag:].append(testing_data)
		reshaped_data = np.reshape(data.values, (len(data), 1))
		supervised_data = self.transform_to_supervised_data(reshaped_data, index=data.index)
		y = supervised_data['lag_0']
		x = supervised_data.drop('lag_0', axis=1)

		# Get predictions
		pred = self.model.predict(x)
		reshaped_pred = np.reshape(pred, (len(pred), 1))
		predictions = self.scaler.inverse_transform(reshaped_pred)
		return pd.Series(data=predictions.flatten(), index=testing_data.index)

	def predict_multi_step_ahead(self, start=None, steps=5, freq='D'):
		# Initialize index
		if start is None:
			start = self.historical_data.index[-1] + pd.Timedelta(value=1, unit=freq)
		datetime_index = pd.date_range(start, periods=steps, freq=freq)

		# Get forecasting values
		pred = []
		data = self.historical_data[-self.lag:]
		reshaped_data = np.reshape(data.values, (len(data), 1))
		scaled_data = self.scaler.transform(reshaped_data)
		temp = scaled_data.flatten()
		for t in range(steps):
			x = np.reshape(temp, (1, len(temp)))
			y = self.model.predict(x)
			pred.append(y)
			temp = np.append(temp, y)
			temp = temp[-self.lag:]

		# Descale predictions
		reshaped_pred = np.reshape(pred, (len(pred), 1))
		descaled_pred = self.scaler.inverse_transform(reshaped_pred)
		series = pd.Series(descaled_pred.flatten(), index=datetime_index)
		return series


class HybridModel:
	def __init__(self, historical_data: pd.Series, order=(1, 1, 0), lag=5, hidden_layers=(5,)):
		self.historical_data = historical_data
		self.order = order
		self.lag = lag
		self.hidden_layers = hidden_layers

	def fit(self):
		# Fit arima model
		self.arima_model = ArimaModel(self.historical_data, order=self.order)
		self.arima_model.fit()

		# Fit ann model for residuals
		residuals = self.arima_model.residuals
		self.ann_model = AnnModel(residuals, lag=self.lag, hidden_layers=self.hidden_layers)
		self.ann_model.fit()

	def get_insample_prediction(self, start=None, end=None):
		pred_mean = self.arima_model.get_insample_prediction()
		pred_residuals = self.ann_model.get_insample_prediction()
		pred_insample = pred_mean + pred_residuals
		return pred_insample

	def predict_multi_step_ahead(self, start=None, steps=5, freq='D'):
		pred_mean = self.arima_model.predict_multi_step_ahead(start=start, steps=steps, freq=freq)
		pred_residuals = self.ann_model.predict_multi_step_ahead(start=start, steps=steps, freq=freq)
		predictions = pred_mean + pred_residuals
		return predictions

	def validate(self, testing_data):
		pred_mean = self.arima_model.validate(testing_data)
		residuals = testing_data - pred_mean
		pred_residuals = self.ann_model.validate(residuals)
		predictions = pred_mean + pred_residuals
		return predictions
