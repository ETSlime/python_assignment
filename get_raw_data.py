import requests
import json
import pymysql
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import cryptography

"""
Retrieve and process the row data from the Alpha Vantage API.
Args:
    company: the company name which you want to retrive, could not provide if you know the symbol
    symbol: the symobol corresponding to the related company
Returns:
    A list of financial data points
"""
def get_raw_data(company = None, symbol = None):
    # get the best match of the symbol of the company name
    if symbol is None:
        try:
            symbol = requests.get('https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + company + '&apikey=' + apiKey).json()['bestMatches'][0]['1. symbol']
        except:
            print('Error: could not get the symbol of company: ' + company)
            exit()

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+ symbol + '&apikey=' + apiKey
    r = requests.get(url)
    data = r.json()

    try: 
        current_date = data['Meta Data']['3. Last Refreshed']
        period = 14
        json_content_list = []
        # get the data of most recently two weeks
        for time, data_point in data['Time Series (Daily)'].items():
            if ( (datetime.strptime(current_date , '%Y-%m-%d') - datetime.strptime(time, '%Y-%m-%d')).days <= period):
                # process the raw API data response
                json_content_list.append({'symbol':symbol, 'date':time, 'open_price':data_point['1. open'], 'close_price':data_point['4. close'], 'volume':data_point['6. volume']})
    except:
        print("Get " + company + " data error: please check your apikey. The standard API call frequency is 5 calls per minute and 500 calls per day.")
        exit()
    return json_content_list


"""
Initialize the database, read the schema.sql to create the financial_data table
Returns:
    the connector and the cursor of the database
"""
def init_db():
    # connect to mysql server
    conn = pymysql.connect(host='database',
                     user='root',
                     password= os.environ.get("DB_PASSWORD"),
                     database=None)
    
    cursor = conn.cursor()

    # create financial_data table if not exist
    with open(os.getcwd() + "/schema.sql", "r") as schema:
        for query in schema.read().split(";"):
            cursor.execute(query)

    return conn, cursor


if __name__ == "__main__":
    # get the apiKey for retrieving data
    load_dotenv(dotenv_path='.env')
    apiKey = os.environ.get('API_KEY')
    if apiKey is None:
        print("your aipKey is not set.")
        exit()

    # initial database, create table
    conn, cursor = init_db()

    # get the data for each company
    ibm_data = get_raw_data("IBM", "IBM")
    apple_data = get_raw_data("Apple Inc", "AAPL")


    # insert the records into the financial_data table
    for data in [ibm_data, apple_data]:
        for each_datapoint in data:
            sql = "INSERT INTO financial_data (symbol, date, open_price, close_price, volume) \
            VALUES (%s, %s, %s, %s, %s) AS new_data\
            ON DUPLICATE KEY UPDATE open_price = new_data.open_price, close_price = new_data.close_price, volume = new_data.volume" % \
            ('"' + each_datapoint['symbol'] + '"', '"' + each_datapoint['date'] + '"', each_datapoint['open_price'], each_datapoint['close_price'], each_datapoint['volume'])
            try:
                cursor.execute(sql)
            except:
                conn.rollback()
    conn.commit()
    print("records update successful.")
    
    # close connection
    cursor.close()
    conn.close()

