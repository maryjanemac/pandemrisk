from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import csv

def get_fresh_data():

    zip_code = int(input("Enter your query zip code: "))
    print("Retrieving data... (this may take a few moments)")

    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options, executable_path='/Users/lzy/bin/chromedriver')

    url = "https://www.eventbrite.com/"
    driver.get(url)

    inputElement = driver.find_element_by_id("locationPicker")
    inputElement.send_keys(zip_code)
    inputElement.send_keys(Keys.ENTER)

    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 1080)")
    time.sleep(2)

    seeMoreElement = driver.find_element_by_css_selector("[data-testid=see-more-events]")
    print(seeMoreElement.get_attribute("innerHTML"))
    allEventLink = seeMoreElement.find_element_by_css_selector("a").get_attribute("href")
    driver.get(allEventLink)



print("Pandemrisk v1.0.0")
print("COVID-19 Risk Assessment Toolkit")
print("Copyright © 2021 Pandemrisk Team")
print("Please select a data source: ")
print("   1. Use Pre-crawled Data (Limited Locations Available)")
print("   2. Retrieve Fresh Data (Might take a while)")
print("")

while True:
    try:
        choice = int(input("Enter '1' or '2': "))
        if choice == 1:
            break
        if choice == 2:
            get_fresh_data()
            break
    except ValueError:
        print("You must enter '1' or '2'!")