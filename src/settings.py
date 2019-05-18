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
MockColl = 'MockCollection'

# Indice options
Indice_options = {
    'VN 30 (VNI30)': [
        'ACB', 'Advanced Compound Stone JSC',
        'Baoviet Securities Company',
        'Bim Son Cement JSC',
        'CEO Group JSC',
        'Cotec Construction JSC',
        'DANANG HOUSING',
        'DHG Pharmaceutical JSC',
        'Dabaco',
        'Dai Chau JSC',
        'Danang Airport Services JSC',
        'Ducgiang Chemicals Detergent Powder',
        'FPT Corp',
        'Faros Construction',
        'Gemadept Corp',
        'HOANG HA JSC',
        'HUD - TASCO',
        'Ho Chi Minh City Develop',
        'Ho Chi Minh City Infrastructure Inv',
        'Hoa Phat Group JSC'
    ],
    'HNX 30 (HNX30)': ['SHB', 'ACB', 'HUT']
}

# Data path
PROJ_PATH = os.getcwd()
DATA_PATH = PROJ_PATH + '/../Data/'
PLOT_PATH = PROJ_PATH + '/../Plots/'
MODELS_PATH = PROJ_PATH + '/../Models/'

# List of indices
INDICES_LST = ['HNX 30 (HNX30)', 'VN 30 (VNI30)']

# Url header for requests
urlheader = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
