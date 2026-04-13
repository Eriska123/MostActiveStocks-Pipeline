# db.py

import pyodbc
import pandas as pd
from decimal import Decimal

# =====================================================
# DATABASE CONFIG
# =====================================================
CONN_STR = r"""
DRIVER={ODBC Driver 17 for SQL Server};
SERVER=localhost\SQLEXPRESS;
DATABASE=StockDB;
Trusted_Connection=yes;
Encrypt=no;
TrustServerCertificate=yes;
"""

# =====================================================
# CONNECTION
# =====================================================
def get_connection():
    return pyodbc.connect(CONN_STR)


# =====================================================
# GET OR CREATE STOCK
# =====================================================
def get_or_create_stock(cursor, symbol, name):
    """
    Ensure stock exists in 'stocks' table, return stock_id
    """
    cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM stocks WHERE symbol = ?)
        INSERT INTO stocks (symbol, company_name)
        VALUES (?, ?)
    """, (symbol, symbol, name))

    cursor.execute("SELECT stock_id FROM stocks WHERE symbol = ?", (symbol,))
    return cursor.fetchone()[0]


# =====================================================
# INSERT STOCK PRICE
# =====================================================
def insert_stock_price(cursor, stock_id, row):
    """
    Insert a stock price record
    """
    cursor.execute("""
    INSERT INTO stock_prices (
        stock_id,
        price,
        change,
        percent_change,
        volume,
        last_updated
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        stock_id,
        Decimal(str(row["Price"])),
        Decimal(str(row["Change"])),
        Decimal(str(row["PercentChange"])),
        int(row["Volume"]),
        row["LastUpdated"]
    ))


# =====================================================
# FETCH EXISTING RECORDS (FOR DEDUPLICATION)
# =====================================================
def get_existing_records(conn, symbols):
    """
    Fetch existing records based on business key:
    Symbol + Price + Change + PercentChange + Volume
    """
    if not symbols:
        return pd.DataFrame(columns=[
            'Symbol', 'Price', 'Change', 'PercentChange', 'Volume'
        ])

    placeholders = ",".join("?" for _ in symbols)

    query = f"""
    SELECT 
        s.symbol AS Symbol,
        sp.price AS Price,
        sp.change AS Change,
        sp.percent_change AS PercentChange,
        sp.volume AS Volume
    FROM stock_prices sp
    INNER JOIN stocks s
        ON sp.stock_id = s.stock_id
    WHERE s.symbol IN ({placeholders})
    """

    return pd.read_sql(query, conn, params=symbols)