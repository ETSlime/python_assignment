import pymysql
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

"""
Connect to the mysql server
Returns:
    the connector and the cursor of the database
"""
def connect_to_db():
	conn = pymysql.connect(host='database',
        user='root',
        password= os.environ.get("DB_PASSWORD"),
        database=None)
	return conn, conn.cursor()

"""
Generate the where condition query given the start date, end date, and symbol
Args:
    start_date: the start date of each record
    end_date: the end date of each record
    symbol: the symbol cooresponding to the company
Returns:
    A where condition sql
"""
def where_query(start_date=None, end_date=None, symbol=None):
	sql = ""
	start_cond = ""
	end_cond = ""
	symbo_cond = ""

	if (start_date is not None):
		start_cond = " date >= %s" % '"' + start_date + '"'
	if (end_date is not None):
		end_cond = " date <= %s" % '"' + end_date + '"'
	if (symbol is not None):
		symbo_cond = " symbol = %s" % '"' + symbol + '"'
	first_cond = True
	for item in [start_cond, end_cond, symbo_cond]:
		if (item != ""):
			if first_cond:
				sql += " WHERE" + item
				first_cond = False
			else:
				sql += " AND" + item
	return sql

"""
Retrive the financial data using api through http request
Args:
    url request arguments
Returns:
    The financial data under the condtion of given parameters
"""
def get_financial_data(args):
	start_date = args.get("start_date", type=str, default=None)
	end_date = args.get("end_date", type=str, default=None)
	symbol = args.get("symbol", type=str, default=None)
	page_limit = args.get("limit", type=int, default=5)
	page = args.get("page", type=int, default=1)

	try:
		if (start_date is not None):
			datetime.strptime(start_date , '%Y-%m-%d')
		if (end_date is not None):
			datetime.strptime(end_date , '%Y-%m-%d')
	except ValueError:
		error_message = "Incorrect data format, should be YYYY-MM-DD"
		return json.dumps({"data":{}, "info":{"error":error_message}}, indent=4, separators=(',',':'))

	connector, cursor = connect_to_db()

	error_message = ""	

	# where conditions query
	sql = where_query(start_date, end_date, symbol)

	start_page = (page - 1) * page_limit

	# get the total number of records
	cursor.execute("USE myschema")
	cursor.execute("SELECT count(*) from financial_data" + sql)
	total_records = cursor.fetchone()[0]

	# calculate the number of pages
	total_pages = total_records / page_limit if total_records % page_limit == 0 else (total_records // page_limit) + 1
	if page > total_pages:
		error_message = "current page index exceeds the total number of pages"

	# retrive the records indicated by page number
	cursor.execute("SELECT symbol, date, open_price, close_price, volume from financial_data" + sql + " LIMIT %s, %s" %  (start_page, page_limit))
	results = list(cursor.fetchall())

	# serialize data from database
	row_headers = [x[0] for x in cursor.description]
	json_data = []
	for item in results:
		list_item = list(item)
		list_item[1] = str(list_item[1])
		list_item[2] = float(list_item[2])
		list_item[3] = float(list_item[3])
		json_data.append(dict(zip(row_headers, list_item)))

	# encapsulating pagination parameters
	page_info = {"count":total_records, "page":page, "limit":page_limit, "pages":total_pages}

	return json.dumps({"data":json_data, "pagination":page_info, "info":{"error":error_message}}, indent=4, separators=(',',':'))


"""
Calcuate the statistics on the data in given period of time
Args:
    url request arguments
Returns:
    The statistics of the financial data in given period of time
"""
def get_statistics_data(args):
	start_date = args.get("start_date", type=str)
	end_date = args.get("end_date", type=str)
	symbol = args.get("symbol", type=str)

	connector, cursor = connect_to_db()

	error_message = ""
	if (start_date is None or end_date is None or symbol is None):
		error_message = "Please provide the correct value for start_date, end_date, and symbol. All parametere are required."
		return json.dumps({"data":{}, "info":{"error":error_message}}, indent=4, separators=(',',':'))

	try:
		datetime.strptime(start_date , '%Y-%m-%d')
		datetime.strptime(end_date , '%Y-%m-%d')
	except ValueError:
		error_message = "Incorrect data format, should be YYYY-MM-DD"
		return json.dumps({"data":{}, "info":{"error":error_message}}, indent=4, separators=(',',':'))

	if ((datetime.strptime(end_date , '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days < 0):
		error_message = "End date is before start date."
		return json.dumps({"data":{}, "info":{"error":error_message}}, indent=4, separators=(',',':'))

	# where conditions query
	sql = where_query(start_date, end_date, symbol)
	
	# calculate the statistics
	cursor.execute("USE myschema")
	cursor.execute("SELECT AVG(open_price) AS average_daily_open_price, AVG(close_price) AS average_daily_close_price, \
					AVG(volume) AS average_daily_volume from financial_data" + sql)
	results = cursor.fetchall()

	# serialize data
	row_headers = [x[0] for x in cursor.description]
	json_data = {"start_date":start_date, "end_date":end_date, "symbol":symbol}
	for idx, item in enumerate(results[0]):
		if (item is None):
			error_message = "No data available. Please check the value for start_date, end_date, and symbol."
		else:
			json_data[row_headers[idx]] = float(item)
	return json.dumps({"data":json_data, "info":{"error":error_message}}, indent=4, separators=(',',':'))
