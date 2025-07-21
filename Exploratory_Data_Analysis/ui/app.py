import streamlit as st
import pandas as pd

st.title('Exploratory Data Analysis Project UI')
st.write('Upload a CSV file to get started!')

uploaded_file = st.file_uploader('Choose a CSV file', type='csv')
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write('## Data Preview')
        st.dataframe(df.head())
        st.write('## Data Summary')
        st.write(df.describe())
    except Exception as e:
        st.error(f'Error loading file: {e}')
