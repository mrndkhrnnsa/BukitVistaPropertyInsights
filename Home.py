import streamlit as st
import pandas as pd

st.set_page_config(
    page_title = 'BukitVista InternPro',
)

st.title('🏡 BukitVista Property Insights')
st.subheader('Enhancing Listings Through Data Science')

st.markdown('''
    Welcome to the BukitVista Market Insights Dashboard! This tool helps analyze property listings and compare them with market competitors to identify areas for improvement.

            
    ##### 📌 Key Features:
            '''
)

if st.button('**📊 Property Analysis:**'):
    st.switch_page('pages/1_BukitVista_Listings_Insights.py')
st.markdown('• In-depth insights into BukitVista’s property data')

if st.button('**💡 Market Competition:**'):
    st.switch_page('pages/2_Market_Competition_Analysis.py')
st.markdown('• Comparing BukitVista’s listings with similar properties from Traveloka')
