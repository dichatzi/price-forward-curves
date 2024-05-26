import pandas as pd
import math


"""
READ INPUT DATA
"""
# Get monthly forwards
monthly_forwards_data = pd.read_csv("./Input Data/monthly_forwards.csv")

BestBidBase_Month = dict()
BestAskBase_Month = dict()
BestBidPeak_Month = dict()
BestAskPeak_Month = dict()
for r in range(monthly_forwards_data.shape[0]):
    year = monthly_forwards_data["YEAR"].iloc[r]
    month = monthly_forwards_data["MONTH"].iloc[r]
    bid_base = monthly_forwards_data["BID_BASE"].iloc[r]
    ask_base = monthly_forwards_data["ASK_BASE"].iloc[r]
    bid_peak = monthly_forwards_data["BID_PEAK"].iloc[r]
    ask_peak = monthly_forwards_data["ASK_PEAK"].iloc[r]

    if not math.isnan(bid_base):
        BestBidBase_Month[(year,month)] = bid_base
        BestAskBase_Month[(year,month)] = ask_base
        BestBidPeak_Month[(year,month)] = bid_peak
        BestAskPeak_Month[(year,month)] = ask_peak


# Get quarterly forwards
quarterly_forwards_data = pd.read_csv("./Input Data/quarterly_forwards.csv")

BestBidBase_Quarter = dict()
BestAskBase_Quarter = dict()
BestBidPeak_Quarter = dict()
BestAskPeak_Quarter = dict()
for r in range(quarterly_forwards_data.shape[0]):
    year = quarterly_forwards_data["YEAR"].iloc[r]
    quarter = quarterly_forwards_data["QUARTER"].iloc[r]
    bid_base = quarterly_forwards_data["BID_BASE"].iloc[r]
    ask_base = quarterly_forwards_data["ASK_BASE"].iloc[r]
    bid_peak = quarterly_forwards_data["BID_PEAK"].iloc[r]
    ask_peak = quarterly_forwards_data["ASK_PEAK"].iloc[r]

    if not math.isnan(bid_base):
        BestBidBase_Quarter[(year,quarter)] = bid_base
        BestAskBase_Quarter[(year,quarter)] = ask_base
        BestBidPeak_Quarter[(year,quarter)] = bid_peak
        BestAskPeak_Quarter[(year,quarter)] = ask_peak


# Get yearly forwards
yearly_forwards_data = pd.read_csv("./Input Data/yearly_forwards.csv")

BestBidBase_Year = dict()
BestAskBase_Year = dict()
BestBidPeak_Year = dict()
BestAskPeak_Year = dict()
for r in range(yearly_forwards_data.shape[0]):
    year = yearly_forwards_data["YEAR"].iloc[r]
    bid_base = yearly_forwards_data["BID_BASE"].iloc[r]
    ask_base = yearly_forwards_data["ASK_BASE"].iloc[r]
    bid_peak = yearly_forwards_data["BID_PEAK"].iloc[r]
    ask_peak = yearly_forwards_data["ASK_PEAK"].iloc[r]

    if not math.isnan(bid_base):
        BestBidBase_Year[year] = bid_base
        BestAskBase_Year[year] = ask_base
        BestBidPeak_Year[year] = bid_peak
        BestAskPeak_Year[year] = ask_peak



# Get time-series data
time_series_data = pd.read_csv("./Input Data/time_series_data.csv")

# Get data series
hour_ids = time_series_data["HOUR_ID"].drop_duplicates().values
# months = time_series_data["MONTH"].drop_duplicates()
# quarters = time_series_data["QUARTER"].drop_duplicates()
# years = time_series_data["YEAR"].drop_duplicates()
# days = time_series_data["DAY"].drop_duplicates()
# hours = time_series_data["HOUR"].drop_duplicates()
day_ids = time_series_data["DAY_ID"].drop_duplicates().values

# Get dimensions
max_hours = max(hour_ids)

# Create dictionaries
Price = dict()
FixedPrice = dict()
# Ih2m = {(h,m): 0 for h in hour_ids for m in months}
# Ih2q = {(h,q): 0 for h in hour_ids for q in quarters}
Ih2d = {(h,d): 0 for h in hour_ids for d  in day_ids}
Periods = {p: 0 for p in hour_ids}

for r in range(time_series_data.shape[0]):
    
    # Get data
    day_id = time_series_data["DAY_ID"].iloc[r]
    hour_id = time_series_data["HOUR_ID"].iloc[r]
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
        Price[hour_id] = round(historical_price, 2)
        FixedPrice[hour_id] = 0
    else:
        Price[hour_id] = 0
        FixedPrice[hour_id] = round(actual_price, 2)

    # Update incidence matrices
    # Ih2m[(hour_id,month)] = 1
    # Ih2q[(hour_id,quarter)] = 1
    Ih2d[(hour_id,day_id)] = 1

    # Define additional parameters
    Periods[hour_id] = hour


print(Periods)
