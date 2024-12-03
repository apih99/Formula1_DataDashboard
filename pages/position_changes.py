import streamlit as st
import fastf1
import plotly.graph_objects as go
import pandas as pd
from utils import get_year_selection
import matplotlib.pyplot as plt
import fastf1.plotting

def show_position_changes_page():
    st.title("Race Position Changes Analysis")
    
    # Year selection using common function
    year = get_year_selection('position')
    
    try:
        # Load race schedule for selected year
        schedule = fastf1.get_event_schedule(year)
        race_names = schedule['EventName'].tolist()
        selected_race = st.sidebar.selectbox("Select Race", race_names, key='pos_race')
        
        with st.spinner('Loading race data...'):
            # Load race session with minimal data
            session = fastf1.get_session(year, selected_race, 'R')
            session.load()
            
            # Create position changes plot
            fig = go.Figure()
            
            # Get teams and their drivers
            team_drivers = {}
            for drv in session.drivers:
                drv_laps = session.laps.pick_driver(drv)
                if not drv_laps.empty:
                    team = drv_laps['Team'].iloc[0]
                    if team not in team_drivers:
                        team_drivers[team] = []
                    team_drivers[team].append(drv)
            
            # Add traces for each driver
            for team, drivers in team_drivers.items():
                for i, drv in enumerate(drivers):
                    drv_laps = session.laps.pick_driver(drv)
                    
                    if not drv_laps.empty:
                        # Get driver's abbreviation and full name
                        abb = drv_laps['Driver'].iloc[0]
                        driver_full_name = session.get_driver(abb)['FullName']
                        
                        # Get FastF1's built-in driver styling
                        style = fastf1.plotting.get_driver_style(identifier=abb,
                                                               style=['color'],
                                                               session=session)
                        
                        # Alternate between solid and dash for teammates
                        line_style = 'solid' if i == 0 else 'dash'
                        
                        # Create the line plot with F1 styling
                        fig.add_trace(go.Scatter(
                            x=drv_laps['LapNumber'],
                            y=drv_laps['Position'],
                            name=f"{abb} - {driver_full_name}",
                            line=dict(
                                color=style['color'],
                                dash=line_style
                            ),
                            mode='lines',
                            hovertemplate="Lap: %{x}<br>Position: %{y}<br>%{text}",
                            text=[f"{abb} - {driver_full_name} ({team})" for _ in range(len(drv_laps))]
                        ))
            
            # Update layout
            fig.update_layout(
                title=f"Position Changes - {selected_race} {year}",
                xaxis_title="Lap",
                yaxis_title="Position",
                yaxis=dict(
                    autorange="reversed",
                    range=[20.5, 0.5],
                    ticktext=['1', '5', '10', '15', '20'],
                    tickvals=[1, 5, 10, 15, 20]
                ),
                height=800,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=1.02,
                    xanchor="left",
                    x=1.0
                ),
                hovermode='x unified'
            )
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Add race statistics
            st.subheader("Race Statistics")
            
            # Calculate position changes for each driver
            driver_stats = []
            for drv in session.drivers:
                drv_laps = session.laps.pick_driver(drv)
                if not drv_laps.empty:
                    abb = drv_laps['Driver'].iloc[0]
                    driver_full_name = session.get_driver(abb)['FullName']
                    team = drv_laps['Team'].iloc[0]
                    
                    start_pos = drv_laps['Position'].iloc[0]
                    end_pos = drv_laps['Position'].iloc[-1]
                    
                    # Handle NaN values
                    if pd.isna(start_pos) or pd.isna(end_pos):
                        continue
                        
                    positions_gained = int(start_pos - end_pos)
                    
                    driver_stats.append({
                        'Driver': f"{abb} - {driver_full_name}",
                        'Team': team,
                        'Start': int(start_pos),
                        'Finish': int(end_pos),
                        'Positions Gained/Lost': positions_gained
                    })
            
            # Display statistics as a table
            st.dataframe(
                pd.DataFrame(driver_stats)
                .sort_values(['Team', 'Finish'])
                .reset_index(drop=True),
                hide_index=True
            )
    
    except Exception as e:
        st.error(f"Error loading race data: {str(e)}")
        if "Event Schedule" in str(e):
            st.info("Note: Race schedule for the selected year might not be available yet.")
        else:
            st.info("Note: Position changes analysis is only available for race sessions.") 