import pandas as pd

SAFE_PROCESSES = ['systemd', 'xorg', 'gnome-shell', 'code', 'python', 'python3', 'streamlit']

def calculate_waste_score(df):
    """
    Calculates safety score, waste score, and flags safe processes.
    """
    if df.empty:
        return df

    # Flag safe system/dev processes
    df['is_safe'] = df['name'].str.lower().apply(lambda x: any(sp in str(x) for sp in SAFE_PROCESSES))
    
    # Simple Waste Score calculation (RAM MB + CPU %)
    df['waste_score'] = df['ram_mb'] + (df['cpu_percent'] * 10)
    
    return df