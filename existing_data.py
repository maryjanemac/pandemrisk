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
