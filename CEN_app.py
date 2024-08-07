import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = 'grouped_education_news.csv'
education_news_df = pd.read_csv(file_path)

# Convert date column to datetime
education_news_df['date'] = pd.to_datetime(education_news_df['date'])

# Title and description
st.title('Education News Analysis')
st.write('Analyze education-related news articles using various metrics, filters, and timelines.')

# Sidebar filters
st.sidebar.header('Filters')
selected_station = st.sidebar.multiselect('Select Station', education_news_df['station'].unique())
selected_relevance = st.sidebar.slider('Select Relevance Score Range', 
                                       min_value=int(education_news_df['relevance'].min()), 
                                       max_value=int(education_news_df['relevance'].max()), 
                                       value=(int(education_news_df['relevance'].min()), int(education_news_df['relevance'].max())))
selected_date_range = st.sidebar.date_input('Select Date Range', 
                                            value=(education_news_df['date'].min(), education_news_df['date'].max()))

# Filter the dataset based on selections
filtered_df = education_news_df[
    (education_news_df['station'].isin(selected_station) if selected_station else True) &
    (education_news_df['relevance'] >= selected_relevance[0]) &
    (education_news_df['relevance'] <= selected_relevance[1]) &
    (education_news_df['date'] >= pd.to_datetime(selected_date_range[0])) &
    (education_news_df['date'] <= pd.to_datetime(selected_date_range[1]))
]

# Show filtered data
st.write('Filtered Data', filtered_df)

# Metrics
st.header('Metrics')
st.write('### Relevance Score Distribution')
fig, ax = plt.subplots()
ax.hist(filtered_df['relevance'], bins=20, edgecolor='k', alpha=0.7)
ax.set_title('Distribution of Relevance Scores')
ax.set_xlabel('Relevance Score')
ax.set_ylabel('Frequency')
st.pyplot(fig)

st.write('### Top 5 Stations by Number of Articles')
top_stations = filtered_df['station'].value_counts().head(5)
st.bar_chart(top_stations)

st.write('### Articles by Date')
articles_by_date = filtered_df['date'].value_counts().sort_index()
st.line_chart(articles_by_date)

st.write('### Sentiment Analysis')
avg_sentiment = filtered_df['sentiment'].mean()
st.metric(label="Average Sentiment", value=avg_sentiment)

# Detailed view
st.header('Detailed View')
selected_article = st.selectbox('Select an Article', filtered_df['ia_show_id'])
article_details = filtered_df[filtered_df['ia_show_id'] == selected_article].iloc[0]
st.write('### Article Details')
st.write('**Show ID:**', article_details['ia_show_id'])
st.write('**Preview URL:**', article_details['preview_url'])
st.write('**Date:**', article_details['date'])
st.write('**Station:**', article_details['station'])
st.write('**Show:**', article_details['show'])
st.write('**Snippet:**', article_details['snippet'])
st.write('**Relevance Score:**', article_details['relevance'])
st.write('**Sentiment:**', article_details['sentiment'])
st.write('**Subjectivity:**', article_details['subjectivity'])

st.write('### Preview')
st.image(article_details['preview_thumb'])

# Run the Streamlit app
if __name__ == '__main__':
    st.run()
