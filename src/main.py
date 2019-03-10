# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:56
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config_tickets import ticket_lst

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


def request_2_web():
	options = Options()
	options.add_argument("--headless")
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option("prefs", prefs)
	driver_lst = []
	for ticket in ticket_lst:
		driver = webdriver.Chrome(options=options)
		driver.get(ticket['url'])
		driver_lst.append(driver)
	return driver_lst


if __name__ == '__main__':
	drivers = request_2_web()
