import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# Function to load data from JSON file
def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data_dict = json.load(f)
            if data_dict and data_dict.get('date'):  # Check if file has data
                # Convert string dates back to datetime.date objects
                data_dict['date'] = [datetime.strptime(d, '%Y-%m-%d').date() for d in data_dict['date']]
            else:
                data_dict = {'date': [], 'score': []}
            return pd.DataFrame(data_dict)
    else:
        # Start with empty DataFrame
        return pd.DataFrame({'date': [], 'score': []})

# Function to save data to JSON file
def save_data(df):
    data_dict = df.copy()
    # Convert datetime.date objects to strings for JSON serialization
    data_dict['date'] = [d.strftime('%Y-%m-%d') for d in data_dict['date']]
    with open('data.json', 'w') as f:
        json.dump(data_dict.to_dict(orient='list'), f, indent=2)

# Initialize or load data
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# App title
st.title("🎈 Daily Relationship Score Tracker")

# Sidebar for adding new data
st.sidebar.header("Add New Entry")

# Date input
new_date = st.sidebar.date_input("Select Date", datetime.now().date())

# Score input
new_score = st.sidebar.slider("Enter Relationship Score", 1, 10, 7)

# Add data button
if st.sidebar.button("Add/Update Score"):
    # Update existing date or add new entry
    date_exists = new_date in st.session_state.data['date'].values
    if date_exists:
        st.session_state.data.loc[st.session_state.data['date'] == new_date, 'score'] = new_score
    else:
        new_row = pd.DataFrame({'date': [new_date], 'score': [new_score]})
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
    
    # Sort by date
    st.session_state.data = st.session_state.data.sort_values('date')
    
    # Save to JSON file
    save_data(st.session_state.data)

# Only show the chart if there's data
if not st.session_state.data.empty:
    # Display the line chart
    st.subheader("Relationship Score Over Time")
    fig = px.line(
        st.session_state.data,
        x='date',
        y='score',
        markers=True,
        title='Daily Relationship Score Trends'
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Score",
        yaxis_range=[0, 10]
    )
    st.plotly_chart(fig)

    # Display the data table
    st.subheader("Data Table")
    st.dataframe(
        st.session_state.data.sort_values('date', ascending=False),
        hide_index=True
    )

    # Add a clear data button
    if st.button("Clear All Data"):
        st.session_state.data = pd.DataFrame({'date': [], 'score': []})
        save_data(st.session_state.data)
        st.success("All data has been cleared!")
else:
    st.info("No data yet! Use the sidebar to add your first entry.")