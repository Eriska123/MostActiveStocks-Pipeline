from fetch import fetch_data

df = fetch_data()

if df is not None:
    print(df.head())