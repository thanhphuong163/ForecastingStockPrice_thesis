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


if __name__ == '__main__':
	print('Initialized.')
	client = connect_2_dbServer()
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, dbClient=client, verbose=True)
	scraper.start_scraping()
# scraper.scraping()
# client = connect_2_dbServer()
# db = client.get_database(DATABASE)
# coll1 = db.get_collection(IndColl)
