import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "telemetry_history.db"

def init_db():
    """
    Creates the SQLite database and metrics table if they don't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            total_ram_mb REAL,
            avg_cpu_percent REAL,
            active_processes INTEGER,
            high_waste_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_telemetry(df: pd.DataFrame):
    """
    Extracts summary metrics from current dataframe and logs to SQLite.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_ram = float(df['ram_mb'].sum())
    avg_cpu = float(df['cpu_percent'].mean())
    active_procs = len(df)
    high_waste = len(df[df['waste_score'] > 200])

    cursor.execute('''
        INSERT INTO system_metrics (timestamp, total_ram_mb, avg_cpu_percent, active_processes, high_waste_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, total_ram, avg_cpu, active_procs, high_waste))

    conn.commit()
    conn.close()

def get_historical_data(limit: int = 50) -> pd.DataFrame:
    """
    Retrieves the most recent historical telemetry records.
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"""
        SELECT timestamp, avg_cpu_percent, total_ram_mb, high_waste_count 
        FROM system_metrics 
        ORDER BY id DESC 
        LIMIT {limit}
    """
    df_history = pd.read_sql_query(query, conn)
    conn.close()
    
    # Sort chronologically for line chart rendering
    if not df_history.empty:
        df_history = df_history.iloc[::-1].reset_index(drop=True)
        
    return df_history