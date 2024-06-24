import pandas as pd
from pyomo.environ import *
from DataLoader import *


# Load data
# prices_data = pd.read_csv("./historical_prices.csv")
# print(prices_data)

# Define model parameters
BestBid = 152.2
BestAsk = 152.2
BestBid_Peak = 165.62
BestAsk_Peak = 165.62

lambda_h = 1
lambda_d = 1
MinPerc = 1 
MaxPerc = 1


# Get dates
# days = prices_data["DAY"].drop_duplicates()


# Define set related parameters
WeekDayNames = ["Monday", "Tuseday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]




""" ===========================================================================
PARAMETERS ====================================================================
"""
# Define prices
# Price = dict()
# for r in range(prices_data.shape[0]):
# 	hour = prices_data["ID"].iloc[r]
# 	price = prices_data["INPUT"].iloc[r]

# 	Price[hour] = price

# Define trading hour per time unit
# Periods = dict()
# hour_counter = 0
# for r in range(prices_data.shape[0]):
# 	hour_counter = hour_counter + 1
# 	hour = prices_data["ID"].iloc[r]

# 	Periods[hour] = hour_counter

# 	if hour_counter == 24:
# 		hour_counter = 0




""" ===========================================================================
MODEL =========================================================================
"""
# Define model
m = ConcreteModel(name="PriceForwardCurves")

# Activate duals
m.dual = Suffix(direction=Suffix.IMPORT)

# Define Sets
hids = [h for h in range(1,max_hours+1)]
hour_ids_yp = [h for h in hour_ids if Periods[h] > 8 and Periods[h] < 21]

# m.T = Set(initialize=hours)

m.H = Set(initialize=hour_ids)					# Set of trading hours (1 to 8784)
m.HYP = Set(initialize=hour_ids_yp)				# Set of trading hours belonging to yearly peak

# m.HP = Set(initialize=hids_yp)
# m.D = Set(initialize=WeekDayNames)
m.TD = Set(initialize=day_ids)				# Set of trading days (1 to 365)
# m.Y = Set(initialize=years)
# m.M = Set(initialize=months)


"""
PARAMETERS
"""
# Define time unit to trading unit incidence matrix
# Ih2d = {(h,d): 0 for h in m.H for d in m.TD}
# for r in range(prices_data.shape[0]):
# 	hour = prices_data["ID"].iloc[r]
# 	trading_day = prices_data["DAY"].iloc[r]

# 	Ih2d[(hour,trading_day)] = 1


"""
VARIABLES
"""
m.f = Var(m.H)
m.fd = Var(m.TD)


"""
EQUATIONS
"""
# Define objective function
def objective_function(m):
	return sum( (m.f[h] - Price[h]) * (m.f[h] - Price[h]) for h in m.H) + \
			lambda_h * sum( (m.f[h-1] - 2 * m.f[h] + m.f[h+1]) * (m.f[h-1] - 2 * m.f[h] + m.f[h+1]) for h in m.H if h > 1 and h < len(m.H) ) + \
			lambda_d * sum( (m.fd[td-1] - 2 * m.fd[td] + m.fd[td+1]) * (m.fd[td-1] - 2 * m.fd[td] + m.fd[td+1]) for td in m.TD if td > 1 and td < len(m.TD) )
m.obj = Objective(rule=objective_function, sense=minimize)


def minimum_hourly_limit(m, h):
	return (1 - MinPerc) * sum(Ih2d[h,td] * m.fd[td] for td in m.TD) <= m.f[h]
m.minimum_hourly_limit = Constraint(m.H, rule=minimum_hourly_limit)


def maximum_hourly_limit(m, h):
	return m.f[h] <= (1 + MaxPerc) * sum(Ih2d[h,td] * m.fd[td] for td in m.TD)
m.maximum_hourly_limit = Constraint(m.H, rule=maximum_hourly_limit)


def bid_limit(m):
	return BestBid <= sum(m.f[h] for h in m.H) / len(m.H)
m.bid_limit = Constraint(rule=bid_limit)


def ask_limit(m):
	return sum(m.f[h] for h in m.H) / len(m.H) <= BestAsk
m.ask_limit = Constraint(rule=ask_limit)


def bid_limit_peak(m):
	return BestBid_Peak <= sum(m.f[h] for h in m.HYP) / len(m.HYP)
m.bid_limit_peak = Constraint(rule=bid_limit_peak)


def ask_limit_peak(m):
	return sum(m.f[h] for h in m.HYP) / len(m.HYP) <= BestAsk_Peak
m.ask_limit_peak = Constraint(rule=ask_limit_peak)


def daily_forward_price(m, td):
	return m.fd[td] == sum(Ih2d[h,td] * m.f[h] for h in m.H) / 24
m.daily_forward_price = Constraint(m.TD, rule=daily_forward_price)



# Set solver
ipopt_path = "/opt/homebrew/bin/ipopt"
solver = SolverFactory("ipopt", executable=ipopt_path)


# Solve model
solver.solve(m, tee=True)




""" ===========================================================================
RESULTS =======================================================================
"""
sum_of_prices = 0

for h in m.H:
	new_price = round(value(m.f[h]), 3)
	sum_of_prices = sum_of_prices + new_price
	print(f"[{h}] Historical price: {Price[h]} -> New price: {new_price}")

average_price = round(sum_of_prices / len(m.H), 2)

print(f"Average price: {average_price}")

print("====================================================================")
# for h in m.HP:
# 	print(h)
# print(hours)
# print(hids)

# print(hour_ids_yp)


with open('./price_forward_curve.csv', 'w') as file:
	file.write("hour,original_price,new_price\n")
	for h in m.H:
		new_price = round(value(m.f[h]), 3)
		file.write(f"{h},{Price[h]},{new_price}\n")