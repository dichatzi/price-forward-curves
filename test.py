import pandas as pd
import math


"""
READ INPUT DATA
"""
# Get monthly forwards
monthly_forwards_data = pd.read_csv("./Input Data/monthly_forwards.csv")

monthly_forwards = dict()
for r in range(monthly_forwards_data.shape[0]):
    year = monthly_forwards_data["YEAR"].iloc[r]
    month = monthly_forwards_data["MONTH"].iloc[r]
    bid_base = monthly_forwards_data["BID_BASE"].iloc[r]

    if not math.isnan(bid_base):
        monthly_forwards[(year,month)] = bid_base






# Get time-series data
time_series_data = pd.read_csv("./Input Data/time_series_data.csv")

# Get dimensions
no_periods = time_series_data["PERIOD"].drop_duplicates()
no_months = time_series_data["MONTH"].drop_duplicates()
no_quarters = time_series_data["QUARTER"].drop_duplicates()

# Create dictionaries
Price = dict()
FixedPrice = dict()
Ih2m = {(h,m): 0 for h in range(1,no_periods+1) for m in range(1,no_months+1)}
Ih2q = {(h,q): 0 for h in range(1,no_periods+1) for q in range(1,no_quarters+1)}

for r in range(time_series_data.shape[0]):
    
    # Get data
    period = time_series_data["PERIOD"].iloc[r]
    date = time_series_data["DATE"].iloc[r]
    nameday = time_series_data["NAMEDAY"].iloc[r]
    year = time_series_data["YEAR"].iloc[r]
    month = time_series_data["MONTH"].iloc[r]
    quarter = time_series_data["QUARTER"].iloc[r]
    day = time_series_data["DAY"].iloc[r]
    hour = time_series_data["HOUR"].iloc[r]
    actual_price = time_series_data["ACTUAL"].iloc[r]
    historical_price = time_series_data["HISTORICAL"].iloc[r]

    # Get prices
    if not math.isnan(historical_price):
        Price[period] = round(historical_price, 2)
        FixedPrice[period] = 0
    else:
        Price[period] = 0
        FixedPrice[period] = round(actual_price, 2)

    # Update incidence matrices
    Ih2m[(period,month)] = 1
    Ih2q[(period,quarter)] = 1


print(Price)
