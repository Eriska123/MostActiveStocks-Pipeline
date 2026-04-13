import requests
import pandas as pd
import pyodbc
from datetime import datetime
from decimal import Decimal
CSV_FILE = "../data/MostActiveStocks.csv"


# =====================================================
# CONFIGURATION
# =====================================================

SERVER = r"DESKTOP-F3EJ92V\SQLEXPRESS"
DATABASE = "StockDB"

csv_file = "../data/MostActiveStocks.csv"   # optional backup


# =====================================================
# STEP 1: FETCH DATA FROM YAHOO FINANCE
# =====================================================

def fetch_data():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=50&scrIds=most_actives"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("✅ Data fetched successfully.")
    except Exception as e:
        print("❌ API request failed:", e)
        return None

    try:
        rows = data["finance"]["result"][0]["quotes"]
        df = pd.DataFrame(rows)

        # Select relevant columns
        df = df[[
            "symbol",
            "shortName",
            "regularMarketPrice",
            "regularMarketChange",
            "regularMarketChangePercent",
            "regularMarketVolume"
        ]].copy()

        # Rename columns
        df.rename(columns={
            "symbol": "Symbol",
            "shortName": "Name",
            "regularMarketPrice": "Price",
            "regularMarketChange": "Change",
            "regularMarketChangePercent": "PercentChange",
            "regularMarketVolume": "Volume"
        }, inplace=True)

        # Data cleaning
        df.dropna(subset=["Price", "Volume"], inplace=True)

        # Timestamp
        df["LastUpdated"] = datetime.now()

        print(f"✅ Processed {len(df)} records.")

        return df

    except Exception as e:
        print("❌ Data processing failed:", e)
        return None


# =====================================================
# STEP 2: CONNECT TO SQL SERVER
# =====================================================

def connect_db():
    conn_str = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={SERVER};
    DATABASE={DATABASE};
    Trusted_Connection=yes;
    """

    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to SQL Server.")
        return conn
    except Exception as e:
        print("❌ Connection failed:", e)
        return None


# =====================================================
# STEP 3: ETL FUNCTIONS
# =====================================================

def get_or_create_stock(cursor, symbol, name):
    cursor.execute("""
    IF NOT EXISTS (SELECT 1 FROM stocks WHERE symbol = ?)
        INSERT INTO stocks (symbol, company_name)
        VALUES (?, ?)
    """, (symbol, symbol, name))

    cursor.execute(
        "SELECT stock_id FROM stocks WHERE symbol = ?",
        (symbol,)
    )

    return cursor.fetchone()[0]


def insert_stock_price(cursor, stock_id, row):
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
# STEP 4: MAIN PIPELINE
# =====================================================

def run_pipeline(save_csv=True):

    # -----------------------------
    # Fetch Data
    # -----------------------------
    df = fetch_data()

    if df is None or df.empty:
        print("❌ No data to process.")
        return

    # -----------------------------
    # Optional CSV Backup
    # -----------------------------
     
    if save_csv:
       df.to_csv(CSV_FILE, index=False)
       print(f"✅ CSV backup saved -> {CSV_FILE}")

    # -----------------------------
    # Connect to DB
    # -----------------------------
    conn = connect_db()

    if conn is None:
        return

    cursor = conn.cursor()

    # ⚡ PERFORMANCE BOOST
    cursor.fast_executemany = True

    try:
        inserted_rows = 0

        for _, row in df.iterrows():

            # Get/Create Stock
            stock_id = get_or_create_stock(
                cursor,
                row["Symbol"],
                row["Name"]
            )

            # Insert Price Record
            insert_stock_price(cursor, stock_id, row)

            inserted_rows += 1

        conn.commit()

        print(f"✅ ETL completed successfully.")
        print(f"📊 Rows inserted: {inserted_rows}")

    except Exception as e:
        conn.rollback()
        print("❌ ETL failed:", e)

    finally:
        conn.close()
        print("Data fetched successfully.")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_pipeline(save_csv=True)