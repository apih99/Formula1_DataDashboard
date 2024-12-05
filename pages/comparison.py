import streamlit as st
import fastf1
import plotly.graph_objects as go
import numpy as np
from utils import get_year_selection, format_time

def show_comparison_page():
    st.title("Driver Comparison Analysis")
    
    # Year selection using common function
    year = get_year_selection('comparison')
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Loading race calendar...")
        progress_bar.progress(10)
        
        # Load race schedule for selected year
        schedule = fastf1.get_event_schedule(year)
        race_names = schedule['EventName'].tolist()
        selected_race = st.sidebar.selectbox("Select Race", race_names, key='comparison_race')
        
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
        selected_session = st.sidebar.selectbox("Select Session", list(session_types.keys()), key='comparison_session')
        
        status_text.text("Loading session data...")
        progress_bar.progress(20)
        
        # Load session data
        session = fastf1.get_session(year, selected_race, session_types[selected_session])
        session.load()
        
        progress_bar.progress(40)
        status_text.text("Processing driver data...")
        
        # Get all drivers
        drivers = session.drivers
        driver_info = {session.get_driver(driver)['Abbreviation']: session.get_driver(driver)['FullName'] 
                      for driver in drivers}
        
        # Create two columns for driver selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Driver 1")
            driver1 = st.selectbox("Select First Driver", 
                                 list(driver_info.keys()),
                                 format_func=lambda x: f"{x} - {driver_info[x]}",
                                 key='driver1')
            
            status_text.text(f"Loading {driver1}'s telemetry...")
            progress_bar.progress(50)
            
            # Get driver 1's laps
            driver1_laps = session.laps.pick_driver(driver1)
            driver1_fastest = driver1_laps.pick_fastest()
            
            # Convert lap numbers using numpy floor
            lap_numbers1 = driver1_laps['LapNumber'].unique()
            lap_numbers1 = sorted([int(np.floor(x)) for x in lap_numbers1])
            lap_options1 = ["Fastest Lap"] + [f"Lap {lap}" for lap in lap_numbers1]
            selected_lap1 = st.selectbox("Select Lap", lap_options1, key='lap1')
        
        with col2:
            st.subheader("Driver 2")
            driver2 = st.selectbox("Select Second Driver", 
                                 [d for d in list(driver_info.keys()) if d != driver1],
                                 format_func=lambda x: f"{x} - {driver_info[x]}",
                                 key='driver2')
            
            status_text.text(f"Loading {driver2}'s telemetry...")
            progress_bar.progress(60)
            
            # Get driver 2's laps
            driver2_laps = session.laps.pick_driver(driver2)
            driver2_fastest = driver2_laps.pick_fastest()
            
            # Convert lap numbers using numpy floor
            lap_numbers2 = driver2_laps['LapNumber'].unique()
            lap_numbers2 = sorted([int(np.floor(x)) for x in lap_numbers2])
            lap_options2 = ["Fastest Lap"] + [f"Lap {lap}" for lap in lap_numbers2]
            selected_lap2 = st.selectbox("Select Lap", lap_options2, key='lap2')
        
        status_text.text("Processing telemetry data...")
        progress_bar.progress(70)
        
        # Get telemetry data for both drivers
        if selected_lap1 == "Fastest Lap":
            telemetry1 = driver1_fastest.get_telemetry().copy()
            lap_time1 = driver1_fastest['LapTime'].total_seconds()
        else:
            lap_number1 = int(selected_lap1.split()[1])
            # Find the matching lap using numpy floor
            matching_laps1 = driver1_laps[driver1_laps['LapNumber'].apply(lambda x: int(np.floor(x))) == lap_number1]
            if not matching_laps1.empty:
                lap_data1 = matching_laps1.iloc[0]
                telemetry1 = lap_data1.get_telemetry().copy()
                lap_time1 = lap_data1['LapTime'].total_seconds()
            else:
                raise ValueError(f"Lap {lap_number1} not found for {driver1}")
        
        if selected_lap2 == "Fastest Lap":
            telemetry2 = driver2_fastest.get_telemetry().copy()
            lap_time2 = driver2_fastest['LapTime'].total_seconds()
        else:
            lap_number2 = int(selected_lap2.split()[1])
            # Find the matching lap using numpy floor
            matching_laps2 = driver2_laps[driver2_laps['LapNumber'].apply(lambda x: int(np.floor(x))) == lap_number2]
            if not matching_laps2.empty:
                lap_data2 = matching_laps2.iloc[0]
                telemetry2 = lap_data2.get_telemetry().copy()
                lap_time2 = lap_data2['LapTime'].total_seconds()
            else:
                raise ValueError(f"Lap {lap_number2} not found for {driver2}")
        
        progress_bar.progress(80)
        status_text.text("Preparing visualization...")
        
        # Ensure consistent data types for X, Y, Z columns
        for col in ['X', 'Y', 'Z']:
            if col in telemetry1.columns:
                telemetry1[col] = telemetry1[col].astype(float)
            if col in telemetry2.columns:
                telemetry2[col] = telemetry2[col].astype(float)
        
        # Convert distance to kilometers
        telemetry1['Distance_KM'] = telemetry1['Distance'] / 1000
        telemetry2['Distance_KM'] = telemetry2['Distance'] / 1000
        
        # Display lap times with new formatting
        time_delta = abs(lap_time1 - lap_time2)
        st.markdown(f"""
        #### Lap Times:
        - **{driver1}**: {format_time(lap_time1)}
        - **{driver2}**: {format_time(lap_time2)}
        - **Delta**: {format_time(time_delta)}
        """)
        
        progress_bar.progress(90)
        status_text.text("Generating plots...")
        
        # Create comparison plots
        def create_comparison_plot(y_variable, title, y_label):
            fig = go.Figure()
            
            # Add traces for both drivers
            fig.add_trace(go.Scatter(x=telemetry1['Distance_KM'], y=telemetry1[y_variable],
                                   name=f"{driver1}", line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=telemetry2['Distance_KM'], y=telemetry2[y_variable],
                                   name=f"{driver2}", line=dict(color='red')))
            
            # Update layout
            fig.update_layout(title=title,
                            xaxis_title='Distance (km)',
                            yaxis_title=y_label,
                            hovermode='x unified')
            return fig
        
        # Speed comparison
        st.plotly_chart(create_comparison_plot('Speed', 'Speed Comparison', 'Speed (km/h)'))
        
        # Throttle comparison
        st.plotly_chart(create_comparison_plot('Throttle', 'Throttle Application Comparison', 'Throttle %'))
        
        # Brake comparison
        st.plotly_chart(create_comparison_plot('Brake', 'Brake Application Comparison', 'Brake %'))
        
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