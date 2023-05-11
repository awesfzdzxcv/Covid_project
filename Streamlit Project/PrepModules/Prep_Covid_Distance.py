import sys
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, date
import matplotlib.pyplot as plt

##Covid dataset countries
Covid_all = pd.read_table('./Streamlit Project/CountryPopulationStatistics/owid-covid-data.csv', sep=',', delimiter=None, header=0)
Covid_all['date'] = pd.to_datetime(Covid_all['date'])
Covid_all = Covid_all[['date', 'iso_code', 'location', 'new_cases', 'new_deaths']]
Covid_country = pd.DataFrame(Covid_all['iso_code'].unique())

##FB dataset countries
df_1 = pd.read_table('./Streamlit Project/CountryPopulationStatistics/movement-range-data-2020-03-01--2020-12-31.txt', sep='\t', header=0, low_memory = False)
df_2 = pd.read_table('./Streamlit Project/CountryPopulationStatistics/movement-range-2022-05-22.txt', sep='\t', header=0, low_memory = False)
df_all = pd.concat([df_1,df_2])
df_HK = df_all

df_all['ds'] = pd.to_datetime(df_all['ds'])
df_all = df_all.sort_values(by=['ds', 'polygon_name'], ascending=True)
df_all = df_all.drop(['polygon_source', 'polygon_id', 'polygon_name', 'all_day_bing_tiles_visited_relative_change', 'baseline_name', 'baseline_type'], axis=1)
df_all = df_all.groupby(['ds','country']).mean().reset_index() #Groupby date and get MEAN

df_country = pd.DataFrame(df_all['country'].unique())#Get list of countries from FB data
Country = pd.merge(Covid_country, df_country, how='inner')#Merge FB and Covid dataset countries via INNER
Country.columns = ['Country']
#Remove countries with no FB data or Covid Data
df_all = pd.merge(df_all, Country, left_on='country', right_on='Country', how='left')

##Getting country codes and country population data + merging
country_codes = pd.read_table('/Users/Circe_1/Desktop/FB + Covid/CountryNamesCodes.csv', sep=',',delimiter=None, header=0, encoding_errors='ignore')
country_popu = pd.read_table('/Users/Circe_1/Desktop/FB + Covid/CountryPopulationStatistics.csv', sep=',',delimiter=None, header=0, encoding_errors='ignore')
country_codes = country_codes[['2char country code', '3char country code', 'region']]
country_popu = pd.merge(country_popu, country_codes, left_on='2char country code', right_on='2char country code', how='left')
country_popu = country_popu[['Country', 'region', '3char country code_x', 'World Share', 'Population', 'Density (P/Km2)']]
country_popu = country_popu.rename({'3char country code_x':'3char country code'}, axis=1)

##Combine FB and Covid Dataset and Country population
df_all = pd.merge(df_all, Covid_all, left_on=['ds', 'country'], right_on=['date', 'iso_code'], how='left')
df_all = pd.merge(df_all, country_popu, left_on='country', right_on='3char country code', how='left')

##Remove countries with too little Covid data
Data_point_per_country = df_all.groupby('country').count()
Max_days_per_country = Data_point_per_country['ds'].max()
Countries_analysed = Data_point_per_country[['ds']].loc[Data_point_per_country['ds'] > Max_days_per_country-10].reset_index()
df_cleaned = pd.merge(df_all, Countries_analysed, left_on='country', right_on='country', how='inner').reset_index(drop=True)

df_cleaned = df_cleaned[['ds_x', 'country', 'region', 'location', 'all_day_ratio_single_tile_users', 'new_cases', 'new_deaths', 'World Share', 'Population']].sort_values(by=['ds_x', 'country'], ascending=True).reset_index(drop=True)
df_cleaned = df_cleaned.fillna({'new_cases':0, 'new_deaths':0}).fillna(0) #Replace Nan values with ZERO
df_cleaned['World Share'] = df_cleaned['World Share'].str.rstrip('%').astype('float') / 100
df_cleaned = df_cleaned.rename({'World Share' : 'World_Share'}, axis='columns')
df_cleaned['Population'] = df_cleaned['Population'].str.replace(',','').astype(float)
df_cleaned = df_cleaned[df_cleaned.Population > 7000000] #Remove countries with population less than 5M
df_cleaned['new_case_per_1M_population'] = df_cleaned['new_cases'] / df_cleaned['Population'] * 1000000 #new column for Covid cases per 1M population
df_cleaned['new_case_per_1M_population_adj'] = df_cleaned['new_case_per_1M_population'].replace(int(0), int(1))
df_cleaned['new_case_per_1M_population_adj'].values[df_cleaned['new_case_per_1M_population_adj'] <= 10] = 1
df_cleaned['Logscale_new_case_per_1M_population'] = np.log10(df_cleaned['new_case_per_1M_population_adj'])
df_cleaned = df_cleaned.set_index('region')

Covid_all=Covid_all.drop_duplicates(subset=['iso_code']).reset_index(drop=True)
Covid_all=Covid_all[['iso_code','location']].set_index('iso_code')
dic=Covid_all.to_dict()
dic=dic['location']
df_cleaned=df_cleaned.replace(dic)
df=df_cleaned.sort_values(['country', 'ds_x']).reset_index()
df.loc[df['country'] == "Hong Kong", 'region'] = 'Hong Kong'

df_px = df
df_px['ds_x'] = df_px['ds_x'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))

from pathlib import Path
filepath = Path('./Streamlit Project/PrepedData/Covid_Distance.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
df_px.to_csv(filepath)
