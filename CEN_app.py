import streamlit as st
import requests

# Set up the Streamlit app
st.title("GDELT API Demo with iFrames")

# Function to fetch data from GDELT API
def fetch_gdelt_data():
    url = 'https://api.gdeltproject.org/api/v2/tvai/tvai'
    params = {
        'format': 'json',
        'timespan': 'FULL',
        'query': 'ocr:"REALDONALDTRUMP" -ocr:"DONALDJTRUMP" (station:KGO OR station:KPIX OR station:KNTV)',
        'mode': 'clipgallery',
        'maxrecords': 100
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            st.error("Error: Failed to parse JSON response.")
            st.text(response.text)
    else:
        st.error(f"Error: {response.status_code}")
        st.text(response.text)
    return None

# Fetch data from the GDELT API
clips_data = fetch_gdelt_data()

if clips_data:
    st.subheader("GDELT API Clips")

    # Display the clips using iFrames
    for clip in clips_data.get('clipgallery', []):
        st.write(f"**Show:** {clip.get('show', 'N/A')}")
        st.write(f"**Station:** {clip.get('station', 'N/A')}")
        st.write(f"**Snippet:** {clip.get('snippet', 'N/A')}")
        preview_url = clip.get('preview_url', 'N/A')
        if preview_url != 'N/A':
            st.components.v1.iframe(preview_url, width=560, height=315)
        st.write("---")

else:
    st.write("No data returned for the specified query.")
