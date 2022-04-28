import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

try:
    with open('previous.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

changes = []

urls = {
    'NSW': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-nsw-seats-6484922',
    'VIC': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-vic-seats-6495711',
    'QLD': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-qld-seats-6496304',
    'WA': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-wa-seats-6496079',
    'SA': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-sa-seats-6494014',
    'TAS': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-tas-seats-6484714',
    'ACT': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-act-seats-6484557',
    'NT': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-nt-seats-6484664',
}

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
driver = webdriver.Chrome('chromedriver', options=options)

for region, url in urls.items():
    print(f"Loading webpage for {region} ...")
    driver.get(url)

    num_main_markets = len(driver.find_elements(By.CLASS_NAME,
                                                'panelDesktop_f1c7wtv3'
                                            ))
    try:
        other_markets = driver.find_element(By.CLASS_NAME, 'headerDesktop_ft0eijx')
        driver.execute_script("arguments[0].click();", other_markets)
        time.sleep(2)  # Wait for other markets to load
    except NoSuchElementException:
        pass
    data_areas = driver.find_elements(By.CLASS_NAME, 'panelDesktop_f1c7wtv3')
    for data_area in data_areas[num_main_markets:]:
        data_area.click()
        time.sleep(0.5)  # Workaround for issue where elements don't click properly
    for data_area in data_areas:
        title_element = data_area.find_element(By.CLASS_NAME, 'size14_f7opyze')
        seat_name = title_element.text.split(" (")[0]
        outcomes = data_area.find_elements(By.CLASS_NAME, 'outcomeContainer_f1wc7xgg')
        if len(outcomes) == 0:
            time.sleep(2)
            data_area.click()
            time.sleep(2)
            outcomes = data_area.find_elements(By.CLASS_NAME, 'outcomeContainer_f1wc7xgg')
        for outcome in outcomes:
            party = outcome.find_element(By.CLASS_NAME, 'outcomeName_f19a8l1b').text
            price = outcome.find_element(By.CLASS_NAME, 'priceTextSize_frw9zm9').text
            if seat_name in data and party in data[seat_name]:
                old_price = data[seat_name][party]
                if old_price != price:
                    changes.append(f'Seat {seat_name}: {party} now at price {price} (changed from {old_price})')
                    data[seat_name][party] = price
            else:
                changes.append(f'Seat {seat_name}: new entry {party} at price {price}')
                if seat_name not in data:
                    data[seat_name] = {}
                data[seat_name][party] = price
driver.close()

with open('updates.txt', 'w') as f:
    for change in changes:
        print(change)
        f.write(change)

with open('previous.json', 'w') as f:
    json.dump(data, f)