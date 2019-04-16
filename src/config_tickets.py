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

# Configure for getting historical data
AJAX_URL = 'https://www.investing.com/instruments/HistoricalDataAjax'
HIS_DATA_HEADERS = [
	{
		'name': 'VN 30',
		'curr_id': '41064',
		'smlID': '2058618',
		'header': 'VN 30 Historical Data',
	},
	{
		'name': 'HNX 30',
		'curr_id': '995072',
		'smlID': '2144064',
		'header': 'HNX 30 Historical Data',
	},
	{
		'name': 'Asia Commercial Bank',
		'curr_id': '41913',
		'smlID': '1286128',
		'header': 'ACB Historical Data',
	},
	{
		'name': 'Advanced Compound Stone JSC',
		'curr_id': '42260',
		'smlID': '1292027',
		'header': 'VCS Historical Data',
	},
	{
		'name': 'Baoviet Securities Company',
		'curr_id': '41942',
		'smlID': '1286621',
		'header': 'BVS Historical Data',
	},
	{
		'name': 'Bim Son Cement',
		'curr_id': '41928',
		'smlID': '1286383',
		'header': 'BCC Historical Data',
	},
	{
		'name': 'DANANG HOUSING',
		'curr_id': '42088',
		'smlID': '1289103',
		'header': 'NDN Historical Data',
	},
	{
		'name': 'Materials Transport Cement JSC',
		'curr_id': '42292',
		'smlID': '1292571',
		'header': 'VTV Historical Data',
	},
	{
		'name': 'Petrovietnam Southern Gas JSC',
		'curr_id': '42109',
		'smlID': '1289460',
		'header': 'PGS Historical Data',
	}
]
