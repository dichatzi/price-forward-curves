import requests
import json
import pandas as pd
import datetime
import time
import sys

# Import custom .py file
sys.path.insert(0, "E://Scripts//Operations//Utilities")
from dcUtils import connectToDB, MergeTableSQL


class eexForwards():
    def __init__(self, area, product, product_type, starting_date, ending_date, connection):
        self.headers = self.create_headers()
        self.area = area
        self.product = product
        self.product_type = product_type
        self.starting_date = starting_date
        self.ending_date = ending_date
        self.connection = connection

        self.url = self.create_url()
        self.data = self.send_request()


    def create_headers(self):
        headers = dict()
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        headers['Sec-Fetch-Mode'] = 'cors'
        headers['Origin'] = 'https://www.eex.com'
        headers['Referer'] = 'https://www.eex.com/en/market-data/power/futures/hungarian-futures'

        return headers

    def create_url(self):
        # Create dictionaries
        area_codes = {"GR": "F", "HU": "9", "BG": "K", "IT": "D"}
        product_types = {"Baseload": "B", "Peak": "P"}

        # Initialize parameters
        area = area_codes[self.area]
        product = self.product
        product_type = product_types[self.product_type]
        starting_date = self.starting_date.replace("-", "%2F")
        ending_date = self.ending_date.replace("-", "%2F")

        # Create url
        url = f"https://webservice-eex.gvsi.com/query/json/getDaily/close/offexchtradevolumeeex/onexchtradevolumeeex/tradedatetimegmt/?priceSymbol=%22%2FE.F{area}{product_type}{product}%22&chartstartdate={starting_date}&chartstopdate={ending_date}&dailybarinterval=Days&aggregatepriceselection=Last"

        return url

    def send_request(self):
        # Send request
        response = requests.get(self.url, headers=self.headers)

        data = []
        if response.status_code == 200:
            # Get retrieved data
            retrieved_data = json.loads(response.text)
            results = retrieved_data["results"]
            items = results["items"]

            # Create data dataframe
            data = pd.DataFrame(data=items)

            # Process dataframe
            if not data.empty:
                data["tradedatetimegmt"] = data["tradedatetimegmt"].apply(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y %I:%M:%S %p").strftime("%Y-%m-%d"))
                data.fillna(0, inplace=True)
                data.insert(0, "biddingArea", area)
                data.insert(0, "productType", self.product_type)
                data.insert(0, "productCode", product_name)
                data = data.rename(columns={"close": "closePrice"})

                try:
                    database_data = MergeTableSQL(dataframe=data, connection=self.connection.connection, table_name="[market_data].[eex_power_forwards]",
                                                  on_fields=["productCode", "productType", "biddingArea", "tradedatetimegmt"], upd_fields=["closePrice", "offexchtradevolumeeex", "onexchtradevolumeeex"])
                    database_data.merge_table()
                except:
                    print(f"Data for product {self.product} could not be uploaded to database ...")

            else:
                print("Request response was 200 but no data exist ...")
        else:
            print("Request response was 400. Operation aborted ...")

        return data

# Set database connection
conn = connectToDB(database="heron_epm", password="Dipbsia_01", username="heron_analyst", servername="10.124.21.72")

# Create dates
starting_date = (datetime.datetime.now() + datetime.timedelta(days=-5)).strftime("%Y-%m-%d")
ending_date = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime("%Y-%m-%d")

current_year = datetime.datetime.now().year - 2000

# Set bidding areas
bidding_areas = ["GR", "HU", "BG", "IT"]

# Set product types
product_types = ["Baseload", "Peak"]

# Create monthly products
m_products_names = ["MF", "MG", "MH", "MJ", "MK", "MM", "MN", "MQ", "MU", "MV", "MX", "MZ"]
m_products_years = [str(current_year + y) for y in range(2)]

# Create quarter products
q_products_names = ["QF", "QJ", "QN", "QV"]
q_products_years = [str(current_year + y) for y in range(3)]

# Create yearly products
y_products_years = [str(current_year + y) for y in range(5)]

# Start timer
start_time = time.time()

for area in bidding_areas:
    for product_type in product_types:

        # Get yearly products
        for year in y_products_years:
            # Create yearly product name
            product_name = "YF" + year

            print(f"Product {product_name} ({product_type}) ............................")
            power_eex = eexForwards(area=area, product=product_name, product_type=product_type,
                                    starting_date=starting_date, ending_date=ending_date, connection=conn)

        # Get quarterly products
        for year in q_products_years:
            for product in q_products_names:
                # Create quarterly product name
                product_name = str(product) + str(year)

                print(f"Product {product_name} ({product_type}) ............................")
                power_eex = eexForwards(area=area, product=product_name, product_type=product_type,
                                        starting_date=starting_date, ending_date=ending_date, connection=conn)

        # Get monthly products
        for year in m_products_years:
            for product in m_products_names:
                # Create monthly product name
                product_name = str(product) + str(year)

                print(f"Product {product_name} ({product_type}) ............................")
                power_eex = eexForwards(area=area, product=product_name, product_type=product_type,
                                        starting_date=starting_date, ending_date=ending_date, connection=conn)


# End time
end_time = time.time()
print(f"Total execution time: {round(end_time - start_time, 2)} sec")

# url = "https://webservice-eex.gvsi.com/query/json/getDaily/close/offexchtradevolumeeex/onexchtradevolumeeex/tradedatetimegmt/?priceSymbol=%22%2FE.F9BQF22%22&chartstartdate=2021%2F10%2F04&chartstopdate=2021%2F11%2F19&dailybarinterval=Days&aggregatepriceselection=Last"


