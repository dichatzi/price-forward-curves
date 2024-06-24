# Import basic libraries
import pandas as pd
from pyomo.environ import *
import math

# Load user defined libraries
from DataLoader import *



bid_relaxation = 1
ask_relaxation = 1


y = 2024

# Yearly parameters
BEST_BID_BASE_YEAR = BestBidBase_Year[y] - bid_relaxation
BEST_ASK_BASE_YEAR = BestAskBase_Year[y] + ask_relaxation
BEST_BID_PEAK_YEAR = BestBidPeak_Year[y] - bid_relaxation
BEST_ASK_PEAK_YEAR = BestAskPeak_Year[y] + ask_relaxation


# Monthly parameters
BEST_BID_BASE_MONTH = dict()
BEST_ASK_BASE_MONTH = dict()
BEST_BID_PEAK_MONTH = dict()
BEST_ASK_PEAK_MONTH = dict()

for m in range(1, 13):
	
    if (y,m) in BestBidBase_Month.keys() and not math.isnan(BestBidBase_Month[(y,m)]):
        BEST_BID_BASE_MONTH[m] = BestBidBase_Month[(y,m)] - bid_relaxation
		
    if (y,m) in BestAskBase_Month.keys() and not math.isnan(BestAskBase_Month[(y,m)]):
        BEST_ASK_BASE_MONTH[m] = BestAskBase_Month[(y,m)] + ask_relaxation
		
    if (y,m) in BestBidPeak_Month.keys() and not math.isnan(BestBidPeak_Month[(y,m)]):
        BEST_BID_PEAK_MONTH[m] = BestBidPeak_Month[(y,m)] - bid_relaxation
		
    if (y,m) in BestAskPeak_Month.keys() and not math.isnan(BestAskPeak_Month[(y,m)]):
        BEST_ASK_PEAK_MONTH[m] = BestAskPeak_Month[(y,m)] + ask_relaxation


# Quarterly parameters
BEST_BID_BASE_QUARTER = dict()
BEST_ASK_BASE_QUARTER = dict()
BEST_BID_PEAK_QUARTER = dict()
BEST_ASK_PEAK_QUARTER = dict()

for q in range(1, 5):
	
    if (y,q) in BestBidBase_Quarter.keys() and not math.isnan(BestBidBase_Quarter[(y,q)]):
        BEST_BID_BASE_QUARTER[q] = BestBidBase_Quarter[(y,q)] - bid_relaxation
		
    if (y,q) in BestAskBase_Quarter.keys() and not math.isnan(BestAskBase_Quarter[(y,q)]):
        BEST_ASK_BASE_QUARTER[q] = BestAskBase_Quarter[(y,q)] + ask_relaxation
		
    if (y,q) in BestBidPeak_Quarter.keys() and not math.isnan(BestBidPeak_Quarter[(y,q)]):
        BEST_BID_PEAK_QUARTER[q] = BestBidPeak_Quarter[(y,q)] - bid_relaxation
		
    if (y,q) in BestAskPeak_Quarter.keys() and not math.isnan(BestAskPeak_Quarter[(y,q)]):
        BEST_ASK_PEAK_QUARTER[q] = BestAskPeak_Quarter[(y,q)] + ask_relaxation



""" ===========================================================================
MODEL =========================================================================
"""
# Define model parameters
lambda_h = 1
lambda_d = 1
MinPerc = 0.2
MaxPerc = 0.2

# Define model
model = ConcreteModel(name="PriceForwardCurves")

# Activate duals
model.dual = Suffix(direction=Suffix.IMPORT)

# Define Sets
hour_ids_yb = [h for h in range(1,max_hours+1)]
hour_ids_yp = [h for h in hour_ids if Periods[h] > 8 and Periods[h] < 21]

# m.T = Set(initialize=hours)

model.H = Set(initialize=hour_ids)					# Set of trading hours (1 to 8784)
model.HYB = Set(initialize=hour_ids_yb)				# Set of trading hours belonging to yearly baseload
model.HYP = Set(initialize=hour_ids_yp)				# Set of trading hours belonging to yearly peak

# m.HP = Set(initialize=hids_yp)
# m.D = Set(initialize=WeekDayNames)
model.TD = Set(initialize=day_ids)				# Set of trading days (1 to 365)
model.M = Set(initialize=months)
model.Q = Set(initialize=quarters)



