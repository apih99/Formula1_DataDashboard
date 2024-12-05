import streamlit as st
import fastf1
import os
from pages.home import show_home_page
from pages.telemetry import show_telemetry_page
from pages.comparison import show_comparison_page
from pages.position_changes import show_position_changes_page
from pages.lap_distribution import show_lap_distribution_page
from pages.gear_shift import show_gear_shift_page
# Create cache directory if it doesn't exist
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Enable FastF1 cache
fastf1.Cache.enable_cache(cache_dir)

# Hide specific elements while keeping the Navigation section
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
.css-1d391kg {display: none;}
div[data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

def main():
    # Create a navigation menu
    st.sidebar.title("Navigation")
    pages = {
        "Home": show_home_page,
        "Telemetry Analysis": show_telemetry_page,
        "Driver Comparison": show_comparison_page,
        "Position Changes": show_position_changes_page,
        "Lap Time Distribution": show_lap_distribution_page,
        "Gear Shift Analysis": show_gear_shift_page
    }
    
    # Let the user select the page
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    
    # Call the selected page function
    pages[selection]()

if __name__ == "__main__":
    main() 