# -*- coding: utf-8 -*-
# Project: ForecastingStockPrice_thesis
# Created at: 01:37

import os

__author__ = 'phuongnt18'
__email__ = 'phuongnt18@vng.com.vn'

# time interval in a minute for scraping data
SCRAPING_TIME = 40

# time to sleep while scraping
SLEEP_TIME = 5

# Database host and name
HOST = 'mongodb://localhost:27017/'
DATABASE = 'StockDB'
IndColl = 'indicesCollection'
CompoColl = 'ComponentsCollection'
History_data = 'HistoryData'

# Data path
PROJ_PATH = os.getcwd()
DATA_PATH = PROJ_PATH + '/../Data/'
PLOT_PATH = PROJ_PATH + '/../Plots/'
MODELS_PATH = PROJ_PATH + '/../Models/'

# List of indices
INDICES_LST = ['HNX 30 (HNX30)', 'VN 30 (VNI30)']