import streamlit as st
import pandas as pd
import plotly.express as px

#load dataset
@st.cache_data
def load_data():
    df = pd.read_csv('dataset/BukitVistaScrape.csv')
    return df

df = load_data()

#sidebar filters
st.sidebar.header('Filters')
selected_area = st.sidebar.multiselect('Select Area: ', options=df['Area'].unique(), default=df['Area'].unique())

def clean_list_type(value):
    if isinstance(value, list): 
        return value
    if isinstance(value, str):  
        value = value.replace("'", "").replace('"', "")
        return [x.strip() for x in value.strip("[]").split(",")]
    return []

df['PropertyType'] = df['PropertyType'].apply(clean_list_type)

selected_property_type = st.sidebar.multiselect('Select Property Type: ', 
                                                options=['Villa', 'Guest House', 'Residential'], 
                                                default=['Villa', 'Guest House', 'Residential'])

if not selected_area:
    st.sidebar.warning('No properties found. Please select at least one Area of interest.')

if not selected_property_type:
    st.sidebar.warning('No properties found. Please select at least one Property Type of interest.')

#apply filter
area_filter = (df['Area'].isin(selected_area))
property_filter = df['PropertyType'].apply(lambda x: any(pt in x for pt in selected_property_type))

filtered_df = df[area_filter & property_filter]

#create different tabs
tabs = st.tabs(['Price Evaluation', 'Feature Analysis'])

#Price Evaluation tab
with tabs[0]:
    st.markdown('### 💰 Price Evaluation: Understanding Price Trends')
    
    st.markdown('#### 📈 Price Distribution per Night')
    st.markdown('This boxplot shows the spread of prices per night for properties in different locations.')
    fig1 = px.box(filtered_df, y='PriceValue', x='Area', 
                  title='Property Prices per Night', 
                  labels={'PriceValue': 'Price (USD)', 'Area': 'Location'})
    st.plotly_chart(fig1)
    
    st.markdown('#### 🔎 Pricing Analysis')
    st.markdown('The charts below show how pricing scales with guest capacity, the number of bedrooms, and the number of bathrooms.')
    fig2 = px.bar(filtered_df, y='PriceValue', x='GuestNo', color='Area', 
                  title='👥 Price per Night by Guest Capacity and Area',
                  labels={'PriceValue': 'Price (USD)', 'GuestNo': 'Guest Capacity'})
    st.plotly_chart(fig2)

    fig3 = px.bar(filtered_df, y='PriceValue', x='Bedrooms', color='Area', 
                  title='🛏️ Price per Night by Number of Bedrooms and Area',
                  labels={'PriceValue': 'Price (USD)', 'Bedrooms': 'No. of Bedrooms'})
    st.plotly_chart(fig3)

    fig4 = px.bar(filtered_df, y='PriceValue', x='Bathrooms', color='Area', 
                  title='🚿 Price per Night by Number of Bathrooms and Area',
                  labels={'PriceValue': 'Price (USD)', 'Bathrooms': 'No. of Bathrooms'})
    st.plotly_chart(fig4)

#Feature Analysis tab
with tabs[1]:
    filtered_df['Features'] = filtered_df['Features'].apply(clean_list_type)
    exploded_features = filtered_df.explode('Features')
    exploded_features['Features'] = exploded_features['Features'].replace('', 'N/A')

    st.markdown('#### ✨ Most Common Feature Available')
    st.markdown('This table below displays the most common feature available for properties in each area. ')
    feature_counts = exploded_features.groupby('Area')['Features'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A')
    st.write(feature_counts)

    st.markdown('#### 📊 Price Distribution by Feature')
    st.markdown('The barchart below explores the average price of properties with specific features across different areas.')
    df_grouped = exploded_features.groupby(['Features', 'Area'], as_index=False)['PriceValue'].mean()
    fig5 = px.bar(
        df_grouped, x='Features', y='PriceValue', color='Area', barmode='group',
        title='Price per Night for Features Across Areas',
        labels={'PriceValue': 'Price (USD)', 'Features': 'Feature'})
    st.plotly_chart(fig5)
