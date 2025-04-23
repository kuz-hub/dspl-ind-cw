import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="COVID-19 Dashboard - Sri Lanka", layout="wide")

def load_data():
    df = pd.read_csv("monthly data.csv")
    df['Date'] = pd.to_datetime(df['Data'], format='%bb-%y')
    return df