"""
VARIABLES
"""
model.f = Var(model.H)
model.fd = Var(model.TD)

model.fm_b = Var(model.M, within=Reals)          # Real variable denoting the average monthly prive of all baseload hours
model.fm_p = Var(model.M, within=Reals)          # Real variable denoting the average monthly prive of all peak hours
model.fq_b = Var(model.Q, within=Reals)
model.fq_p = Var(model.Q, within=Reals)
model.p_y = Var(within=Reals)



"""
EQUATIONS
"""
# Define objective function
def objective_function(model):
	return sum( (model.f[h] - Price[h]) * (model.f[h] - Price[h]) for h in model.H) + \
			lambda_h * sum( (model.f[h-1] - 2 * model.f[h] + model.f[h+1]) * (model.f[h-1] - 2 * model.f[h] + model.f[h+1]) for h in model.H if h > 1 and h < len(model.H) ) + \
			lambda_d * sum( (model.fd[td-1] - 2 * model.fd[td] + model.fd[td+1]) * (model.fd[td-1] - 2 * model.fd[td] + model.fd[td+1]) for td in model.TD if td > 1 and td < len(model.TD) )
model.obj = Objective(rule=objective_function, sense=minimize)


def minimum_hourly_limit(model, h):
	return (1 - MinPerc) * sum(Ih2d[h,td] * model.fd[td] for td in model.TD) <= model.f[h]
model.minimum_hourly_limit = Constraint(model.H, rule=minimum_hourly_limit)


def maximum_hourly_limit(model, h):
	return model.f[h] <= (1 + MaxPerc) * sum(Ih2d[h,td] * model.fd[td] for td in model.TD)
model.maximum_hourly_limit = Constraint(model.H, rule=maximum_hourly_limit)


# Define yearly constraints
def bid_limit_base_year(model):
	if not math.isnan(BEST_BID_BASE_YEAR):
		return BEST_BID_BASE_YEAR <= sum(model.f[h] for h in model.HYB) / len(model.HYB)
	else:
		return Constraint.Skip
model.bid_limit_base_year = Constraint(rule=bid_limit_base_year)

def ask_limit_base_year(model):
	if not math.isnan(BEST_ASK_BASE_YEAR):
		return sum(model.f[h] for h in model.HYB) / len(model.HYB) <= BEST_ASK_BASE_YEAR
	else:
		return Constraint.Skip
model.ask_limit_base_year = Constraint(rule=ask_limit_base_year)

def bid_limit_peak_year(model):
	if not math.isnan(BEST_BID_PEAK_YEAR):
		return BEST_BID_PEAK_YEAR <= sum(model.f[h] for h in model.HYP) / len(model.HYP)
	else:
		return Constraint.Skip
model.bid_limit_peak_year = Constraint(rule=bid_limit_peak_year)

def ask_limit_peak_year(model):
	if not math.isnan(BEST_ASK_PEAK_YEAR):
		return sum(model.f[h] for h in model.HYP) / len(model.HYP) <= BEST_ASK_PEAK_YEAR
	else:
		return Constraint.Skip
model.ask_limit_peak_year = Constraint(rule=ask_limit_peak_year)


# Define monthly constraints
def bid_limit_base_month(model, m):
	if m in BEST_BID_BASE_MONTH.keys():
		return BEST_BID_BASE_MONTH[m] <= model.fm_b[m]
	else:
		return Constraint.Skip
model.bid_limit_base_month = Constraint(model.M, rule=bid_limit_base_month)

def ask_limit_base_month(model, m):
	if m in BEST_ASK_BASE_MONTH.keys():
		return model.fm_b[m] <= BEST_ASK_BASE_MONTH[m]
	else:
		return Constraint.Skip
model.ask_limit_base_month = Constraint(model.M, rule=ask_limit_base_month)

def bid_limit_peak_month(model, m):
	if m in BEST_BID_PEAK_MONTH.keys():
		return BEST_BID_PEAK_MONTH[m] <= model.fm_p[m]
	else:
		return Constraint.Skip
model.bid_limit_peak_month = Constraint(model.M, rule=bid_limit_peak_month)

def ask_limit_peak_month(model, m):
	if m in BEST_ASK_PEAK_MONTH.keys():
		return model.fm_p[m] <= BEST_ASK_PEAK_MONTH[m]
	else:
		return Constraint.Skip
