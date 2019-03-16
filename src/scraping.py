# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:57
import time

import numpy as np
import pandas as pd
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.config_tickets import REAL_TIME_HEADER_XPATH, COMPONENT_HEADER_DATA
from src.settings import SCRAPING_TIME, SLEEP_TIME, DATABASE, IndColl, CompoColl

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


class WebScraping:
	def __init__(self, driver_lst, dbClient: MongoClient, verbose=True):
		self.driver_lst = driver_lst
		self.database = dbClient.get_database(DATABASE)
		self.verbose = verbose
		self.indices_df = pd.DataFrame()
		self.component_df = pd.DataFrame()

	@staticmethod
	def scrape_indices(driver: webdriver):
		xpath_lst = REAL_TIME_HEADER_XPATH
		row = {}
		time_stamp = time.time()
		for item in xpath_lst:
			element = WebDriverWait(driver, 10).until(lambda dr: driver.find_element_by_xpath(item['xpath']))
			row[item['header']] = element.text
		row['timestamp'] = time_stamp
		return row

	@staticmethod
	def scrape_components(driver: webdriver):
		df = pd.DataFrame()
		for item in COMPONENT_HEADER_DATA:
			element_lst = WebDriverWait(driver, 10).until(lambda dr: driver.find_elements_by_xpath(item['xpath']))
			df[item['header']] = [element.text for element in element_lst]
		time_stamp = time.time()
		df['timestamp'] = time_stamp
		return df

	@staticmethod
	def convert_number(str_number):
		try:
			return np.float(str_number.replace(',', ''))
		except:
			return np.float('nan')

	@staticmethod
	def convert_volume(str_vol):
		try:
			char = str_vol[-1]
			# To abandon the percentage character at the end of the string
			digits = str_vol[:-1]
			value = digits.replace(',', '')
			if char == 'K':
				value = np.float(value) * 10e3
			elif char == 'M':
				value = np.float(value) * 10e6
			elif char == '-':
				value = np.float('nan')
			else:
				value = np.float(str_vol.replace(',', ''))
			return value
		except:
			return np.float('nan')

	@staticmethod
	def convert_change_per(str_value):
		# To abandon the percentage character at the end of the string
		try:
			return np.float(str_value[:-1])
		except:
			return np.float('nan')

	@staticmethod
	def convert_day_range(str_value):
		try:
			tmp = str_value.split('-')
			low = np.float(tmp[0].strip())
			high = np.float(tmp[1].strip())
			return low, high
		except:
			return np.float('nan'), np.float('nan')

	def convert_indices(self, row):
		tmp = dict()
		tmp['name'] = row['name']
		tmp['last'] = self.convert_number(row['last'])
		tmp['change'] = self.convert_number(row['change'])
		tmp['change_per'] = self.convert_change_per(row['change_per'])
		tmp['volume'] = self.convert_volume(row['volume'])
		tmp['low'], tmp['high'] = self.convert_day_range(row['day_range'])
		tmp['timestamp'] = row['timestamp']
		return tmp

	def convert_components(self, df):
		tmp_df = pd.DataFrame()
		tmp_df['name'] = df['name']
		tmp_df['last'] = df['last'].apply(lambda x: self.convert_number(x))
		tmp_df['high'] = df['high'].apply(lambda x: self.convert_number(x))
		tmp_df['low'] = df['low'].apply(lambda x: self.convert_number(x))
		tmp_df['change'] = df['change'].apply(lambda x: self.convert_number(x))
		tmp_df['change_per'] = df['change_per'].apply(lambda x: self.convert_change_per(x))
		tmp_df['volume'] = df['volume'].apply(lambda x: self.convert_volume(x))
		tmp_df['timestamp'] = df['timestamp']
		return tmp_df

	def scraping(self):
		try:
			for driver in self.driver_lst:
				row = self.scrape_indices(driver)
				df = self.scrape_components(driver)
				self.indices_df = self.indices_df.append(self.convert_indices(row), ignore_index=True)
				self.component_df = self.component_df.append(self.convert_components(df), ignore_index=True)
			time.sleep(SLEEP_TIME)
			print(len(self.indices_df))
			print(len(self.component_df))
		except Exception as e:
			print(e.args)

	def organize_data(self):
		# indices dataframe
		indices_lst = np.unique(self.indices_df['name'])
		lst_1 = []
		for index_name in indices_lst:
			df = self.indices_df
			df = df[df['name'].apply(lambda x: x == index_name)]
			tmp = dict(
				name=index_name,
				last=np.mean(df['last']),
				high=np.max(df['high']),
				low=np.min(df['low']),
				change=np.mean(df['change']),
				chang_per=np.mean(df['change_per']),
				volume=list(df['volume'])[-1],
				time=time.time(),
			)
			lst_1.append(tmp)
		indices_coll = self.database[IndColl]
		indices_coll.insert_many(lst_1)

		# Components dataframe
		component_lst = np.unique(self.component_df['name'])
		lst_2 = []
		for component_name in component_lst:
			df = self.component_df
			df = df[df['name'].apply(lambda x: x == component_name)]
			tmp = dict(
				name=component_name,
				last=np.mean(df['last']),
				high=np.max(df['high']),
				low=np.min(df['low']),
				change=np.mean(df['change']),
				chang_per=np.mean(df['change_per']),
				volume=list(df['volume'])[-1],
				time=time.time(),
			)
			lst_2.append(tmp)
		components_coll = self.database[CompoColl]
		components_coll.insert_many(lst_2)

	def start_scraping(self):
		if self.verbose:
			print('Start scraping...')
		start = time.time()
		while True:
			current = time.time()
			if current - start < SCRAPING_TIME:
				self.scraping()
			else:
				self.organize_data()
				start = time.time()