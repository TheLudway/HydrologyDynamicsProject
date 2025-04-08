#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import csv

# Fetch the page
url = 'https://niveles.cormagdalena.gov.co/'
response = requests.get(url)
response.raise_for_status()

# Parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find divs with the relevant classes
data_divs = soup.find_all('div', class_=lambda x: x and 'color' in x)

# Regex to match date and value
pattern = re.compile(r'([A-Za-z]{3}/\d{2}/\d{2})\s*[-–>]+\s*([\d.]+)')

# Open CSV file to write
with open('../Data/Levels/niveles.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Date', 'Value'])  # Header

    for div in data_divs:
        text = div.get_text(strip=True)
        match = pattern.search(text)
        if match:
            date, value = match.groups()
            writer.writerow([date, value])
            print(f"Saved: {date}, {value}")


