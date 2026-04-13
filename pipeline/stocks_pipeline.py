# stocks_pipeline.py

from fetch import fetch_data
from db import (
    get_connection,
    get_or_create_stock,
    insert_stock_price,
    get_existing_records
)

import os
import pandas as pd

DATA_DIR = os.path.join("..", "data")
CSV_FILE = os.path.join(DATA_DIR, "MostActiveStocks.csv")


def run_pipeline(save_csv=True):
    print("🚀 Starting Stock Data Pipeline...")

    # =====================================================
    # 1. FETCH DATA
    # =====================================================
    df = fetch_data()

    if df.empty:
        print("❌ No data fetched.")
        return

    print(f"✅ Processed {len(df)} records.")

    # =====================================================
    # 2. SAVE CSV BACKUP
    # =====================================================
    if save_csv:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ CSV saved -> {CSV_FILE}")

    # =====================================================
    # 3. NORMALIZE DATA (CRITICAL FOR DEDUP)
    # =====================================================
    df['Price'] = df['Price'].astype(float).round(4)
    df['Change'] = df['Change'].astype(float).round(4)
    df['PercentChange'] = df['PercentChange'].astype(float).round(4)
    df['Volume'] = df['Volume'].astype(int)

    # =====================================================
    # 4. CONNECT TO DATABASE
    # =====================================================
    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # 5. FETCH EXISTING RECORDS
    # =====================================================
    existing_df = get_existing_records(conn, df['Symbol'].tolist())

    if not existing_df.empty:
        existing_df['Price'] = existing_df['Price'].astype(float).round(4)
        existing_df['Change'] = existing_df['Change'].astype(float).round(4)
        existing_df['PercentChange'] = existing_df['PercentChange'].astype(float).round(4)
        existing_df['Volume'] = existing_df['Volume'].astype(int)

    # =====================================================
    # 6. DEDUPLICATION (BUSINESS KEY)
    # =====================================================
    merged = df.merge(
        existing_df,
        on=['Symbol', 'Price', 'Change', 'PercentChange', 'Volume'],
        how='left',
        indicator=True
    )

    new_rows = merged[merged['_merge'] == 'left_only'].copy()

    print(f"✅ {len(new_rows)} new records to insert.")

    # =====================================================
    # 7. INSERT ONLY NEW RECORDS
    # =====================================================
    inserted = 0

    for _, row in new_rows.iterrows():
        try:
            stock_id = get_or_create_stock(cursor, row['Symbol'], row['Name'])
            insert_stock_price(cursor, stock_id, row)
            inserted += 1
        except Exception:
            # Handles duplicate constraint safely
            print(f"⚠️ Skipped duplicate: {row['Symbol']}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Inserted {inserted} records.")
    print("🔒 Database connection closed.")


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    run_pipeline(save_csv=True)