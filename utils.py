import streamlit as st

def get_year_selection(key_suffix=''):
    """Common function to get year selection with consistent range"""
    return st.sidebar.selectbox(
        "Select Year",
        range(2024, 2017, -1),
        key=f'year_{key_suffix}'
    )

def format_time(seconds):
    """Format time in seconds to appropriate format"""
    if seconds >= 60:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:06.3f}"
    return f"{seconds:.3f}s" 