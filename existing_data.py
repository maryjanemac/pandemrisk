from numpy import NaN
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd
import os
import sys


def existingWHOData(countryName):
    df = pd.read_csv('who_data.csv')

    # check if the countryName is valid
    if (countryName not in df['iso_code'].values):
        print("Sorry, no data for this country. Please try another one.")
        return

    df = df[['iso_code', 'location','date','new_cases','new_deaths', \
            'people_vaccinated','population_density']]
    # print(df)

    countryData = df.loc[df['iso_code'] == countryName]

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
