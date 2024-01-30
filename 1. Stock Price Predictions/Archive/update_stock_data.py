# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:17:49 2023

@author: mball3
"""

# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import glob
import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

base_path = r'C:\Users\mball3\OneDrive - KPMG\Documents\Investment_Analysis\data'

# This returns all folders in the base_path
# return the folder, in the base path, if it is a folder
# And only return folders of length 10 containins two underscores 
folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))
           and len(folder) == 10 and folder.count('_') == 2
          ]

# Find latest folder in the path
latest_folder = max(folders, key=lambda x: datetime.strptime(x,'%d_%m_%Y'))

# Create new full path to the most recent folder
latest_path = os.path.join(base_path, latest_folder)

# Retrieve the file names
filenames = glob.glob(latest_path+"/*.csv")

# This specifies to the url below, which devices that url can be accessed from
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}


for filename in filenames:
    ############################################
    # Read in the historical data for each stock 
    historical_data = pd.read_csv(filename)
    stock = filename.split("\\")[-1].split('.')[0]
    
    # Convert date to date format - english 
    historical_data['Date'] = pd.to_datetime(historical_data['Date'])
    
    ############################################
    # Read in the new data
    ############################################
    
    # Set the URL to the current stock's prices
    url = (f"https://finance.yahoo.com/quote/{stock}/history?p={stock}")
    r = requests.get(url, verify=False, headers=headers)

    # This div class contains all the information I need on hisorical stock price data
    web_content = BeautifulSoup(r.text, 'lxml')
    web_content = web_content.find('div', class_='Pb(10px) Ovx(a) W(100%)')

    # within the div class there is a tbody 
    tbody = web_content.find("tbody")

    # each tr is a row within the tbody, which contains information for every date
    rows = tbody.find_all("tr")

    # Define the headers and create an empty dictionary to fill
    data_headers = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    data_dict = {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'Adj Close': [], 'Volume': []}

    # This gets every row from tbody - ignoring the top row as they are headers
    for row in rows:
        data_row = []
        # Each td is a different value within that row
        for cell in row.find_all("td"):
            # Strip removes unwanted info
            row_data = cell.text.strip()
            # Store this for this row 
            data_row.append(row_data)

        # This then zips together the data with the header
        # Which then populates the dictionary, ensuring that the data goes into the correct place
        for header, value in zip(data_headers, data_row):
            if len(data_row) == 7:
                data_dict[header].append(value)

            continue 


    # Convert to date
    scraped_data = pd.DataFrame(data_dict)
    scraped_data['Date'] = pd.to_datetime(scraped_data['Date'])
    
    # Add new data to the end of historical data
    new_data = scraped_data[scraped_data['Date'] > max(historical_data['Date'])]
    full_data = pd.concat([historical_data,new_data], axis=0)
    
    # Change data types
    full_data['Volume'] = full_data['Volume'].replace(',', '', regex=True)
    full_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = full_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].apply(pd.to_numeric, errors='coerce')
 
    ############################################
    # Now save this file in a folder with todays date
    ############################################
    latest_date = datetime.now() - timedelta(days=1)
    latest_date = latest_date.strftime('%d_%m_%Y')
    folder_path = os.path.join('C:\\Users\\mball3\\OneDrive - KPMG\\Documents\\Investment_Analysis\\data', latest_date)
    os.makedirs(folder_path, exist_ok=True)
    
    final_file_path = os.path.join(folder_path, f'{stock}.csv')
    full_data.to_csv(final_file_path, index=False)