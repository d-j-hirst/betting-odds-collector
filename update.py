import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
driver = webdriver.Chrome('chromedriver', options=options)
driver.get("https://www.sportsbet.com.au/betting/politics/australian-federal-politics/next-federal-election-nsw-seats-5878289")

num_main_markets = len(driver.find_elements(By.CLASS_NAME,
                                            'panelDesktop_f1c7wtv3'
                                           ))
other_markets = driver.find_element(By.CLASS_NAME, 'headerDesktop_ft0eijx')
driver.execute_script("arguments[0].click();", other_markets)
time.sleep(2)  # Wait for other markets to load
data_areas = driver.find_elements(By.CLASS_NAME, 'panelDesktop_f1c7wtv3')
for data_area in data_areas[num_main_markets:]:
    print(f'clicking data area: {data_area.text}')
    data_area.click()
    time.sleep(0.5)  # Workaround for issue where elements don't click properly
for data_area in data_areas:
    title_element = data_area.find_element(By.CLASS_NAME, 'size14_f7opyze')
    print(title_element.text)
    outcomes = data_area.find_elements(By.CLASS_NAME, 'outcomeContainer_f1wc7xgg')
    if len(outcomes) == 0:
        time.sleep(2)
        data_area.click()
        time.sleep(2)
        outcomes = data_area.find_elements(By.CLASS_NAME, 'outcomeContainer_f1wc7xgg')
    for outcome in outcomes:
        party = outcome.find_element(By.CLASS_NAME, 'outcomeName_f19a8l1b')
        print(f'  {party.text}')
        price = outcome.find_element(By.CLASS_NAME, 'priceTextSize_frw9zm9')
        print(f'  {price.text}')
driver.close()