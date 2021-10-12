from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv

import pandas as pd
import requests
from bs4 import BeautifulSoup

with open('geo-data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"', skipinitialspace = True)
    for row in spamreader:
        print(row)

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/Users/lzy/bin/chromedriver')

url = "https://www.eventbrite.com/directory/sitemap/"
driver.get(url)

elements = driver.find_elements_by_css_selector(".panel_head2")
e_groups = [el.find_elements_by_css_selector(".g-group") for el in elements if el.find_element_by_css_selector("h2").text == "United States"]
e_links_nested = [[el.find_elements_by_css_selector(".g-cell") for el in els] for els in e_groups]
e_links = [e.find_element_by_css_selector("a").get_attribute("href") for els in e_links_nested for el in els for e in el]

print(e_links)


# Shuxuan Liu 
def CDCData(stateName):
    url = 'https://data.cdc.gov/resource/9mfq-cb36.json'    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Read data from url into textfile
    fout = open('/Users/liushuxuan/Desktop/Grad School/21Fall/DFP/Final Project/CDCData.txt', 'wt',
                encoding='utf-8')
    fout.write(page.text)
    fout.close()

    # Read data from textfile into dataframe
    df = pd.read_json('/Users/liushuxuan/Desktop/Grad School/21Fall/DFP/Final Project/CDCData.txt')

    # Clean the data and retireve based on state
    # stateName = input("Please enter the state name\n")
    stateData = df.loc[df['state'] == stateName][['submission_date', 'state', 'tot_cases', 'new_case', 
                                                  'tot_death', 'new_death']]
    stateData.submission_date = stateData.submission_date.replace({'T00:00:00.000':''}, regex=True)
    stateData = stateData.sort_values(by=['submission_date'])
    index = pd.Series(range(len(stateData)))
    stateData = stateData.set_index(index)
    
    # Calculate score
    stateData['score'] = stateData.index * (stateData.new_case + abs(stateData.new_death)) / 10000
    score = sum(stateData['score']) / 50
    
    return stateData, score
