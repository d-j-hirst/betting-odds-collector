import requests
import time
import json
import datetime
import environ
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

import environ

env = environ.Env(
    DEBUG=(int, 0)
)

# reading .env file
environ.Env.read_env('.env')

try:
    with open('previous_sb.json', 'r') as f:
        sb_data = json.load(f)
except FileNotFoundError:
    sb_data = {}

try:
    with open('previous_tab.json', 'r') as f:
        tab_data = json.load(f)
except FileNotFoundError:
    tab_data = {}


sb_changes = []
tab_changes = []

# urls = {
#     'NSW': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-nsw-seats-6484922',
#     'VIC': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-vic-seats-6495711',
#     'QLD': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-qld-seats-6496304',
#     'WA': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-wa-seats-6496079',
#     'SA': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-sa-seats-6494014',
#     'TAS': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-tas-seats-6484714',
#     'ACT': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-act-seats-6484557',
#     'NT': 'https://www.sportsbet.com.au/betting/politics/australian-federal-politics/electorate-betting-nt-seats-6484664',
# }

# Important: when changing election URL also make sure to rename previous.json so that
# the new results don't get mixed up with old ones
urls = {
    'all': 'https://www.sportsbet.com.au/betting/politics/nsw-politics/nsw-election-electorate-betting-7155024'
}

tab_url = 'https://www.tab.com.au/sports/betting/Politics/competitions/NSW%20Politics'

print('Loading data from web ...')

options = Options()
options.add_argument('headless')
options.add_argument("no-sandbox")
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# This assumes running Linux/wsl2 and you have installed chromedriver
# according to instructions here:
# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
webdriver_service = Service(f"/home/{env.str('USERNAME')}/chromedriver/stable/chromedriver")
driver = webdriver.Chrome(service=webdriver_service, options=options)


# TAB site
driver.get(tab_url)
elements = driver.find_elements(By.CLASS_NAME, 'template-title')
for element in elements:
    if element.text == 'Seat Winner':
        element.click()
elements = driver.find_elements(By.CLASS_NAME, 'market-propositions')
for element in elements:
    text = element.text
    if 'SeatW' in element.text:
        seatWnPos = text.find('SeatW')
        lines = [a.strip().replace(' (','(') for a in text.split('\n')][1:]
        seat_name = (lines[0].split('(')[1]).split(')')[0]
        # Messed-up formatting with Winston Hills in 2023nsw, can't be bothered
        # accomodating it as there is no 3rd-party here, so just skip
        if seat_name == 'Coalition': continue
        parties = [a.split('(')[0] for a in lines if '(' in a]
        prices = [a for a in lines if '(' not in a]
        for party, price in zip(parties, prices):
            if seat_name in tab_data and party in tab_data[seat_name]:
                old_price = tab_data[seat_name][party]
                if old_price != price:
                    tab_changes.append(f'Seat {seat_name}: {party} now at price {price} (changed from {old_price})')
                    tab_data[seat_name][party] = price
            else:
                tab_changes.append(f'Seat {seat_name}: new entry {party} at price {price}')
                if seat_name not in tab_data:
                    tab_data[seat_name] = {}
                tab_data[seat_name][party] = price



for region, url in urls.items():
    if (len(urls) > 1): print(f"Loading webpage for {region} ...")
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
            if seat_name in sb_data and party in sb_data[seat_name]:
                old_price = sb_data[seat_name][party]
                if old_price != price:
                    sb_changes.append(f'Seat {seat_name}: {party} now at price {price} (changed from {old_price})')
                    sb_data[seat_name][party] = price
            else:
                sb_changes.append(f'Seat {seat_name}: new entry {party} at price {price}')
                if seat_name not in sb_data:
                    sb_data[seat_name] = {}
                sb_data[seat_name][party] = price
driver.close()

with open('updates.txt', 'w') as f:
    print('TAB')
    f.write('TAB\n')
    for change in tab_changes:
        print(change)
        f.write(change)
    print('Sportsbet')
    f.write('Sportsbet\n')
    for change in sb_changes:
        print(change)
        f.write(change)

now = datetime.datetime.now()

sb_archive_name = (f'Update Archives/update_archive_sb_{now.year}-{now.month}'
                f'-{now.day}-{now.hour}-{now.minute}-{now.second}.dat')

tab_archive_name = (f'Update Archives/update_archive_tab_{now.year}-{now.month}'
                f'-{now.day}-{now.hour}-{now.minute}-{now.second}.dat')

with open(sb_archive_name, 'w') as f:
    for seat_name, seat_data in sb_data.items():
        f.write(f'#{seat_name}\n')
        for party_name, party_odds in seat_data.items():
            f.write(f'{party_name},{party_odds}\n')

with open(tab_archive_name, 'w') as f:
    for seat_name, seat_data in tab_data.items():
        f.write(f'#{seat_name}\n')
        for party_name, party_odds in seat_data.items():
            f.write(f'{party_name},{party_odds}\n')

with open('previous_tab.json', 'w') as f:
    json.dump(tab_data, f)

with open('previous_sb.json', 'w') as f:
    json.dump(sb_data, f)

def interpret_odds(odds):
    try:
        return float(odds)
    except ValueError:
        return 1000.0

party_leading = {}
data_items = [a for a in sb_data.items() if a[0] != '']
for seat_name, seat_data in data_items:
    seat_data = [a for a in seat_data.items() if a[0] != '']
    best_party, odds = min(seat_data, key=lambda x: interpret_odds(x[1]))
    if best_party == "|Coalition": best_party = "Coalition"
    if sum(a[1] == odds for a in seat_data) > 1:
        best_party = 'Tie between ' + ', '.join(a[0] for a in seat_data if a[1] == odds)
    if best_party not in party_leading:
        party_leading[best_party] = 0
    party_leading[best_party] += 1

for party, count in party_leading.items():
    print (f'{party}: {count} seats')