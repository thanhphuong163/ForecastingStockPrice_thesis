# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 22:09

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

ticket_lst = [
	{
		'ticket': 'VNI30',
		'url': 'https://www.investing.com/indices/vn-30-components',
	},
	{
		'ticket': 'HNX30',
		'url': 'https://www.investing.com/indices/hnx-30-components',
	},
]

# real-time data header xpath
REAL_TIME_HEADER_XPATH = [
	{
		'header': 'name',
		'xpath': '//*[@id="leftColumn"]/div[1]/h1',
	},
	{
		'header': 'last',
		'xpath': '//*[@id="last_last"]',
	},
	{
		'header': 'change',
		'xpath': '//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[2]',
	},
	{
		'header': 'change_per',
		'xpath': '//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[4]',
	},
	{
		'header': 'volume',
		'xpath': '//*[@id="quotes_summary_secondary_data"]/div/ul/li[1]/span[2]/span',
	},
	{
		'header': 'open',
		'xpath': '//*[@id="quotes_summary_secondary_data"]/div/ul/li[2]/span[2]',
	},
	{
		'header': 'day_range',
		'xpath': '//*[@id="quotes_summary_secondary_data"]/div/ul/li[3]/span[2]',
	},
]

tbody = '//*[@id="cr1"]/tbody'
COMPONENT_HEADER_DATA = [
	{
		'header': 'name',
		'xpath': tbody + '/tr/td[2]/a',
	},
	{
		'header': 'last',
		'xpath': tbody + '/tr/td[3]',
	},
	{
		'header': 'high',
		'xpath': tbody + '/tr/td[4]',
	},
	{
		'header': 'low',
		'xpath': tbody + '/tr/td[5]',
	},
	{
		'header': 'change',
		'xpath': tbody + '/tr/td[6]',
	},
	{
		'header': 'change_per',
		'xpath': tbody + '/tr/td[7]',
	},
	{
		'header': 'volume',
		'xpath': tbody + '/tr/td[8]',
	},
]
