import streamlit as st
import fastf1
import plotly.express as px
import numpy as np
from utils import get_year_selection, format_time

def show_telemetry_page():
    st.title("Telemetry Analysis")
    
    # Year selection using common function
    year = get_year_selection('telemetry')
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Loading race calendar...")
        progress_bar.progress(10)
        
        # Load race schedule for selected year
        schedule = fastf1.get_event_schedule(year)
        race_names = schedule['EventName'].tolist()
        selected_race = st.sidebar.selectbox("Select Race", race_names, key='telemetry_race')
        
        # Session selection
        session_types = {
            'Practice 1': 'FP1',
            'Practice 2': 'FP2',
            'Practice 3': 'FP3',
            'Qualifying': 'Q',
            'Sprint Shootout': 'SQ',
            'Sprint': 'S',
            'Race': 'R'
        }
        selected_session = st.sidebar.selectbox("Select Session", list(session_types.keys()), key='telemetry_session')
        
        status_text.text("Loading session data...")
        progress_bar.progress(30)
        
        # Load session data
        session = fastf1.get_session(year, selected_race, session_types[selected_session])
        session.load()
        
        progress_bar.progress(50)
        status_text.text("Processing driver data...")
        
        # Driver selection
        drivers = session.drivers
        driver_info = {session.get_driver(driver)['Abbreviation']: session.get_driver(driver)['FullName'] 
                      for driver in drivers}
        selected_driver = st.sidebar.selectbox("Select Driver", list(driver_info.keys()),
                                             format_func=lambda x: f"{x} - {driver_info[x]}")
        
        status_text.text(f"Loading {selected_driver}'s lap data...")
        progress_bar.progress(60)
        
        # Get driver's laps
        driver_laps = session.laps.pick_driver(selected_driver)
        
        # Get fastest lap
        fastest_lap = driver_laps.pick_fastest()
        
        # Convert lap numbers to integers and sort them
        lap_numbers = sorted([int(np.floor(lap)) for lap in driver_laps['LapNumber'].unique()])
        lap_options = ["Fastest Lap"] + [f"Lap {lap}" for lap in lap_numbers]
        selected_lap = st.sidebar.selectbox("Select Lap", lap_options)
        
        status_text.text("Processing telemetry data...")
        progress_bar.progress(70)
        
        # Get telemetry data based on lap selection
        if selected_lap == "Fastest Lap":
            telemetry = fastest_lap.get_telemetry()
            lap_time = fastest_lap['LapTime'].total_seconds()
            st.header(f"{selected_session} Fastest Lap Telemetry for {driver_info[selected_driver]}")
            st.subheader(f"Lap Time: {format_time(lap_time)}")
        else:
            lap_number = int(selected_lap.split()[1])
            # Find the first matching lap (in case of partial laps)
            matching_laps = driver_laps[driver_laps['LapNumber'].apply(lambda x: int(np.floor(x))) == lap_number]
            if not matching_laps.empty:
                lap_data = matching_laps.iloc[0]
                telemetry = lap_data.get_telemetry()
                lap_time = lap_data['LapTime'].total_seconds()
                st.header(f"{selected_session} {selected_lap} Telemetry for {driver_info[selected_driver]}")
                st.subheader(f"Lap Time: {format_time(lap_time)}")
            else:
                raise ValueError(f"Lap {lap_number} not found for {selected_driver}")
        
        status_text.text("Generating visualizations...")
        progress_bar.progress(80)
        
        # Convert distance to kilometers for better readability
        telemetry['Distance_KM'] = telemetry['Distance'] / 1000
        
        # Speed plot
        fig_speed = px.line(telemetry, x='Distance_KM', y='Speed',
                           title='Speed Telemetry',
                           labels={'Distance_KM': 'Distance (km)',
                                 'Speed': 'Speed (km/h)'})
        st.plotly_chart(fig_speed)
        
        progress_bar.progress(90)
        
        # Throttle plot
        fig_throttle = px.line(telemetry, x='Distance_KM', y='Throttle',
                              title='Throttle Application',
                              labels={'Distance_KM': 'Distance (km)',
                                    'Throttle': 'Throttle %'})
        st.plotly_chart(fig_throttle)
        
        # Brake plot
        fig_brake = px.line(telemetry, x='Distance_KM', y='Brake',
                           title='Brake Application',
                           labels={'Distance_KM': 'Distance (km)',
                                 'Brake': 'Brake %'})
        st.plotly_chart(fig_brake)
        
        # Clear progress indicators
        progress_bar.progress(100)
        status_text.empty()
    
    except Exception as e:
        # Clear progress indicators in case of error
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
            
        st.error(f"Error loading session data: {str(e)}")
        if "Event Schedule" in str(e):
            st.info("Note: Race schedule for the selected year might not be available yet.")
        else:
            st.info("Note: Not all sessions may be available for all races.")