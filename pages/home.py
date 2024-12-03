import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting

def show_home_page():
    st.title("F1 Data Analysis Dashboard")
    
    st.markdown("""
    Welcome to the F1 Data Analysis Dashboard! This application allows you to analyze Formula 1 race data in various ways.
    
    ### Available Features:
    
    1. **Telemetry Analysis**
       - View detailed telemetry data for any driver
       - Analyze speed, throttle, and brake data
       - Compare different laps from the same session
    
    2. **Driver Comparison**
       - Compare telemetry data between two drivers
       - Analyze speed differences
       - Compare throttle and brake usage
    
    3. **Position Changes**
       - Track position changes throughout a race
       - Visualize overtakes and position gains/losses
    
    ### How to Use:
    
    1. Select a page from the sidebar menu
    2. Choose the year and race you want to analyze
    3. Select the specific session (Practice, Qualifying, or Race)
    4. Pick the driver(s) you want to analyze
    5. Explore the data through interactive charts
    
    ### Data Source:
    
    This application uses the FastF1 package to access official Formula 1 timing data.
    The data is cached locally for faster access in subsequent queries.
    
    ### Note:
    
    - Some sessions might not be available immediately after a race weekend
    - Data availability might vary for different years and sessions
    - The first load of a session might take some time as data needs to be downloaded
    """) 