# Author: Ziyuan Liu
# ziyuanl3@andrew.cmu.edu
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from fresh_data import freshWHOData, freshCDCData, get_yt_metadata
from existing_data import existingWHOData, existingCDCData, pre_cr_metadata
import requests
from bs4 import BeautifulSoup
import dateparser
import time
import re
import csv


DRIVER_EXECUTABLE_PATH = '/Users/lzy/bin/chromedriver'

def fresh_country_state_selector():
    print("What region would you like information for?")
    print("   1. United States (More Data Sources)")
    print("   2. International (Only World Health Organization data available)")

    while True:
        try:
            choice = int(input("Enter '1' or '2': "))
            if choice == 1:
                get_fresh_us_data()
                return
            if choice == 2:
                country_code = take_iso3166_input()
                who_df, score = freshWHOData(country_code)
                if who_df is None:
                    return
                display_intl_data(who_df, score, country_code)
                return
        except ValueError:
            print("You must enter '1' or '2'!")

    return

def take_iso3166_input():

    iso_codes = {}
    with open('iso3166.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            iso_codes[row[2]] = row[0]

    print("Please enter the ISO 3166 Alpha-3 Code of the country you would like to look up: ")
    print("Examples of ISO 3166 Alpha-3 Codes (Look up more at https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3):")
    print("    China: CHN")
    print("    France: FRA")
    print("    Russian Federation: RUS")
    print("    United Kingdom of Great Britain and Northern Ireland: GBR")
    print("    United States of America: USA")

    while True:
        choice = input("Enter ISO 3166 Alpha-3 Code")
        if choice in iso_codes:
            print("You have selected: " + choice + " " + iso_codes[choice])
            return choice
        else:
            print("You must enter a valid ISO 3166 Alpha-3 Code!")

def get_fresh_us_data():

    zip_codes = {}
    with open('geo-data.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            zip_codes[row[3]] = (row[4], row[2])

    while True:
        zip_code = int(input("Enter your query zip code: "))
        if str(zip_code) in zip_codes:
            print("Retrieving data... (this may take a few moments)")
            break
        else:
            print("That was not a valid zip code! Please enter a valid US zip code.")

    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_EXECUTABLE_PATH)

    url = "https://www.eventbrite.com/"
    driver.get(url)

    inputElement = driver.find_element_by_id("locationPicker")
    inputElement.send_keys(zip_code)
    inputElement.send_keys(Keys.ENTER)

    eventsExist = True

    try:
        if "No events in your area" in driver.find_element_by_css_selector(".eds-text-bl h3").text:
            eventsExist = False
    except:
        time.sleep(2)

    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    if eventsExist:
        seeMoreElement = driver.find_element_by_css_selector("[data-testid=see-more-events]")
        allEventLink = seeMoreElement.find_element_by_css_selector("a").get_attribute("href")
        driver.close()
        events, city, state = get_eventbrite_list_data(allEventLink, allEventLink, zip_code)
        # event_csv_lines = [event[0].replace(",", "") + "," + str(event[2]) + "," + str(event[3]) + "," + str(event[4]) for event in events]

        events = [[event[0], event[2], event[3]] for event in events]
        cdc_df, cdc_score = freshCDCData(state)
        yt_df, yt_score = get_yt_metadata(city)
        eb_df = pd.DataFrame(events, columns = ['EventName', 'EventTime', 'EventPopularity'])
        eb_score = sum(event[2] for event in events) / len(events)
        display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score)
    else:
        city, state = zip_codes[zip_code][0], zip_codes[zip_code][1]
        cdc_df, cdc_score = freshCDCData(state)
        yt_df, yt_score = get_yt_metadata(city)
        eb_df = pd.DataFrame(columns = ['EventName', 'EventTime', 'EventPopularity'])
        eb_score = 0
        display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score)


    return

def get_existing_data():
    print("Please select a zip code: ")
    print("   1. 15213 (Pittsburgh PA)")
    print("   2. 97203 (Portland OR)")
    print("   3. 63105 (St. Louis MO)")
    print("   4. International Location")
    print("")
    while True:
        try:
            choice = int(input("Enter '1', '2', '3' or '4': "))
            if choice == 1:
                zip_code = 15213
                cdc_df, cdc_score = existingCDCData(choice)
                yt_df, yt_score = pre_cr_metadata(choice)
                eb_df, eb_score = existing_eb_data(zip_code)
                display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score)
                break
            if choice == 2:
                zip_code = 97203
                cdc_df, cdc_score = existingCDCData(choice)
                yt_df, yt_score = pre_cr_metadata(choice)
                eb_df, eb_score = existing_eb_data(zip_code)
                display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score)
                break
            if choice == 3:
                zip_code = 63105
                cdc_df, cdc_score = existingCDCData(choice)
                yt_df, yt_score = pre_cr_metadata(choice)
                eb_df, eb_score = existing_eb_data(zip_code)
                display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score)
                break
            if choice == 4:
                country_code = take_iso3166_input()
                whodf, score = existingWHOData(country_code)
                display_intl_data(whodf, score, country_code)
                return
        except ValueError:
            print("You must enter '1', '2', '3' or '4'!")

    return

