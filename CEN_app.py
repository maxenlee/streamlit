import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import requests
import nltk

# Download necessary NLTK data
nltk.download('punkt')

# Define keywords or phrases that are typically found in commercials
commercial_keywords = ["learn more", "visit", "call now", "buy", "order", "subscribe", "save"]

# Define search keywords
search_keywords = [
    "Education", "Public Education", "Students", "Schools", "Kids", "Elementary School",
    "Secondary School", "High School", "Charter Schools", "Education Policy", "Teacher",
    "Classroom", "Curriculum", "Academic", "Lesson", "Homework", "School District", "PTA",
    "Extracurricular", "Special Education", "Preschool", "Education Reform", "Literacy",
    "Education Technology", "Tutoring", "School Administration"
]

# Function to check if a snippet contains any commercial keyword
def is_commercial(snippet):
    for keyword in commercial_keywords:
        if keyword.lower() in snippet.lower():
            return True
    return False

# Function to analyze sentiment
def analyze_sentiment(snippet):
    analysis = TextBlob(snippet)
    return analysis.sentiment.polarity, analysis.sentiment.subjectivity

# Streamlit app
st.title("Education News Analysis")

# Check if the data is already fetched and processed
if 'data_fetched' not in st.session_state:
    st.session_state.data_fetched = False

# Fetch and process data if not already done
if not st.session_state.data_fetched:
    url = 'https://api.gdeltproject.org/api/v2/tv/tv'
    base_params = {
        'mode': 'ClipGallery',  # Mode to return a gallery of clips
        'format': 'json',  # Response format
        'TIMESPAN': '1W',  # Time span of 1 week
        'LAST24': 'yes',
        'DATACOMB': 'combined',
        'maxrecords': '3000'  # Increase the number of records to return
    }

    master_df = pd.DataFrame()

    for keyword in search_keywords:
        params = base_params.copy()
        params['query'] = f'{keyword} market:"National"'

        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    dict_key = list(data)[-1]  # Get the last key in the JSON response

                    if dict_key in data:
                        df = pd.DataFrame(data[dict_key])
                        df['search'] = keyword  # Add the search keyword to the DataFrame

                        # Filter out rows that contain commercial snippets
                        df = df[~df['snippet'].apply(is_commercial)]

                        # Remove duplicates based on the 'snippet' column
                        df = df.drop_duplicates(subset='snippet')

                        # Concatenate to master DataFrame
                        master_df = pd.concat([master_df, df], ignore_index=True)
                else:
                    st.write(f"No data found for keyword '{keyword}'")
            except ValueError:
                st.write(f"Error: Unable to parse JSON response for keyword '{keyword}'")
                st.write("Response content:", response.text)
        else:
            st.write(f"Error: {response.status_code} for keyword '{keyword}'")
            st.write("Response content:", response.text)

    if not master_df.empty:
        # Convert 'show_date' to datetime
        master_df['show_date'] = pd.to_datetime(master_df['show_date'])

        # Sort by the 'show_date' column
        master_df = master_df.sort_values(by='show_date')

        # Group snippets by 'ia_show_id' and concatenate them into a single column
        grouped_df = master_df.groupby('ia_show_id').agg({
            'preview_url': 'first',
            'date': 'first',
            'station': 'first',
            'show': 'first',
            'show_date': 'first',
            'preview_thumb': 'first',
            'snippet': lambda x: ' '.join(x),
            'search': lambda x: ', '.join(x)
        }).reset_index()

        grouped_df['search'] = grouped_df['search'].apply(lambda x: x.split(','))
        grouped_df['search'] = grouped_df['search'].apply(lambda x: list(set([num.strip() for num in x])))
        grouped_df = grouped_df.assign(relevance=lambda x: x['search'].apply(len))
        relevant_df = grouped_df[grouped_df['relevance'] > 1]
        relevant_df.reset_index(inplace=True)

        search_df = pd.DataFrame(relevant_df['search'].tolist())
        search_obj = search_df.stack()
        search_df = pd.get_dummies(search_obj)
        search_df = search_df.groupby(level=0).sum()
        df_encoded = pd.concat([relevant_df, search_df], axis=1)
        df_encoded[['sentiment', 'subjectivity']] = df_encoded['snippet'].apply(
            lambda x: pd.Series(analyze_sentiment(x)))

        st.session_state.df_final = df_encoded
        st.session_state.data_fetched = True
    else:
        st.write("No data found in the response.")

# Use the processed data
if 'df_final' in st.session_state:
    df_final = st.session_state.df_final

    # Display the dataframe
    st.write("## Dataset")
    st.dataframe(df_final)

    # Filter options
    st.write("## Filter Options")
    selected_station = st.selectbox("Select Station", options=df_final['station'].unique())
    selected_show = st.selectbox("Select Show", options=df_final['show'].unique())
    selected_date = st.date_input("Select Date", pd.to_datetime(df_final['date']).dt.date.min())

    # Filter the dataset based on user selection
    filtered_df = df_final[
        (df_final['station'] == selected_station) &
        (df_final['show'] == selected_show) &
        (pd.to_datetime(df_final['date']).dt.date == selected_date)
    ]

    st.write("## Filtered Data")
    st.dataframe(filtered_df)

    # Display top ten preview URLs
    st.write("## Top Ten Preview URLs")
    top_ten_preview_urls = df_final['preview_url'].head(10)
    for url in top_ten_preview_urls:
        st.markdown(f"- [Preview]({url})")

    # Show sentiment analysis
    st.write("## Sentiment Analysis")
    fig = px.histogram(df_final, x="sentiment", title="Sentiment Analysis")
    st.plotly_chart(fig)

    fig2 = px.histogram(df_final, x="subjectivity", title="Subjectivity Analysis")
    st.plotly_chart(fig2)

    # Summary statistics
    st.write("## Summary Statistics")
    st.write(df_final.describe())
else:
    st.write("Data is not available.")
