import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from io import StringIO
import requests
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.optimize import least_squares
from pathlib import Path

URL_CASES = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
URL_DEATHS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
URL_VACCINES = "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv"

def download_data(URL):
    return pd.read_csv(URL)
cases = download_data(URL_CASES)
deaths = download_data(URL_DEATHS)
vaccines = download_data(URL_VACCINES)

# ------------------------#
CovidHKhospitalised = 'http://www.chp.gov.hk/files/misc/enhanced_sur_covid_19_eng.csv'
CovidHKvaccinated = 'https://www.healthbureau.gov.hk/download/opendata/COVID19/vaccination-rates-over-time-by-age.csv'
URL_HKcovid = "http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_covid_19_eng.csv"

def download_Gov_data(gov_url):  # HTTP error, hence the below IOrequest
    gov_request = requests.get(gov_url).text
    return pd.read_csv(StringIO(gov_request))

CovidHK_hospital = download_Gov_data(CovidHKhospitalised)
CovidHK_VacByAge = download_Gov_data(CovidHKvaccinated)
HKcovid = download_Gov_data(URL_HKcovid)
# ------------------------#
# FB movement data

movement1 = pd.read_table('./CountryPopulationStatistics/movement-range-2022-05-22.txt',
                          sep='\t', header=0, low_memory=False)
movement2 = pd.read_table(
    './CountryPopulationStatistics/movement-range-data-2020-03-01--2020-12-31.txt', sep='\t',
    header=0, low_memory=False)
movement = pd.concat([movement1, movement2])
movement = movement.sort_values(by=['ds', 'country'], ascending=True).reset_index(drop=True)
# ------------------------#
country_stats = pd.read_table('./CountryPopulationStatistics/CountryPopulationStatistics.csv',
                              sep=',', delimiter=None, header=0, encoding_errors='ignore')

cases = pd.melt(cases, id_vars=['Country/Region', 'Province/State'], value_vars=list(cases.iloc[:, 5:].columns),
                ignore_index=False)
HK = cases.query("`Country/Region` == 'China'" and "`Province/State` == 'Hong Kong'").replace(
    {'Country/Region': {'China': 'Hong Kong'}})
cases = pd.concat([cases, HK])
cases = cases.rename(columns={'variable': 'ds', 'value': 'daily_cases', 'Country/Region': 'country'})
cases['ds'] = pd.to_datetime(cases['ds'])
cases = cases.sort_values(by=['ds', 'country'], ascending=True)
cases['ds'] = pd.to_datetime(cases['ds'])
cases = cases.groupby(['country', 'ds'])['daily_cases'].agg(['sum']).reset_index().rename(columns={'sum': 'cases'})


deaths = pd.melt(deaths, id_vars=['Country/Region', 'Province/State'], value_vars=list(deaths.iloc[:, 5:].columns),
                 ignore_index=False)
HK = deaths.query("`Country/Region` == 'China'" and "`Province/State` == 'Hong Kong'").replace(
    {'Country/Region': {'China': 'Hong Kong'}})
deaths = pd.concat([deaths, HK])
deaths = deaths.rename(columns={'variable': 'ds', 'value': 'daily_deaths', 'Country/Region': 'country'})
deaths['ds'] = pd.to_datetime(deaths['ds'])
deaths = deaths.sort_values(by=['ds', 'country'], ascending=True)
deaths['ds'] = pd.to_datetime(deaths['ds'])
deaths = deaths.groupby(['country', 'ds'])['daily_deaths'].agg(['sum']).reset_index().rename(columns={'sum': 'deaths'})


# ------------Get daily data and get rid of errors------------#

def dictit(df):
    df = df.reset_index()
    df_dict = {zz: df[df['country'] == zz] for zz in df.country.unique()}
    return df_dict

