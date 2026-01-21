# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL


def extract_features_df(
    df,
    w=24,
    z_thr=3.0,
    ewma_alpha=0.1
):
    """
    Extract rolling time-series features from a pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DatetimeIndex (hourly), columns = signals (e.g. zones).
        Should already be detrended / STL residuals.
    w : int
        Rolling window size (in hours).
    z_thr : float
        Z-score threshold for anomaly rate.
    ewma_alpha : float
        Alpha for EWMA volatility.

    Returns
    -------
    features : pd.DataFrame
        Feature table aligned on time.
    """

    features = []

    for col in df.columns:
        s = df[col].astype(float)
        f = pd.DataFrame(index=s.index)

        roll = s.rolling(w)

        # -----------------------
        # Level & dispersion
        # -----------------------
        f["mean"] = roll.mean()
        f["std"] = roll.std()

        # Robust MAD
        f["mad"] = roll.apply(
            lambda x: np.median(np.abs(x - np.median(x))),
            raw=True
        )

        # -----------------------
        # Rolling quantiles for robust spike detection
        # -----------------------
        f["q25"] = roll.quantile(0.25)
        f["q75"] = roll.quantile(0.75)
        f["iqr"] = f["q75"] - f["q25"]

        # -----------------------
        # Anomalies
        # -----------------------
        z = (s - f["mean"]) / f["std"]
        f["z_abs"] = z.abs()

        f["anomaly_rate"] = (
            z.abs()
             .rolling(w)
             .apply(lambda x: (x > z_thr).mean(), raw=True)
        )

        # Robust z-score (MAD)
        rz = (s - roll.median()) / (1.4826 * f["mad"])
        f["rz_abs"] = rz.abs()

        # -----------------------
        # Volatility
        # -----------------------
        f["vol_rolling"] = f["std"]

        f["vol_ewma"] = (
            s.sub(s.mean())
             .abs()
             .ewm(alpha=ewma_alpha)
             .mean()
        )

        # -----------------------
        # Temporal structure & Lags
        # -----------------------
        f["acf1"] = roll.apply(
            lambda x: pd.Series(x).autocorr(lag=1)
        )

        f["acf2"] = roll.apply(
            lambda x: pd.Series(x).autocorr(lag=2)
        )

        # Lag features (day and week)
        f["lag24"] = s.shift(24)
        f["lag168"] = s.shift(168)
        f["lag24_delta"] = s.diff(24)
        f["lag168_delta"] = s.diff(168)

        # -----------------------
        # Day-of-week / hour-of-day normalized anomalies
        # -----------------------
        # Group by (weekday, hour) and compute baseline mean/std from rolling window
        dow_hour = s.index.to_series().apply(
            lambda t: (t.weekday(), t.hour)
        )
        f["dow_hour_z"] = 0.0  # placeholder

        for (dow, hod), idx_group in s.groupby(dow_hour).groups.items():
            if len(idx_group) > 1:
                group_vals = s.loc[idx_group]
                group_mean = group_vals.mean()
                group_std = group_vals.std()
                if group_std > 0:
                    f.loc[idx_group, "dow_hour_z"] = (
                        (s.loc[idx_group] - group_mean) / group_std
                    )

        # -----------------------
        # Regime / change proxy
        # -----------------------
        f["mean_shift"] = f["mean"].diff().abs()

        # Prefix column names
        f.columns = [f"{col}_{c}" for c in f.columns]

        features.append(f)

    features = pd.concat(features, axis=1)

    return features

