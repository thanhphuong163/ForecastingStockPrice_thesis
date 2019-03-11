# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:56
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config_tickets import ticket_lst
from src.scraping import WebScraping

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'


def request_2_website():
	options = Options()
	options.add_argument("--headless")
	prefs = {"profile.managed_default_content_settings.images": 2}
	options.add_experimental_option("prefs", prefs)
	driver_lst = []
	print('Requesting...')
	for ticket in ticket_lst:
		driver = webdriver.Chrome(options=options)
		driver.get(ticket['url'])
		driver_lst.append(driver)
	return driver_lst


if __name__ == '__main__':
	print('Initialized.')
	driver_lst = request_2_website()
	scraper = WebScraping(driver_lst=driver_lst, verbose=True)
	scraper.scraping()
# drivers = request_2_website()
# driver = drivers[0]
# tr_lst = '//*[@id="cr1"]/tbody/tr'
# tr_element_lst = WebDriverWait(driver, 10).until(lambda df: driver.find_elements_by_xpath(tr_lst))
# print(tr_element_lst[2].text)
# driver_ = webdriver.Chrome()
