# Python Assignment-Yibin Xia

This project retrives data from AlphaVantage, store processed data into local database, and provides backend APIs for query.

## Tech stack

- MySQL: a free open-source relational database management system. 
- Flask: a micro web framework which does not requrie particular tools or libraries.
- docker: provides a virtualized environment for API services.
- pymysql: a MySQL client library that helps connect to the MySQL db through python

## How to run this code in local environment

1. Firstly, you need to have python 3 and docker installed in your os, which can be downloaded from online sources. 
2. Then create a fine named `.env` in the root directory to store your AlphaVantage API key and password to the MySQL server. An example could be:
```
API_KEY = "put your api key here"
DB_PASSWORD = "put your password here"
``` 
3. Open the terminal:

```bash
docker-compose up
```
to start the database and API services

```bash
docker exec api python get_raw_data.py  
```

to initialzie database and retrive the data from AlphaVantage

4. use the following command to retrive the financial data from database

```bash
curl -X GET 'http://localhost:5000/api/financial_data?start_date=2023-01-01&end_date=2023-03-14&symbol=IBM&limit=3&page=2'

```
parameters:
    start_date(optional)
    end_date(optional)
    symbol(optional)
    limit(optional, default 5)


use the following command to calcuate the statistics on the data in given period of time
```bash
curl -X GET 'http://localhost:5000/api/statistics?start_date=2023-01-01&end_date=2023-03-31&symbol=IBM'

```
parameters:
    start_date(required)
    end_date(required)
    symbol(required)


## How to maintain the API key

In local development, use `.env`  to store the API key as a local environment variables instead of hard-coded in the code such that others won't see your API key.Be careful that do not upload the API key to any public repositories. In production environment, use any secure platform such as Google cloud to store API keys.

