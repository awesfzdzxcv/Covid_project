import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, date
sys.path.append('../PrepModules')

df_px = pd.read_table('/Users/Circe_1/Desktop/Build an interative dashboard/Streamlit Project/PrepedData/Covid_Distance.csv',
                      sep=',', delimiter=None, header=0, encoding_errors='ignore')
cases = pd.read_table('/Users/Circe_1/Desktop/Build an interative dashboard/Streamlit Project/PrepedData/cases.csv',
                      sep=',', delimiter=None, header=0, encoding_errors='ignore')
cases.set_index('country', inplace=True)

fig = px.scatter(df_px,
                 x="new_case_per_1M_population",
                 y="all_day_ratio_single_tile_users",
                 size="World_Share",
                 color="region",
                 hover_name="location",
                 log_x=True, size_max=60,
                 animation_frame = 'ds_x',
                 range_y=[0,0.7],
                 range_x=[0.001, 12000],
                 labels={
                     "new_case_per_1M_population": "New Covid cases per million people per day",
                     "all_day_ratio_single_tile_users": "Mobility index",
                     "region": "Region"})

fig.add_annotation(
    text = ("@Arthur Cheung <br>Source: Facebook movement research")
    , showarrow=False
    , x = 0
    , y = -0.35
    , xref='paper'
    , yref='paper'
    , xanchor='left'
    , yanchor='bottom'
    , xshift=-1
    , yshift=-5
    , font=dict(size=10, color="grey")
    , align="left"
    ,)

fig.update_layout(xaxis_range=[0.05, 4])
fig.update_layout(
    title="Relationship between social distancing and Covid cases")

st.plotly_chart(fig)


df = pd.read_table('/Users/Circe_1/Desktop/Build an interative dashboard/Streamlit Project/PrepedData/Covid_HK_Distance.csv',
                      sep=',', delimiter=None, header=0, encoding_errors='ignore').set_index('Unnamed: 0')
#Plotting scatter graph for HK regional mobility
x = df['ds'].unique()
y_HKI = df.loc[df['Region'] == 'HKI', 'allday_single_tile_byRegion']
y_KL = df.loc[df['Region'] == 'KL', 'allday_single_tile_byRegion']
y_NT = df.loc[df['Region'] == 'NT', 'allday_single_tile_byRegion']

fig_hk = make_subplots(specs=[[{"secondary_y": True}]]) # Create figure with secondary y-axis

# Add traces
fig_hk.add_trace(go.Scatter(x=df.ds, y=y_HKI, name="HKI", mode='markers'),
              secondary_y=False)
fig_hk.add_trace(go.Scatter(x=df.ds, y=y_KL, name="KL", mode='markers'),
              secondary_y=False)
fig_hk.add_trace(go.Scatter(x=df.ds, y=y_NT, name="NT", mode='markers'),
              secondary_y=False)

d_start=str(df.ds[0])[0:10]
d_end=str(list(df.ds)[-1])[0:10]
HK_daily_log=np.log10(cases.query('country == "Hong Kong"').set_index('ds').loc[d_start : d_end].daily)
HK_daily_log=HK_daily_log.rolling(7, min_periods=1, center=True).mean()

HK_Covid_cases = st.sidebar.checkbox('Show Daily Covid cases')
if HK_Covid_cases:
    fig_hk.add_trace(go.Scatter(x=df.ds, y=HK_daily_log, name="HK cases(Log)", mode='lines'),
                  secondary_y=True)

# Configure title and layout
fig_hk.update_layout(
    title="Social distancing in Hong Kong from 2020",
    xaxis_title="Dates",
    yaxis_title="Mobility index")
fig_hk.update_traces(marker=dict(size=3))

st.plotly_chart(fig_hk)