# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:57
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.config_tickets import REAL_TIME_HEADER_XPATH

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


class WebScraping:
	def __int__(self, verbose=True, drivers=None):
		self.drivers = drivers
		self.verbose = verbose

	@staticmethod
	def scrape_indices(driver: webdriver):
		"""
		To parse html page into data
		:param driver: the page of exchange
		:return: all parsed data at a time
		"""
		xpath_lst = REAL_TIME_HEADER_XPATH
		row = {}
		time_stamp = time.time()
		for item in xpath_lst:
			element = WebDriverWait(driver, 10).until(lambda dr: driver.find_element_by_xpath(item['xpath']))
			row[item['header']] = element.text
		row['time'] = time_stamp
		return row
