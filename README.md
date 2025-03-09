# BizBuySell Scraper

This repository contains a Python script that scrapes business broker data from BizBuySell’s directory pages and outputs the results to an Excel file. The script is designed to extract each broker’s **Name**, **Phone Number**, **Company**, and **Website**. A sample Excel output is also provided for reference.

---

## Overview

- **Scraper Script (`bizbuysell_scraper.py`):**  
  Rebuilds the BizBuySell scraper from the ground up using up-to-date XPaths to accommodate any recent changes to the BizBuySell website structure.

- **Sample Output (`brokers_sample.xlsx`):**  
  Demonstrates the final Excel format, showing columns for Name, Phone, Company, and Website.

---

## Features

1. **Pagination Support:**  
   Automatically navigates through the BizBuySell directory pages until no more “Next” buttons are found.

2. **Real-Time Data Extraction:**  
   Each broker’s detail page is opened and scraped for name, phone number, company name, and website URL.

3. **Phone Number Reveal:**  
   Clicks the “Show Phone Number” button on each broker profile to access the full phone number.

4. **Threaded / Single-Thread Versions:**  
   Depending on your needs, you can run a single-threaded version or use a multithreaded approach for improved speed.

5. **Robust Error Handling:**  
   If any elements are missing or cannot be clicked, the script logs the error and continues with the next broker.

---

## Requirements

1. **Python 3.7+**  
2. **Selenium**  
3. **pandas**  
4. **openpyxl** (to write Excel files)  
5. **Chrome WebDriver** (must match your installed version of Google Chrome)

Example installation commands:

```bash
pip install selenium pandas openpyxl
