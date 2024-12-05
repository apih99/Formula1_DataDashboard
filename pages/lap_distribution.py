import streamlit as st
import fastf1
import fastf1.plotting
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def show_lap_distribution_page():
    st.title("Lap Time Distribution Analysis")
    
    # Session selection
    year = st.selectbox("Select Year", range(2024, 2017, -1))
    
    # Get list of races for the selected year
    with st.spinner("Loading race calendar..."):
        fastf1.Cache.enable_cache('cache')
        schedule = fastf1.get_event_schedule(year)
        races = schedule['EventName'].tolist()
    selected_race = st.selectbox("Select Race", races)
    
    # Session type selection
    session_type = st.selectbox("Select Session", ['R', 'Q', 'SQ', 'FP1', 'FP2', 'FP3'])
    

    if st.button("Generate Distribution Plot"):
        try:
            # Create a placeholder for the progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Load the session
            status_text.text("Loading session data...")
            progress_bar.progress(10)
            
            session = fastf1.get_session(year, selected_race, session_type)
            progress_bar.progress(30)
            
            status_text.text("Processing lap times...")
            session.load()
            progress_bar.progress(50)
            
            point_finishers = session.drivers[:10]
            driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
            driver_laps = driver_laps.reset_index()
            progress_bar.progress(70)

            finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]
            
            # Get lap times for all drivers
            status_text.text("Generating visualization...")
            lap_times = session.laps
            progress_bar.progress(80)
            
            # create the figure
            fig, ax = plt.subplots(figsize=(10, 5))

            # Seaborn doesn't have proper timedelta support,
            # so we have to convert timedelta to float (in seconds)
            driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

            sns.violinplot(data=driver_laps,
                           x="Driver",
                           y="LapTime(s)",
                           hue="Driver",
                           inner=None,
                           density_norm="area",
                           order=finishing_order,
                           palette=fastf1.plotting.get_driver_color_mapping(session=session)
               )

            sns.swarmplot(data=driver_laps,
              x="Driver",
              y="LapTime(s)",
              order=finishing_order,
              hue="Compound",
              palette=fastf1.plotting.get_compound_mapping(session=session),
              hue_order=["SOFT", "MEDIUM", "HARD"],
              linewidth=0,
              size=4,
              )
            
            ax.set_xlabel("Driver")
            ax.set_ylabel("Lap Time (s)")
            plt.suptitle(f"{selected_race} {session_type} Lap Time Distributions")
            sns.despine(left=True, bottom=True)

            plt.tight_layout()
            progress_bar.progress(90)
            
            # Display plot in Streamlit
            st.pyplot(plt)
            
            # Display summary statistics
            status_text.text("Calculating statistics...")
            st.subheader("Lap Time Summary Statistics")
            summary = lap_times.groupby('Driver')['LapTime'].agg(['mean', 'min', 'max', 'count']).reset_index()
            summary['mean'] = summary['mean'].dt.total_seconds()
            summary['min'] = summary['min'].dt.total_seconds()
            summary['max'] = summary['max'].dt.total_seconds()
            summary.columns = ['Driver', 'Mean Time (s)', 'Best Time (s)', 'Worst Time (s)', 'Lap Count']
            st.dataframe(summary)
            
            # Clear the progress indicators
            progress_bar.progress(100)
            status_text.empty()
            
        except Exception as e:
            # Clear the progress indicators in case of error
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
                
            st.error(f"An error occurred while loading the data: {str(e)}")
            st.info("This could be due to:\n"
                   "- The selected session data not being available yet\n"
                   "- Network connectivity issues\n"
                   "- Invalid session type for this race weekend")