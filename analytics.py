import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# ---------------- Z-SCORE ----------------
def compute_zscore(series, window=30):
    """
    Compute rolling Z-score for a price series
    """
    if len(series) < window:
        return series * np.nan

    mean = series.rolling(window).mean()
    std = series.rolling(window).std()

    return (series - mean) / std


# ---------------- SPREAD ----------------
def compute_spread(df, sym1, sym2):
    """
    Compute price spread between two symbols
    """
    s1 = df[df.symbol == sym1]["price"].reset_index(drop=True)
    s2 = df[df.symbol == sym2]["price"].reset_index(drop=True)

    min_len = min(len(s1), len(s2))
    if min_len == 0:
        return s1 * np.nan

    return s1[:min_len] - s2[:min_len]


# ---------------- ROLLING CORRELATION ----------------
def rolling_correlation(df, sym1, sym2, window=30):
    """
    Compute rolling correlation between two price series
    """
    s1 = df[df.symbol == sym1]["price"].reset_index(drop=True)
    s2 = df[df.symbol == sym2]["price"].reset_index(drop=True)

    min_len = min(len(s1), len(s2))
    if min_len < window:
        return s1 * np.nan

    return s1[:min_len].rolling(window).corr(s2[:min_len])


# ---------------- ADF TEST ----------------
def adf_test(series):
    """
    Perform Augmented Dickey-Fuller test
    Returns p-value
    """
    series = series.dropna()
    if len(series) < 20:
        return np.nan

    result = adfuller(series)
    return result[1]  # p-value


# ---------------- OLS HEDGE RATIO ----------------
def hedge_ratio_ols(df, sym1, sym2):
    """
    Compute hedge ratio using OLS regression
    """
    s1 = df[df.symbol == sym1]["price"].reset_index(drop=True)
    s2 = df[df.symbol == sym2]["price"].reset_index(drop=True)

    min_len = min(len(s1), len(s2))
    if min_len < 30:
        return None

    X = sm.add_constant(s2[:min_len])
    model = sm.OLS(s1[:min_len], X).fit()

    return model.params[1]

def rolling_hedge_ratio(df, sym1, sym2, window=60):
    """
    Compute rolling OLS hedge ratio
    """
    s1 = df[df.symbol == sym1]["price"].reset_index(drop=True)
    s2 = df[df.symbol == sym2]["price"].reset_index(drop=True)

    min_len = min(len(s1), len(s2))
    if min_len < window:
        return s1 * np.nan

    ratios = [np.nan] * window

    for i in range(window, min_len):
        y = s1[i-window:i]
        x = sm.add_constant(s2[i-window:i])
        model = sm.OLS(y, x).fit()
        ratios.append(model.params[1])

    return ratios
