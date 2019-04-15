# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:56

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config_tickets import ticket_lst
from src.scraping import WebScraping
from src.settings import HOST

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

urlheader = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
	"X-Requested-With": "XMLHttpRequest"
}


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


def connect_2_dbServer():
	mongoClient = MongoClient(HOST)
	return mongoClient


def get_historical_data():
	url = 'https://www.investing.com/instruments/HistoricalDataAjax'
	payload = {
		'curr_id': '41064',
		'smlID': '2058618',
		'header': 'VN 30 Historical Data',
		'st_date': '3/15/2010',
		'end_date': '04/15/2019',
		'interval_sec': 'Daily',
		'sort_col': 'date',
		'sort_ord': 'DESC',
		'action': 'historical_data'
	}
	res = requests.post(url, data=payload, headers=urlheader)
	soup = BeautifulSoup(res.content, 'html.parser')
	tbody = soup.find('tbody')
	return tbody


def test():
	options = Options()
	options.add_argument("--headless")
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option("prefs", prefs)
	driver = webdriver.Chrome(options=options)
	driver.get('https://www.investing.com/indices/vn-30-historical-data')
	return driver


if __name__ == '__main__':
	print('Initialized.')
	client = connect_2_dbServer()
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	# scraper.start_scraping()
	scraper.scrape_historical_data(years=1)
	print('Done.')
