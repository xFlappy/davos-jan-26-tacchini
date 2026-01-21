# imports
import pandas as pd
import numpy as np
import os
import volue_insight_timeseries
from dotenv import load_dotenv
import matplotlib.pyplot as plt


def initialize_session(client_id: str = None, client_secret: str = None):
    """
    Initialize and return a Volue Insight API session.
    
    Args:
        client_id: API client ID (defaults to env var VOLUE_CLIENT_ID)
        client_secret: API client secret (defaults to env var VOLUE_CLIENT_SECRET)
    
    Returns:
        volue_insight_timeseries.Session object
    """
    # Load from environment variables
    load_dotenv()
    cid = os.getenv("VOLUE_CLIENT_ID")
    csecret = os.getenv("VOLUE_CLIENT_SECRET")
    
    if not cid or not csecret:
        raise ValueError("Missing VOLUE_CLIENT_ID or VOLUE_CLIENT_SECRET")
    
    session = volue_insight_timeseries.Session(
        client_id=cid,
        client_secret=csecret
    )
    print("Authentication succeeded. Session returned.")
    return session

def get_curve(session, curve_name: str):
    """
    Retrieve a curve object by name.
    
    Args:
        session: Authenticated Volue session
        curve_name: Full curve name (e.g., 'pri ch spot ec00 €/mwh cet h f')
    
    Returns:
        Curve object with metadata
    """
    curve = session.get_curve(name=curve_name)
    print(f"Curve fetched correctly! Curve ID: {curve.id}, Type: {curve.curve_type}")
    return curve

def select_data(curve, data_from, data_to):
    """
    Select time series data from a curve within a date range.
    
    Args:
        curve: Curve object from get_curve()
        data_from: Start date (YYYY-MM-DD or timestamp)
        data_to: End date (YYYY-MM-DD or timestamp)
    
    Returns:
        pandas DataFrame with time series data
    """
    print(f"Selecting data from {data_from} to {data_to}...")
    ts = curve.get_data(data_from=data_from, data_to=data_to)
    df = ts.to_pandas()
    print(f"Retrieved {len(df)} data points.")
    return df

# def select_instances(
#     curve,
#     issue_date_from: str,
#     issue_date_to: str,
#     with_data: bool = True
# ):
#     """
#     Search and retrieve curve instances within a date range.
    
#     Args:
#         curve: Curve object from get_curve()
#         issue_date_from: Start date (YYYY-MM-DD or timestamp)
#         issue_date_to: End date (YYYY-MM-DD or timestamp)
#         with_data: Whether to include time series data
    
#     Returns:
#         List of TimeSeriesInstance objects (call .to_pandas() on each)
#     """
#     print(f"Searching instances from {issue_date_from} to {issue_date_to}...")
#     instances = curve.search_instances(
#         issue_date_from=issue_date_from,
#         issue_date_to=issue_date_to,
#         with_data=with_data
#     )
#     print(f"Found {len(instances)} instance(s)")
#     return instances

# def instance_to_dataframe(instance):
#     """
#     Convert a TimeSeriesInstance to a pandas DataFrame.
    
#     Args:
#         instance: TimeSeriesInstance object
    
#     Returns:
#         pandas DataFrame with time series data
#     """
#     df = instance.to_pandas()
#     print("Conversion to dataframe succeeded.")
#     return df

def plot_dataframe(df):
    """
    Plot time series data from a DataFrame.
    
    Args:
        df: pandas DataFrame with time series data
    """
    
    print("Plotting data...")
    df.plot()
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.title("Time Series Data")
    plt.show()
    print("Plotting completed.")
