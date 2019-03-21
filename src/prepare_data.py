# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 21:30
from datetime import datetime

import numpy as np
import pandas as pd

from src.settings import DATA_PATH

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

data = pd.read_csv(DATA_PATH + 'VN 30 Historical Data.csv')


def convert_price(str_value):
	tmp = str_value.replace(',', '')
	return np.float(tmp)


def convert_date(str_date):
	date_fmt = '%b %d, %Y'
	return datetime.strptime(str_date, date_fmt)


if __name__ == '__main__':
	df = pd.DataFrame()
	df['date'] = data['Date'].apply(lambda x: convert_date(x))
	df['price'] = data['Price'].apply(lambda x: convert_price(x))
	df.set_index(['date'])
	df.to_csv(DATA_PATH + 'vni30.csv')
	print(df.head(10))
