import pandas as pd
import threading

# Thread-safe in-memory storage
_ticks = []
_lock = threading.Lock()

def store_tick(tick: dict):
    """Store a single tick safely"""
    with _lock:
        _ticks.append(tick)

def get_ticks_df():
    """Return a DataFrame copy of stored ticks"""
    with _lock:
        if not _ticks:
            return pd.DataFrame()
        data_copy = list(_ticks)

    df = pd.DataFrame(data_copy)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def resample_ticks(df, timeframe="1s"):
    if df.empty:
        return df

    # Ensure timestamp is datetime
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")

    # Resample per symbol
    resampled = (
        df.groupby("symbol")
          .resample(timeframe)
          .agg(
              price=("price", "last"),
              volume=("size", "sum")
          )
          .dropna()
    )

    # 🔴 CRITICAL: bring index levels back as columns
    resampled = resampled.reset_index()

    return resampled

    
