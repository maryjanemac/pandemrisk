from numpy import NaN
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd


def WHOData(countryName):
    url = 'https://covid.ourworldindata.org/data/owid-covid-data.json'    
    response = urlopen(url)
    # data = json.loads(response.read())
    df = pd.read_json(url)
    df = df.transpose()
    index = pd.Series(range(len(df)))
    df = df.set_index(index)

    # print(df)
    # print(df.columns.values)
    # countryName = input("Enter the country name: ")
    countryData = {'location':[],'date':[],'new_cases':[],'new_deaths':[], \
            'people_vaccinated':[],'population_density':[]}
    # countryData = pd.DataFrame(columns=['location','date','new_cases','new_deaths','icu_patients', \
    #         'people_vaccinated','population_density','handwashing_facilities'])
    # print(df.loc[df['location'] == countryName])
    # print(df.loc[df['location'] == countryName]['data'][0])
    # print(type(df.loc[df['location'] == countryName]['data'][0]))
    for d in df.loc[df['location'] == countryName]['data'][0]:
        # print(d)
        # countryData.append([countryName],d['date'],d['new_cases'],d['new_deaths'],d['icu_patients'],d['people_vaccinated'],d['population_density'],d['handwashing_facilities'])
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
