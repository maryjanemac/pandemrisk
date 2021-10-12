from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv

from googlesearch import search
from googleapiclient.discovery import build
import json
import numpy as np
import datetime as dtm
from statistics import mean

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

from numpy import NaN
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd


def WHOData(countryName):
    url = 'https://covid.ourworldindata.org/data/owid-covid-data.json'    
    response = urlopen(url)
    df = pd.read_json(url)
    df = df.transpose()
    index = pd.Series(range(len(df)))
    df = df.set_index(index)

    countryData = {'location':[],'date':[],'new_cases':[],'new_deaths':[], \
            'people_vaccinated':[],'population_density':[]}
    for d in df.loc[df['location'] == countryName]['data'][0]:
        countryData['location'].append(countryName)
        countryData['date'].append(d['date'])
        if 'new_cases' in d.keys():
            countryData['new_cases'].append(d['new_cases'])
        else:
            countryData['new_cases'].append(NaN)
        if 'new_deaths' in d.keys():
            countryData['new_deaths'].append(d['new_deaths'])
        else:
            countryData['new_deaths'].append(NaN)
        if 'people_vaccinated' in d.keys():
            countryData['people_vaccinated'].append(d['people_vaccinated'])
        else:
            countryData['people_vaccinated'].append(NaN)
        if 'population_density' in d.keys():
            countryData['population_density'].append(d['population_density'])
        else:
            countryData['population_density'].append(NaN) 
    countryData = pd.DataFrame(countryData)
    # print(countryData)

    # calculate the score
    score = 0
    df_score = countryData.copy()
    df_score = df_score.fillna(0)
    df_score['score'] = df_score.index * (df_score.new_cases + df_score.new_deaths + df_score.people_vaccinated + df_score.population_density) / 10000
    score = sum(df_score['score']) / 100000

    return countryData, score

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

def get_yt_metadata(city_str):
    query = 'youtube covid-19 ' + city_str
    URL_list = [] 
    for i in search(query, tld = 'com', num=20, stop=20, pause=2):
        if i[0:32] == 'https://www.youtube.com/watch?v=':   
            URL_list.append(i) 
    print(URL_list)
    
    #Gets the video ids from the URLs
    id_list = []
    for i in URL_list:
        i = i + '&'
        id_str = ''
        j = 0
        isurl = False
        while i[j] != '&':
            if isurl == True:
                id_str = id_str + i[j]
            if i[j] == '=':
                isurl = True
            j = j + 1
        id_list.append(id_str)  
    
    api_key = 'AIzaSyDKzsR_tYoiiT6cvjfNoM7DlDR-0vFnM-g'
    service = build('youtube', 'v3', developerKey = api_key) 
    fout = open('/Users/queen/OneDrive/url.json', 'wt', encoding = 'utf-8')
    
    #Creates an empty data frame that will be populated with info from APIs
    yt_data_df = pd.DataFrame(np.nan, index=[i for i in range(len(URL_list))], columns=['URL','Video Title', 'Channel Title', 'Views', 'Likes', 'Dislikes', 'Comments', 'Date', 'Duration', 'Definition', 'Captions', 'Licensed Content'])
    yt_data_df['URL'] = [i for i in URL_list] 
    
    #Creates list that will be used for timestamps later
    datetime_str_list = []
    
    row_num = 0
    for i in id_list:
        request = service.videos().list(part = 'statistics',id=i) 
        response = request.execute()
        json.dump(response, fout)
        try:
            yt_data_df.loc[row_num, 'Views'] = response['items'][0]['statistics']['viewCount'] 
        except:
            yt_data_df.loc[row_num, 'Views'] = 0
        try:
            yt_data_df.loc[row_num, 'Likes'] = response['items'][0]['statistics']['likeCount'] 
        except:
            yt_data_df.loc[row_num, 'Likes'] = 0
        try:
            yt_data_df.loc[row_num, 'Dislikes'] = response['items'][0]['statistics']['dislikeCount'] 
        except:
            yt_data_df.loc[row_num, 'Dislikes'] = 0
        try:
            yt_data_df.loc[row_num, 'Comments'] = response['items'][0]['statistics']['commentCount'] 
        except:
            yt_data_df.loc[row_num, 'Comments'] = 0
        request = service.videos().list(part = 'contentDetails',id=i) 
        response = request.execute()
        json.dump(response, fout)
        duration_str = response['items'][0]['contentDetails']['duration']
        duration_str = duration_str.replace('PT', '')
        duration_str = duration_str.replace('H', ' hours ')
        duration_str = duration_str.replace('M', ' minutes ')
        duration_str = duration_str.replace('S', ' seconds')
        yt_data_df.loc[row_num, 'Duration'] = duration_str
        yt_data_df.loc[row_num, 'Definition'] = response['items'][0]['contentDetails']['definition'] 
        if response['items'][0]['contentDetails']['caption'] == 'true':
            yt_data_df.loc[row_num, 'Captions'] = 'Yes' 
        else:
            yt_data_df.loc[row_num, 'Captions'] = 'No'
        if response['items'][0]['contentDetails']['licensedContent'] == 'true':
            yt_data_df.loc[row_num, 'Licensed Content'] = 'Yes' 
        else:
            yt_data_df.loc[row_num, 'Licensed Content'] = 'No'
        request = service.videos().list(part = 'snippet',id=i) 
        response = request.execute()
        json.dump(response, fout)
        yt_data_df.loc[row_num, 'Date'] = (response['items'][0]['snippet']['publishedAt'])[0:10]
        vid_datetime = (response['items'][0]['snippet']['publishedAt'])[0:10] + ' ' + (response['items'][0]['snippet']['publishedAt'])[11:18]
        datetime_str_list.append(vid_datetime)
        yt_data_df.loc[row_num, 'Video Title'] = response['items'][0]['snippet']['title'] 
        yt_data_df.loc[row_num, 'Channel Title'] = response['items'][0]['snippet']['channelTitle'] 
        row_num = row_num + 1
    fout.close()
    
    yt_data_df = yt_data_df.set_index('URL')
    
    datetime_list = []
    timestamp_list = []
    format = '%Y-%m-%d %H:%M:%S'
    for i in datetime_str_list:
        #dt = i
        datetime_list.append(dtm.datetime.strptime(i, format))
    for i in datetime_list:
        timestamp_list.append(int(round(i.timestamp())))
    avg_ts = mean(timestamp_list) 
    ct = dtm.datetime.now()
    c_ts = int(round(ct.timestamp()))
    diff = c_ts - avg_ts 
    
    if diff <= 259200: #three days
        score = 5
    elif 259200 < diff <= 604800: #3-7 days
        score = 4
    elif 604800 < diff <= 1209600: #7-14 days
        score = 3
    elif 1209600 < diff <= 5184000: #2 weeks to 60 days
        score = 2
    elif 5184000 < diff <= 10368000: #60 to 120 days
        score = 1
    else:
        score = 0
    return yt_data_df, score
