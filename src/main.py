# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:56

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
	client = connect_2_dbServer()
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	scraper.scrape_historical_data(years=3)


def test():
	options = Options()
	options.add_argument("--headless")
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option("prefs", prefs)
	driver = webdriver.Chrome(options=options)
	driver.get('https://www.investing.com/indices/vn-30-historical-data')
	return driver


if __name__ == '__main__':
	# start = datetime.today() - relativedelta(months=4)
	# end = datetime.today()
	# print('Initialized.')
	# client = connect_2_dbServer()
	# # driver_lst = request_2_website()
	# # scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	# # # scraper.start_scraping()
	# # scraper.scrape_historical_data(years=2)
	# # print('Done.')
	# query_data = QueryData(dbClient=client)
	# lst_symbol = query_data.get_list_ticket()
	# print(lst_symbol)
	get_historical_data()
