import sys
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, date
path = os.path.abspath("module1")
sys.path.append('/Streamlit-Project')
from Models import train_data

cases = pd.read_table('/Streamlit-Project/PrepedData/cases.csv',
                      sep=',', delimiter=None, header=0, encoding_errors='ignore')
cases.set_index('country', inplace=True)
deaths = pd.read_table('/Streamlit-Project/PrepedData/deaths.csv',
                       sep=',', delimiter=None, header=0, encoding_errors='ignore')
deaths.set_index('country', inplace=True)

cat = st.sidebar.radio('Data Type', ('Covid Cases', 'Covid Deaths'))
if cat == 'Covid Cases':
    df = cases
elif cat == 'Covid Deaths':
    df = deaths

clist = df.index.unique()
country = st.sidebar.selectbox("Select a country:", clist)
# price = st.slider("Date range", value=datetime.date(2020, 1, 1), 10000000, step=100000)

latest_date_in_data = datetime.strptime((df.query('country == country').ds.max()),'%Y-%m-%d').date()
start_time, end_time = st.sidebar.slider(
    "Model Training period",
    value=(latest_date_in_data - pd.Timedelta("120D"), latest_date_in_data,))

text = '''---------------------------'''
st.sidebar.markdown(text)
st.sidebar.text('Display Options')

pred, tail = train_data(df, country, str(start_time), str(end_time), 5, 120)

data=df.loc[str(country)]

fig1 = px.line()
fig1.add_scatter(x=data.ds, y=data.iloc[:,1], mode='lines',
                name=f'Cumulative {df.columns[1]}')
fig1.add_scatter(x=pred.index, y=pred.values, mode='lines',
                name=f'Projected {df.columns[1]}')
fig1.update_layout(xaxis_title='Date', yaxis_title='Cases')


fig2 = px.line()
daily_diff = data.iloc[:,1].diff()
daily_diff = daily_diff.replace(0,np.nan)
fig2.add_scatter(x=data.ds, y=daily_diff, mode='lines',
                name=f'Daily {df.columns[1]}')

pred_daily_diff = pred.diff()
pred_daily_diff = pred_daily_diff.replace(0, np.nan)
fig2.add_scatter(x=pred_daily_diff.index, y=pred_daily_diff.values, mode='lines',
                name=f'Projected {df.columns[1]}')
fig2.update_layout(xaxis_title='Date', yaxis_title='Deaths')

tail_show = st.sidebar.checkbox('Show Projection Model Tail')
if tail_show:
    fig1.add_scatter(x=tail.index, y=tail.values, mode='lines', name=f'Projection model tail')
    tail_daily_diff = tail.diff()
    tail_daily_diff = tail_daily_diff.replace(0, np.nan)
    fig2.add_scatter(x=tail_daily_diff.index, y=tail_daily_diff.values, mode='lines', name=f'Projection model tail')
    # fig1.update_layout()
    # fig2.update_layout()

training_period = st.sidebar.checkbox('Show Training Period')
if training_period:
    fig1.add_vrect(x0=start_time, x1=end_time, annotation_text="Training Period", annotation_position="bottom left",
       annotation_font_size=20, annotation_opacity=0.4,
       annotation_textangle=90, line_width=0, fillcolor="red", opacity=0.15)

st.header(f"Smoothed Cumulative Covid {df.columns[1].capitalize()} beginning from 2020")
st.plotly_chart(fig1)
st.header(f"Daily Covid {df.columns[1].capitalize()} beginning from 2020")
st.plotly_chart(fig2)