model.ask_limit_peak_month = Constraint(model.M, rule=ask_limit_peak_month)


# Define quarterly constraints
def bid_limit_base_quarter(model, q):
	if q in BEST_BID_BASE_QUARTER.keys():
		return BEST_BID_BASE_QUARTER[q] <= model.fq_b[q]
	else:
		return Constraint.Skip
model.bid_limit_base_quarter = Constraint(model.Q, rule=bid_limit_base_quarter)

def ask_limit_base_quarter(model, q):
	if q in BEST_ASK_BASE_QUARTER.keys():
		return model.fq_b[q] <= BEST_ASK_BASE_QUARTER[q]
	else:
		return Constraint.Skip
model.ask_limit_base_quarter = Constraint(model.Q, rule=ask_limit_base_quarter)

def bid_limit_peak_quarter(model, q):
	if q in BEST_BID_PEAK_QUARTER.keys():
		return BEST_BID_PEAK_QUARTER[q] <= model.fq_p[q]
	else:
		return Constraint.Skip
model.bid_limit_peak_quarter = Constraint(model.Q, rule=bid_limit_peak_quarter)

def ask_limit_peak_quarter(model, q):
	if q in BEST_ASK_PEAK_QUARTER.keys():
		return model.fq_p[q] <= BEST_ASK_PEAK_QUARTER[q]
	else:
		return Constraint.Skip
model.ask_limit_peak_quarter = Constraint(model.Q, rule=ask_limit_peak_quarter)





# Define average prices
def daily_forward_price(model, td):
	return model.fd[td] == sum(Ih2d[h,td] * model.f[h] for h in model.H) / 24
model.daily_forward_price = Constraint(model.TD, rule=daily_forward_price)

def monthly_average_baseload_prices(model, m):
	return model.fm_b[m] == sum(Ih2m_b[h,m] * model.f[h] for h in model.H) / Tm_b[m]
model.monthly_average_baseload_prices = Constraint(model.M, rule=monthly_average_baseload_prices)

def monthly_average_peak_prices(model, m):
	return model.fm_p[m] == sum(Ih2m_p[h,m] * model.f[h] for h in model.H) / Tm_p[m]
model.monthly_average_peak_prices = Constraint(model.M, rule=monthly_average_peak_prices)

def quarterly_average_baseload_prices(model, q):
	return model.fq_b[q] == sum(Ih2q_b[h,q] * model.f[h] for h in model.H) / Tq_b[q]
model.quarterly_average_baseload_prices = Constraint(model.Q, rule=quarterly_average_baseload_prices)

def quarterly_average_peak_prices(model, q):
	return model.fq_p[q] == sum(Ih2q_p[h,q] * model.f[h] for h in model.H) / Tq_p[q]
model.quarterly_average_peak_prices = Constraint(model.Q, rule=quarterly_average_peak_prices)


# Set solver
# ipopt_path = "/opt/homebrew/bin/ipopt"
ipopt_path = "C://Ipopt//bin//ipopt.exe"

solver = SolverFactory("ipopt", executable=ipopt_path)


# Solve model
solver.solve(model, tee=True)



""" ===========================================================================
RESULTS =======================================================================
"""
# Define output files
OUTPUT_PRICE_FORWARD_CURVES = "./Output Data/price_forward_curve.csv"

# Open output price forward curve file and write new 
with open(OUTPUT_PRICE_FORWARD_CURVES, "w") as file:
	
	# Write header
	file.write("Hour ID,Year,Quarter,Month,Day,Hour,Original Price,New Price\n")
	
    # Write data
	for h in model.H:
		new_price = round(value(model.f[h]), 3)
		file.write(f"{h},{TradingYear[h]},{TradingQuarter[h]},{TradingMonth[h]},{TradingDay[h]},{TradingHour[h]},{Price[h]},{new_price}\n")


for m in model.M:
	print(f"[Baseload] Month: {m}: {round(value(model.fm_b[m]), 2)}")
	
print("----------------")
for m in model.M:
	print(f"[Peak] Month: {m}: {round(value(model.fm_p[m]), 2)}")

print("====================")
print("====================")
for q in model.Q:
	print(f"[Baseload] Quarter: {q}: {round(value(model.fq_b[q]), 2)}")
	
print("----------------")
for q in model.Q:
	print(f"[Peak] Quarter: {q}: {round(value(model.fq_p[q]), 2)}")
