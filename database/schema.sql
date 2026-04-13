-- Create Database
CREATE DATABASE StockDB;
GO

USE StockDB;
GO

-- ===============================
-- STOCKS TABLE
-- ===============================
CREATE TABLE stocks (
    stock_id INT IDENTITY(1,1) PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255)
);

-- ===============================
-- STOCK PRICES TABLE
-- ===============================
CREATE TABLE stock_prices (
    price_id INT IDENTITY(1,1) PRIMARY KEY,
    stock_id INT,
    price DECIMAL(10,4),
    change DECIMAL(10,4),
    percent_change DECIMAL(10,4),
    volume BIGINT,
    last_updated DATETIME,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

-- ===============================
-- UNIQUE INDEX (DEDUP LOGIC)
-- ===============================
CREATE UNIQUE INDEX uq_stock_price
ON stock_prices (stock_id, price, change, percent_change, volume);