def daily_data(df):
    df_dict = {i: df[df['country'] == i] for i in df.country.unique()}

    def error_mask(country_dict):
        mask = df_dict[country_dict] < df_dict[country_dict].cummax()
        df_dict[country_dict] = df_dict[country_dict].mask(mask)  # .interpolate().round(0).astype('np.float64')
        df_dict[country_dict].iloc[:, 2] = df_dict[country_dict].iloc[:, 2].interpolate().round(0).astype('int64')


    for country in df.country.unique():
        error_mask(country)
        # get_daily(country)
    #         remove_zeroes(country)
    df_dict1 = df_dict
    df = pd.concat(df_dict).set_index(['country'])
    return df

cases = daily_data(cases)
deaths = daily_data(deaths)

# ------------------------#
CovidHK_VacByAge = CovidHK_VacByAge.rename(columns={'ï»¿"Date"': 'ds'})
CovidHK_VacByAge['Sinovac total'] = CovidHK_VacByAge.iloc[:, 3:9].sum(axis=1)
CovidHK_VacByAge['BioNTech total'] = CovidHK_VacByAge.iloc[:, 9:15].sum(axis=1)
CovidHK_VacByAge['Vaxed_once'] = CovidHK_VacByAge.loc[:, ['Sinovac 1st dose', 'BioNTech 1st dose']].sum(axis=1)
CovidHK_VacByAge['Vaxed_twice'] = CovidHK_VacByAge.loc[:, ['Sinovac 2nd dose', 'BioNTech 2nd dose']].sum(axis=1)
CovidHK_VacByAge['Vaxed_thrice'] = CovidHK_VacByAge.loc[:, ['Sinovac 3rd dose', 'BioNTech 3rd dose']].sum(axis=1)
CovidHK_VacByAge = CovidHK_VacByAge[
    ['ds', 'Age Group', 'Sex', 'Sinovac total', 'BioNTech total', 'Vaxed_once', 'Vaxed_twice', 'Vaxed_thrice']]

# ------------------------#
country_map = country_stats[['Country', '3char country code']].set_index('3char country code').to_dict()
movement = movement.replace({'country': country_map['Country']})
movement = movement[['ds', 'country', 'all_day_ratio_single_tile_users']].rename(
    columns={'all_day_ratio_single_tile_users': 'mobility'})

# ------------Replace country name------------#
REPLACE_COUNTRY_NAME = {
    "Korea, South": "South Korea",
    "Taiwan*": "Taiwan",
    "Burma": "Myanmar",
    "Holy See": "Vatican City"}

def replace_name(df):
    df = df.reset_index()
    df = df.replace({df.columns[0]: REPLACE_COUNTRY_NAME})
    df = df.set_index(['country'])
    return df

replace_name(cases)

cases = replace_name(cases)
deaths = replace_name(deaths)

def smooth_data(df):
    df = df.reset_index()
    df_dict = {zz: df[df['country'] == zz] for zz in df.country.unique()}

    def Lowess_data(country_dict):
        cum_y = df_dict[country_dict].iloc[:, 2]
        x = df_dict[country_dict].ds.values
        frac = 15 / len(x)
        # daily_lowess=lowess(daily_y,x,frac=frac, is_sorted=True, return_sorted=False).round(0)
        cum_lowess = lowess(cum_y, x, frac=frac, is_sorted=True, return_sorted=False).round(0)
        df_dict[country_dict].iloc[:, 2] = list(cum_lowess)
        df_dict[country_dict]['daily'] = df_dict[country_dict].iloc[:, 2].diff()
        df_dict[country_dict].iloc[0, 3] = df_dict[country_dict].iloc[0, 2]  # first data point in each country
        # df_dict[country_dict].loc[df_dict[country_dict].iloc[:,3] < 0, df_dict[country_dict].iloc[:,3]]=0
        # df_dict[country_dict].loc[df_dict[country_dict].iloc[:,2] < 0, df_dict[country_dict].iloc[:,2]]=0

    for country in df.country.unique():
        Lowess_data(country)

    df = pd.concat(df_dict).set_index(['country'])
    return df

cases_s = smooth_data(cases)
deaths_s = smooth_data(deaths)


filepath = Path('./PrepedData/cases.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
cases_s.to_csv(filepath)

filepath = Path('./PrepedData/deaths.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
deaths_s.to_csv(filepath)