def existing_eb_data(zip_code):
    filename = "eventbrite-" + str(zip_code) + ".csv"
    eb_data = []
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            eb_data.append([row[0], row[1], int(row[2])])
    eb_df = pd.DataFrame(eb_data, columns=['EventName', 'EventTime', 'EventPopularity'])
    eb_score = sum(ebd[2] for ebd in eb_data) / len(eb_data)
    return eb_df, eb_score

def display_us_data(cdc_df, cdc_score, yt_df, yt_score, eb_df, eb_score):
    print("Would you like to see the detailed dataframe of data from the following sources?")
    print("    1. CDC")
    print("    2. Youtube")
    print("    3. EventBrite")
    print("    4. No thanks, send me straight to the evaluation")

    while True:
        try:
            choice = int(input("Enter '1', '2', '3' or '4': "))
            if choice == 1:
                print(cdc_df)
                print("Would you like to view any other dataframe?")
            if choice == 2:
                print(yt_df)
                print("Would you like to view any other dataframe?")
            if choice == 3:
                print(eb_df)
                print("Would you like to view any other dataframe?")
            if choice == 4:
                break
        except ValueError:
            print("You must enter '1', '2', '3' or '4'!")

    print("The disease transmission score is " + str(cdc_score))
    print("The media attention score is " + str(yt_score))
    print("The social gathering score is " + str(eb_score))
    return

def display_intl_data(who_df, score, country_code):
    print("Would you like to see the detailed dataframe of WHO data for " + country_code + "?")
    print("    1. Yes")
    print("    2. No")

    while True:
        try:
            choice = int(input("Enter '1' or '2': "))
            if choice == 1:
                print(who_df)
                break
            if choice == 2:
                break
        except ValueError:
            print("You must enter '1' or '2'!")

    print("For " + country_code+ ", the risk score is currently " + str(score))
    return

def get_eventbrite_list_data(eventListLink, base_url, zip_code):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")

    events = []

    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_EXECUTABLE_PATH)

    driver.get(eventListLink)
    time.sleep(5)

    titleText = driver.title
    titleAry = titleText.split(", ")
    city, state = titleAry[0], titleAry[1][0:2]

    contentDiv = driver.find_element_by_css_selector(".search-main-content")
    listElements = contentDiv.find_elements_by_css_selector("li")

    for le in listElements:
        title = ""
        followCount = ""
        parsed_date = ""
        try:
            title = le.find_element_by_css_selector(".eds-event-card__formatted-name--is-clamped").text
            eventLink = le.find_element_by_css_selector("a").get_attribute("href")
            eventTime = le.find_element_by_css_selector(".eds-event-card-content__sub-title").text
            pat = r'\+'
            if re.search(pat, eventTime)!= None:
                eventTime = eventTime.split("+")[0]
            # print(eventTime)
            parsed_date = dateparser.parse(eventTime)
            pat = r'k'
            followCount = 0
            followCountText = le.find_element_by_css_selector(".eds-event-card__sub-content--signal").text.replace(" followers", "")
            if re.search(pat, followCountText) != None:
                followCount = int(float(followCountText.replace("k", "")) * 1000)
            else:
                followCount = int(followCountText)
        except NoSuchElementException:
            pass

        # print(title, eventLink, parsed_date, followCount)
        events.append([title, eventLink, parsed_date, followCount, zip_code])

    paginationText = driver.find_element_by_css_selector(".eds-pagination__navigation-minimal").text
    paginationArray = paginationText.split(" of ")

    if int(paginationArray[0]) < 3:
        if (int(paginationArray[0]) + 1) <= int(paginationArray[1]):
            next_url = base_url + "?page=" + str(int(paginationArray[0]) + 1)
            driver.close()
            return events + get_eventbrite_list_data(next_url, base_url, zip_code)[0], city, state
        else:
            driver.close()
            return events, city, state
    else:
        driver.close()
        return events, city, state

print("Pandemrisk v1.0.0")
print("COVID-19 Risk Assessment Toolkit")
print("Copyright © 2021 Pandemrisk Team")
print("""ATTENTION! ALL RISK ASSESSMENT SCORES IN PANDEMRISK TO BE
      INTERPRETED ACCORDING TO DIRECTIONS IN MANUAL (README FILE)""")
print("Please select a data source: ")
print("   1. Use Pre-crawled Data (Limited Locations Available)")
print("   2. Retrieve Fresh Data (Might take a while)")
print("")

while True:
    try:
        choice = int(input("Enter '1' or '2': "))
        if choice == 1:
            get_existing_data()
            break
        if choice == 2:
            fresh_country_state_selector()
            break
    except ValueError:
        print("You must enter '1' or '2'!")
