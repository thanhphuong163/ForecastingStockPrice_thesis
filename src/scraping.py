# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:57
import time

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.config_tickets import REAL_TIME_HEADER_XPATH, COMPONENT_HEADER_DATA

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


class WebScraping:
	def __int__(self, driver_lst, verbose=True):
		self.driver_lst = driver_lst
		self.verbose = verbose

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
	def convert_number(column):
		return column.apply(lambda x: np.float(x.replace(',', '')))

	@staticmethod
	def convert_volume(column):
		lst = []
		for item in column:
			char = item[-1]
			digits = item[:-1]
			value = np.float(digits)
			if char == 'K':
				value *= 10e3
			elif char == 'M':
				value *= 10e6
			else:
				value = np.float(item.replace(',', ''))
			lst.append(value)
		return lst

	def start_scraping(self):
		try:
			for driver in self.driver_lst:
				row = self.scrape_indices(driver)
				df = self.scrape_components(driver)
				print(row)
				print(df)
		except Exception as e:
			print(e)
