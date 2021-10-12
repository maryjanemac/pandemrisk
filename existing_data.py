from numpy import NaN
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd
import os
import sys


def WHOData(countryName):
    url = 'https://covid.ourworldindata.org/data/owid-covid-data.json'    
    response = urlopen(url)
    # data = json.loads(response.read())
    df = pd.read_json(url)
    df = df.transpose()
    df['country_code'] = df.index
    index = pd.Series(range(len(df)))
    df = df.set_index(index)

    countryData = {'code':[], 'location':[],'date':[],'new_cases':[],'new_deaths':[], \
            'people_vaccinated':[],'population_density':[]}

    for d in df.loc[df['country_code'] == countryName]['data'][0]:
        countryData['code'].append(countryName)
        countryData['location'].append(df.loc[df['country_code'] == countryName]['location'][0])
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

def existingCDCData(choice):
    
    if choice == 1:
        stateName = 'PA'
    elif choice == 2:
        stateName = 'OR'
    elif choice == 3:
        stateName = 'MO'
        
    # Read data from file into dataframe
    df = pd.read_csv('United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv')
    
    df.submission_date = df.submission_date.replace({'T00:00:00.000':''}, regex=True)
    
    # Clean the data and retireve based on state
    stateData = df.loc[df['state'] == stateName][['submission_date', 'state', 'tot_cases', 'new_case', 
                                                  'tot_death', 'new_death']]
    stateData = stateData.sort_values(by=['submission_date'])
    index = pd.Series(range(len(stateData)))
    stateData = stateData.set_index(index)
    stateData['score'] = stateData.index * (stateData.new_case + abs(stateData.new_death)) / 10000
    
    score = sum(stateData['score']) / 50
    
    return stateData[['submission_date', 'state', 'tot_cases', 'new_case', 
                                                  'tot_death', 'new_death']], score

#Mary Jane MacArthur
def pre_cr_metadata(city_int):
    dirname = os.path.dirname(__file__)
    if city_int == 1: #Pittsburgh
        pre_cr_df = pd.read_csv(os.path.join(dirname, 'Pitt_data.csv'))
        score = 1
        return_items = []
        return_items.append(pre_cr_df)
        return_items.append(score)
        return return_items
    elif city_int == 2: #Portland
        pre_cr_df = pd.read_csv(os.path.join(dirname, 'Port_data.csv'))
        score = 1
        return_items = []
        return_items.append(pre_cr_df)
        return_items.append(score)
        return return_items
    elif city_int == 3: #St Louis
        pre_cr_df = pd.read_csv(os.path.join(dirname, 'StLouis_data.csv'))
        score = 2
        return_items = []
        return_items.append(pre_cr_df)
        return_items.append(score)
        return return_items
    else:
        print("Please enter, 1, 2, or 3")
        return
