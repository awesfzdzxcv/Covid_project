import sys
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, date
import matplotlib.pyplot as plt

#HK_Covid analysis
#Facebook data on people mobility data in HK
df1 = pd.read_table('./Streamlit Project/CountryPopulationStatistics/movement-range-data-2020-03-01--2020-12-31.txt', sep='\t', header=0, low_memory = False)
df1 = df1.loc[df1['country'] == 'HKG']
df2 = pd.read_table('./Streamlit Project/CountryPopulationStatistics/movement-range-2022-05-22.txt', sep='\t', header=0, low_memory = False)
df2 = df2.loc[df2['country'] == 'HKG']
df = pd.concat([df1,df2])

df['ds'] = pd.to_datetime(df['ds'])
    #drop rows Outer Islands District
df = df[df.polygon_name != 'Islands']
df = df.sort_values(by=['ds', 'polygon_name'], ascending=True)

#Data for COVID cases in HK
Covid_HK = pd.read_table('./Streamlit Project/CountryPopulationStatistics/owid-covid-data.csv',sep=',',delimiter=None, header=0)
Covid_HK = Covid_HK.loc[Covid_HK['iso_code'] == 'HKG']
    #Retain only dates and covid cases from CSV
Covid_HK = Covid_HK[['date', 'iso_code', 'location', 'new_cases', 'new_deaths']]
    #replace 0 new cases with 1 new cases for Log scale purposes
Covid_HK['new_cases'] = Covid_HK['new_cases'].replace(int(0), int(1))
    #log scale of new cases in HK
Covid_HK['new_cases_log'] = np.log10(Covid_HK['new_cases'])
Covid_HK = Covid_HK.reset_index(drop=True)
Covid_HK = Covid_HK.drop(Covid_HK.index[0:38]).reset_index(drop=True)
Covid_HK['date'] = pd.to_datetime(Covid_HK['date'])

#HK Districts and District population
Dist_popu = {'District' : ['Kowloon City', 'Wan Chai', 'North', 'Tuen Mun',
       'Tsuen Wan', 'Sham Shui Po', 'Sai Kung', 'Eastern', 'Yuen Long',
       'Kwai Tsing', 'Tai Po', 'Sha Tin', 'Yau Tsim Mong',
       'Central and Western', 'Southern', 'Kwun Tong', 'Wong Tai Sin'],
      'Population@2016' : [419, 180, 315, 489, 319, 406, 162, 555, 607, 521, 304, 660, 343, 243, 275, 649, 425]
            }

Dist_popu = pd.DataFrame(Dist_popu)
Dist_popu_sum = Dist_popu['Population@2016'].sum()
Dist_popu['Dist_popu_ratio'] = Dist_popu['Population@2016'] / Dist_popu_sum
Dist_popu['Weighted_popu'] = Dist_popu['Population@2016'] * Dist_popu['Dist_popu_ratio']

#Region and district data | Combining Districts into Regions
NT = ['Kwai Tsing', 'North', 'Sai Kung', 'Sha Tin', 'Tai Po', 'Tsuen Wan', 'Tuen Mun', 'Yuen Long']
KL =['Kowloon City', 'Kwun Tong', 'Sham Shui Po', 'Wong Tai Sin', 'Yau Tsim Mong']
HKI = ['Central and Western', 'Eastern', 'Southern', 'Wan Chai']

Region_class = pd.DataFrame([np.ravel(x) for x in [NT, KL, HKI]])
Region_class['index'] = ['NT', 'KL', 'HKI']
Region_class = Region_class.set_index('index').transpose()
Region_class = Region_class.melt()
Region_class = Region_class.rename({'index':'Region','value':'District'}, axis=1)
#Delete row with None
Region_class = Region_class.dropna()

#Data by District
Dist_popu = pd.merge(Dist_popu, Region_class, on=['District'])
Dist_popu['Dist_popu_adj'] = Dist_popu['Dist_popu_ratio'] * 17

#Data by Region
Region_popu = Dist_popu.groupby(['Region']).sum()
Region_popu['Region_popu_ratio'] = Region_popu['Population@2016'] / Region_popu['Population@2016'].sum()

#Region_popu['Region_popu_adj'] = Region_popu['Region_popu_ratio'] * 3
Region_popu = Region_popu.drop(['Weighted_popu', 'Dist_popu_adj'], axis=1)
Region_popu['#_of_Districts'] = [4,5,8]

#Merging Region classification data + District_popu ratio/adj + Region_popu ratio/adj
df = pd.merge(df, Dist_popu[['District', 'Region', 'Dist_popu_adj']], left_on='polygon_name', right_on='District', how='left')
df = pd.merge(df, Region_popu[['Region_popu_ratio', '#_of_Districts']], left_on='Region', right_on='Region', how='left')
df = df.drop(['District', 'baseline_name', 'baseline_type', 'polygon_id', 'polygon_source'], axis=1)
df = df.dropna()
#Percentage of ppl staying witin a single tile in a day by District
df['allday_single_tile_byDistrict'] = df['all_day_ratio_single_tile_users'] * df['Dist_popu_adj']

#Summarising District level data to Regional level data
df = df.groupby(['ds','Region', 'country']).agg({'all_day_bing_tiles_visited_relative_change': np.sum, 'allday_single_tile_byDistrict': np.sum, '#_of_Districts': 'first','Region_popu_ratio': 'first'})
df['allday_single_tile_byRegion'] = df['allday_single_tile_byDistrict'] / df['#_of_Districts']

#Reset index after groupby | setting drop as false to not remove index
df = df.reset_index(drop=False)

#Plotting scatter graph for HK regional mobility
x = df['ds'].unique()
y_HKI = df.loc[df['Region'] == 'HKI', 'allday_single_tile_byRegion']
y_KL = df.loc[df['Region'] == 'KL', 'allday_single_tile_byRegion']
y_NT = df.loc[df['Region'] == 'NT', 'allday_single_tile_byRegion']

#Axis 1 for social distancing over time
fig_HK, ax1 = plt.subplots()
print(f'x={len(x)}, y={len(y_HKI)}')
ax1.scatter(x, y_HKI, c='b',s=1, label="HKI")
ax1.scatter(x, y_KL, c='r',s=1, label="KL")
ax1.scatter(x, y_NT, c='g',s=1, label="NT")
ax1.figure.set_size_inches(15,5)
ax1.set_xlabel('Date')
ax1.set_ylabel('Mobility index')
ax1.set_title('Social distancing in Hong Kong beginning from 2020')
ax1.legend()

# #Axis 2 for Covid cases in HK over time
# fig_HK, ax2 = plt.subplots()
#
# x2 = Covid_HK['date'].to_numpy()
# y2 = Covid_HK['new_cases_log']
# ax2.plot(x2, y2, c='black')
# ax2.figure.set_size_inches(12.5,5)
# ax2.set_xlabel('Date')
# ax2.set_ylabel('Log scale of new Covid cases in HK')
# ax2.set_title('Number of new Covid Casees in HK over time')
# #ax2.locator_params(axis='x', nbins=10)
# ax2.locator_params(nbins=10, axis='x')

fig_HK.tight_layout()
plt.show()

from pathlib import Path
filepath = Path('./Streamlit Project/PrepedData/Covid_HK_Distance.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(filepath)
