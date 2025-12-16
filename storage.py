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

    resampled = (
        df.set_index("timestamp")
        .groupby("symbol")
        .resample(timeframe)
        .agg(
            price=("price", "last"),
            volume=("size", "sum")
        )
        .reset_index()
    )

    # ✅ Critical fix: forward-fill price PER SYMBOL
    resampled["price"] = (
        resampled
        .groupby("symbol")["price"]
        .ffill()
    )

    # Drop rows where price is still missing (initial buckets)
    resampled = resampled.dropna(subset=["price"])

    return resampled


    

