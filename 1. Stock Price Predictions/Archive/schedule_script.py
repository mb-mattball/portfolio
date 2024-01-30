# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:15:43 2023

@author: mball3
"""

import schedule
import time
import subprocess

def my_job():
    # Replace 'your_script.py' with the path to your Python script
    subprocess.run(["python", "C:\\Users\\mball3\\OneDrive - KPMG\\Documents\\Investment_Analysis\\code\\update_stock_data.py"])

# Set the interval in days
interval_days = 2

# Schedule the job to run every n days
schedule.every(interval_days).days.do(my_job)

while True:
    schedule.run_pending()
    time.sleep(1)
