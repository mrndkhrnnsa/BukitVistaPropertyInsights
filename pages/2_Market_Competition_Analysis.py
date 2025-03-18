import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

#load dataset
@st.cache_data
def load_data():
    final_df = pd.read_csv('dataset/CombinedData.csv')
    return final_df

df = load_data()
bv = df[df['DataSource'] == 'BukitVista']
tl = df[df['DataSource'] == 'Traveloka']

#clean features
def clean_list_type(value):
    if isinstance(value, list): 
        return value
    if isinstance(value, str):  
        value = value.replace("'", "").replace('"', "")
        return [x.strip() for x in value.strip("[]").split(",") if x.strip()]
    return []

bv['Features'] = bv['Features'].apply(clean_list_type)
tl['Features'] = tl['Features'].apply(clean_list_type)

exploded_features = tl.explode('Features') #currently only using traveloka, so only exploding traveloka features
exploded_features['Features'] = exploded_features['Features'].replace('', 'N/A')

#compare price per night between BukitVista and Traveloka across different area
st.markdown('#### 🤑 Price per Night Comparison')
st.markdown('The chart below highlights the differences in price values of properties across different areas from BukitVista\'s data and competitor\'s data.')
fig2 = px.box(df, y='PriceValue', x='Area', color = 'DataSource', 
              title='Property Prices per Night',
              labels={'PriceValue': 'Price (USD)', 'Area': 'Location'})
color_map = {'BukitVista': 'BukitVista\'s', 'Traveloka': 'Competitor\'s'}
fig2.for_each_trace(lambda trace: trace.update(name=color_map.get(trace.name, trace.name)))
st.plotly_chart(fig2)

#rating prediction of BukitVista properties using model trained from Traveloka
st.markdown('#### 🌟🌟🌟 Best-Value Villas: Rating & Price Insights ')
st.markdown('The table below shows the most potentially profitable properties with the cheapest price yet highest predicted rating.')

#import model and encoder
model = joblib.load('models/rating_predictor_model.pkl')
encoder = joblib.load('models/location_encoder.pkl')

#pre-process data for rating predictions 
def encode_location(loc):
    return encoder.transform([loc])[0] if loc in encoder.classes_ else None

bv['Area_encoded'] = bv['Area'].apply(encode_location)

#create filter
selected_areas = st.multiselect('Select Area: ', options=bv['Area'].unique(), default=bv['Area'].unique())

#apply filter
bv_filtered = bv[bv['Area'].isin(selected_areas)]

#create dataframe for prediction - ignoring areas not included in training set
X_bv = bv_filtered[['PriceValue', 'Area_encoded']].dropna()

#use model for rating prediction
if not X_bv.empty:
    bv_filtered.loc[X_bv.index, 'Predicted_Rating'] = model.predict(X_bv)

    bv_filtered['Predicted_Rating'] = bv_filtered['Predicted_Rating'].apply(lambda x: round(x, 1) if isinstance(x, (int, float)) else x)
    bv_filtered['Predicted_Rating'].fillna('Unknown', inplace=True)

    top_properties = bv_filtered.sort_values(by=['Predicted_Rating', 'PriceValue'], ascending=[False, True]).head(3)

    st.write(top_properties[['VillaName', 'Area', 'PriceValue', 'Predicted_Rating']])
else:
    st.warning('No properties found. Please select at least one Area of interest.')