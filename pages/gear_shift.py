import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np

def show_gear_shift_page():
    st.title("Gear Shift Analysis")
    
    # Session selection
    year = st.selectbox("Select Year", range(2024, 2017, -1))
    
    # Get list of races for the selected year
    with st.spinner("Loading race calendar..."):
        fastf1.Cache.enable_cache('cache')
        schedule = fastf1.get_event_schedule(year)
        races = schedule['EventName'].tolist()
    selected_race = st.selectbox("Select Race", races)
    
    # Session type selection
    session_type = st.selectbox("Select Session", ['Q', 'R', 'SQ', 'FP1', 'FP2', 'FP3'])
    
    # Driver selection
    drivers = ['VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA', 'ALO', 'STR',
               'GAS', 'OCO', 'ALB', 'SAR', 'BOT', 'ZHO', 'TSU', 'RIC', 'MAG', 'HUL']
    selected_driver = st.selectbox("Select Driver", drivers)

    if st.button("Generate Gear Shift Visualization"):
        try:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Load session data
            status_text.text("Loading session data...")
            progress_bar.progress(10)
            
            session = fastf1.get_session(year, selected_race, session_type)
            progress_bar.progress(30)
            
            status_text.text("Processing telemetry data...")
            session.load()
            progress_bar.progress(50)
            
            # Get fastest lap for selected driver
            driver_laps = session.laps.pick_driver(selected_driver)
            if len(driver_laps) == 0:
                raise ValueError(f"No lap data found for {selected_driver}")
                
            fastest_lap = driver_laps.pick_fastest()
            if fastest_lap is None:
                raise ValueError(f"No valid fastest lap found for {selected_driver}")
                
            progress_bar.progress(60)
            
            # Get telemetry data
            status_text.text("Getting telemetry data...")
            telemetry = fastest_lap.get_telemetry()
            if telemetry is None or len(telemetry) == 0:
                raise ValueError("No telemetry data available for this lap")
                
            progress_bar.progress(70)
            
            # Prepare the plot
            status_text.text("Generating visualization...")
            fastf1.plotting.setup_mpl(mpl_timedelta_support=True)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create colormap for gears
            num_gears = len(np.unique(telemetry['nGear']))
            cmap = plt.cm.get_cmap('RdYlBu_r')
            
            # Plot the circuit with color-coded gears
            points = ax.scatter(telemetry['X'], telemetry['Y'],
                              c=telemetry['nGear'], 
                              cmap=cmap,
                              s=30,
                              vmin=1,
                              vmax=8)
            
            # Add colorbar
            cbar = plt.colorbar(points)
            cbar.set_label('Gear')
            
            # Set title and labels
            plt.title(f"Fastest Lap Gear Shift Visualization\n{selected_driver} - {selected_race} {year}")
            ax.set_xlabel("X Position (m)")
            ax.set_ylabel("Y Position (m)")
            
            # Set aspect ratio to equal for true track shape
            ax.set_aspect('equal')
            
            progress_bar.progress(90)
            
            # Display the plot
            st.pyplot(fig)
            
            # Display fastest lap information
            st.subheader("Fastest Lap Information")
            lap_info = {
                "Lap Time": str(fastest_lap['LapTime']),
                "Lap Number": int(fastest_lap['LapNumber']) if 'LapNumber' in fastest_lap else None,
                "Compound": fastest_lap['Compound'] if 'Compound' in fastest_lap else None,
                "Stint": int(fastest_lap['Stint']) if 'Stint' in fastest_lap else None,
                "Fresh Tyre": "Yes" if fastest_lap.get('FreshTyre', False) else "No",
                "DRS Activations": len(telemetry[telemetry['DRS'] > 0]) if 'DRS' in telemetry else "N/A"
            }
            
            # Filter out None values
            lap_info = {k: v for k, v in lap_info.items() if v is not None}
            
            st.json(lap_info)
            
            # Clear progress indicators
            progress_bar.progress(100)
            status_text.empty()
            
        except Exception as e:
            # Clear progress indicators in case of error
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
                
            st.error(f"An error occurred while loading the data: {str(e)}")
            st.info("This could be due to:\n"
                   "- The selected session data not being available yet\n"
                   "- Network connectivity issues\n"
                   "- Invalid session type for this race weekend\n"
                   "- Selected driver did not participate in this session")