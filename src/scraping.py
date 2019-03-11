# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:57
import time

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.config_tickets import REAL_TIME_HEADER_XPATH, COMPONENT_HEADER_DATA
from src.settings import SCRAPING_TIME, SLEEP_TIME

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


class WebScraping:
	def __init__(self, driver_lst, verbose=True):
		self.driver_lst = driver_lst
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
		return np.float(str_number.replace(',', ''))

	@staticmethod
	def convert_volume(str_vol):
		char = str_vol[-1]
		# To abandon the percentage character at the end of the string
		digits = str_vol[:-1]
		value = np.float(digits)
		if char == 'K':
			value *= 10e3
		elif char == 'M':
			value *= 10e6
		else:
			value = np.float(str_vol.replace(',', ''))
		return value

	@staticmethod
	def convert_change_per(str_value):
		# To abandon the percentage character at the end of the string
		return np.float(str_value[:-1])

	def scraping(self):
		try:
			row = {}
			df = pd.DataFrame()
			for driver in self.driver_lst:
				row = self.scrape_indices(driver)
				df = self.scrape_components(driver)
			self.indices_df = self.indices_df.append(row, axis=0)
			self.component_df = self.component_df.append(df, axis=0)
			time.sleep(SLEEP_TIME)
		except Exception as e:
			print(e)

	def organize_data(self):
		# indices dataframe
		indices_lst = np.unique(self.indices_df['name'])
		for index_name in indices_lst:
			df = self.indices_df
			df = df[df['name'].apply(lambda x: x == index_name)]
			tmp = dict(name=index_name,
			           last=np.mean(df['last']),
			           high=np.max(df['high']),
			           low=np.min(df['low']),
			           change=np.mean(df['change']),
			           chang_per=np.mean(df['change_per']),
			           volume=df['volume'][-1],
			           )

		pass

	def start_scraping(self):
		start = time.time()
		while True:
			current = time.time()
			if current - start < SCRAPING_TIME:
				self.scraping()
			else:
				self.organize_data()
				start = time.time()
