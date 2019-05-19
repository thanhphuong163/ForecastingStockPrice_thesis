# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:56
from datetime import datetime

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config_tickets import ticket_lst
from src.query_data import QueryData
from src.scraping import WebScraping
from src.settings import HOST
from src.utilities import run_model

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
	mongo_client = MongoClient(HOST)
	return mongo_client


def get_historical_data():
	client = connect_2_dbServer()
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	scraper.scrape_historical_data(years=5)


def demo():
	start = datetime(2010, 1, 1)
	client = connect_2_dbServer()
	index = 'VNI30'
	query = QueryData(dbClient=client)
	df_ticket = query.get_list_ticket(index)
	lst_ticket = list(df_ticket['name'][:5])
	print(lst_ticket)
	df = query.get_historical_data(lst_ticket)

	# closed_price = pd.DataFrame()
	for ticket in lst_ticket:
		# closed_price[ticket] = df[df.name == ticket]['close']
		print(ticket)
		time_series = df[df.name == ticket]['close']
		run_model(time_series)


# print(closed_price)


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
	# get_historical_data()
	demo()
