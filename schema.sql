CREATE SCHEMA IF NOT EXISTS myschema;
USE myschema;
CREATE TABLE IF NOT EXISTS financial_data(
	id SERIAL PRIMARY KEY,
    symbol VARCHAR(128) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10, 2) NOT NULL,
    close_price DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL
)