def analyze_day(
    df,
    day,
    w=48,
    stl_period=24,
    tz="UTC",
    history_hours=24 * 30,
    quantiles=(0.1, 0.5, 0.9),
    spike_pctl=0.95
):
    """
    Analyze one day of a time series using historical context.

    Parameters
    ----------
    df : pd.Series or pd.DataFrame
        Full dataset (DatetimeIndex, hourly).
    day : str or pd.Timestamp
        Day to analyze (YYYY-MM-DD).
    w : int
        Rolling window for hourly features (hours).
    stl_period : int
        STL seasonality period.
    tz : str
        Target timezone.
    history_hours : int
        How much history to consider when building features (e.g., 24*30 for ~1 month).
    quantiles : tuple
        Quantiles to summarize the target day distribution per column.
    spike_pctl : float
        Percentile on the historical window used as a spike threshold.

    Returns
    -------
    day_features : pd.DataFrame
        Features for the selected day (hourly).
    """

    # --- Normalize to DataFrame and timezone
    if isinstance(df, pd.Series):
        df = df.to_frame(name=getattr(df, "name", "value"))

    if df.index.tz is None:
        df = df.tz_localize(tz)
    else:
        df = df.tz_convert(tz)

    day_ts = pd.Timestamp(day, tz=tz)
    day_start = day_ts.normalize()
    day_end = day_start + pd.Timedelta(days=1)

    # --- Use history window up to end of day
    hist_start = day_end - pd.Timedelta(hours=history_hours)
    df_hist = df.loc[hist_start:day_end]

    # --- STL residuals
    resid = pd.DataFrame(index=df_hist.index)

    for c in df_hist.columns:
        stl = STL(df_hist[c], period=stl_period, robust=True)
        resid[c] = stl.fit().resid

    # --- Feature extraction
    X = extract_features_df(resid, w=w)

    # --- Keep only target day
    day_features = X.loc[day_start:day_end].dropna().copy()

    # --- Calendar context
    day_features["weekday"] = day_features.index.weekday
    day_features["hour"] = day_features.index.hour

    # --- Day-level distribution and spike/ramp metrics per column
    day_slice = df.loc[day_start:day_end]

    if not day_features.empty:
        for c in df.columns:
            s_day = day_slice[c].dropna()
            s_hist = df_hist[c].dropna()

            q_vals = s_day.quantile(quantiles) if len(s_day) else pd.Series([np.nan] * len(quantiles))
            neg_share = (s_day < 0).mean() if len(s_day) else np.nan

            spike_thr = s_hist.quantile(spike_pctl) if len(s_hist) else np.nan
            spike_share = (s_day > spike_thr).mean() if spike_thr == spike_thr else np.nan

            ramp = s_day.diff()
            ramp_mean = ramp.mean() if len(ramp) else np.nan
            ramp_std = ramp.std() if len(ramp) else np.nan
            ramp_max_abs = ramp.abs().max() if len(ramp) else np.nan

            # Lag features for the target day
            lag24_vals = df.loc[(df.index >= day_start - pd.Timedelta(hours=24)) & 
                               (df.index < day_end - pd.Timedelta(hours=24)), c].dropna()
            lag168_vals = df.loc[(df.index >= day_start - pd.Timedelta(hours=168)) & 
                                (df.index < day_end - pd.Timedelta(hours=168)), c].dropna()
            
            lag24_mean = lag24_vals.mean() if len(lag24_vals) else np.nan
            lag168_mean = lag168_vals.mean() if len(lag168_vals) else np.nan
            
            day_vs_lag24 = (s_day.mean() - lag24_mean) if len(s_day) and lag24_mean == lag24_mean else np.nan
            day_vs_lag168 = (s_day.mean() - lag168_mean) if len(s_day) and lag168_mean == lag168_mean else np.nan

            day_features[f"{c}_day_mean"] = s_day.mean() if len(s_day) else np.nan
            day_features[f"{c}_day_min"] = s_day.min() if len(s_day) else np.nan
            day_features[f"{c}_day_max"] = s_day.max() if len(s_day) else np.nan
            day_features[f"{c}_day_q{int(quantiles[0]*100)}"] = q_vals.iloc[0]
            day_features[f"{c}_day_q{int(quantiles[1]*100)}"] = q_vals.iloc[1]
            day_features[f"{c}_day_q{int(quantiles[2]*100)}"] = q_vals.iloc[2]
            day_features[f"{c}_neg_share"] = neg_share
            day_features[f"{c}_spike_share"] = spike_share
            day_features[f"{c}_ramp_mean"] = ramp_mean
            day_features[f"{c}_ramp_std"] = ramp_std
            day_features[f"{c}_ramp_max_abs"] = ramp_max_abs
            day_features[f"{c}_lag24_mean"] = lag24_mean
            day_features[f"{c}_lag168_mean"] = lag168_mean
            day_features[f"{c}_day_vs_lag24"] = day_vs_lag24
            day_features[f"{c}_day_vs_lag168"] = day_vs_lag168

    """
    day_features DataFrame Structure:
    ===================================
    
    24 rows (one per hour of the target day, indexed by timestamp)
    
    For each price column (e.g., "value"), the following features are included:
    
    === Hourly Rolling Features (from extract_features_df on STL residuals) ===
    {col}_mean              : Rolling mean over w hours (baseline level)
    {col}_std               : Rolling std over w hours (short-term volatility)
    {col}_mad               : Median Absolute Deviation (robust to outliers)
    {col}_q25               : 25th percentile over w hours
    {col}_q75               : 75th percentile over w hours
    {col}_iqr               : Inter-quartile range (robust spread metric)
    {col}_z_abs             : Absolute z-score (how many std from mean)
    {col}_anomaly_rate      : % of hours in window with |z| > z_thr (default 3.0)
    {col}_rz_abs            : Robust z-score using MAD (resistant to extreme values)
    {col}_vol_rolling       : Rolling volatility (= std)
    {col}_vol_ewma          : Exponential moving avg of absolute deviations (recent vol emphasis)
    {col}_acf1              : Autocorrelation at lag 1 (t vs t-1)
    {col}_acf2              : Autocorrelation at lag 2 (t vs t-2)
    {col}_lag24             : Price value from 24 hours ago
    {col}_lag168            : Price value from 168 hours ago (7 days)
    {col}_lag24_delta       : Price change over past 24 hours (t - t-24)
    {col}_lag168_delta      : Price change over past 168 hours (t - t-168)
    {col}_dow_hour_z        : Z-score normalized by day-of-week + hour-of-day baseline
                              (removes diurnal/weekly seasonality)
    {col}_mean_shift        : Absolute change in rolling mean (regime change signal)
    
    === Calendar Context ===
    weekday                 : Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday)
    hour                    : Hour of day (0=00:00, 1=01:00, ..., 23=23:00)
    
    === Day-Level Statistics ===
    {col}_day_mean          : Average price for the target day
    {col}_day_min           : Minimum price during the target day
    {col}_day_max           : Maximum price during the target day
    {col}_day_q10           : 10th percentile of prices that day
    {col}_day_q50           : Median price that day
    {col}_day_q90           : 90th percentile of prices that day
    
    === Price Regime Indicators ===
    {col}_neg_share         : Share of hours with negative prices (0.0 to 1.0)
    {col}_spike_share       : Share of hours exceeding 30-day 95th percentile
    
    === Intra-Day Volatility ===
    {col}_ramp_mean         : Average hour-to-hour price change
    {col}_ramp_std          : Volatility of hour-to-hour changes
    {col}_ramp_max_abs      : Largest single-hour price jump (absolute value)
    
    === Lag-Based Momentum & Seasonality ===
    {col}_lag24_mean        : Average price 24 hours ago (yesterday, same time)
    {col}_lag168_mean       : Average price 168 hours ago (7 days ago, same weekday)
    {col}_day_vs_lag24      : Today's avg - Yesterday's avg (day momentum)
    {col}_day_vs_lag168     : Today's avg - Last week's avg (weekly seasonality)
    """

    return day_features