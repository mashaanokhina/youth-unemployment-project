import requests, zipfile, io, pandas as pd

# Step 1: Download StatCan data (Table 14-10-0287-01)
table_id = "14100287"
zip_url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"

print("⬇️ Downloading direct CSV ZIP from StatCan...")
response = requests.get(zip_url)
response.raise_for_status()

# Step 2: Unzip in memory
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    csv_files = [name for name in z.namelist() if name.endswith(".csv")]
    csv_name = csv_files[0]
    print(f"📄 Found CSV inside ZIP: {csv_name}")
    with z.open(csv_name) as f:
        df = pd.read_csv(f, low_memory=False)

print("✅ Data loaded successfully!")

# Step 3: Filter for years 2020+
df["Year"] = df["REF_DATE"].astype(str).str[:4].astype(int)
df = df[df["Year"] >= 2020]

# Step 4: Keep only provinces (exclude "Canada")
provinces = [
    "Newfoundland and Labrador", "Prince Edward Island", "Nova Scotia", "New Brunswick",
    "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta", "British Columbia"
]
df = df[df["GEO"].isin(provinces)]

# Step 5: Keep only desired labour force characteristics
desired_chars = [
    "Population",
    "Unemployment rate",
    "Employment rate",
    "Unemployed",
    "Employed"
]
df = df[df["Labour force characteristics"].isin(desired_chars)]

# Step 6: Keep only seasonally adjusted data (correct column is "Data type")
if "Data type" in df.columns:
    df = df[df["Data type"].str.contains("Seasonally adjusted", case=False, na=False)]
else:
    print("⚠️ Column 'Data type' not found; skipping seasonal adjustment filter.")

# Step 7: Drop duplicates
df = df.drop_duplicates(
    subset=["REF_DATE", "GEO", "Gender", "Age group", "Labour force characteristics"],
    keep="first"
)

# Step 8: Select and rename relevant columns
df = df[[
    "REF_DATE",
    "GEO",
    "Gender",
    "Age group",
    "Labour force characteristics",
    "VALUE",
    "UOM"
]]

df = df.rename(columns={
    "REF_DATE": "Date",
    "GEO": "Province",
    "VALUE": "Value",
    "UOM": "Unit"
})

# Step 9: Save cleaned version
output_path = "C:/Users/Masha/Documents/labour_market_2020_onward.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"💾 Saved filtered dataset to: {output_path}")
print(f"✅ Final rows: {len(df)}")
print(df.head(10))

# Step 10: Create pivoted version (for Power BI / Excel)
df_pivot = df.pivot_table(
    index=["Date", "Province", "Gender", "Age group"],
    columns="Labour force characteristics",
    values="Value"
).reset_index()

# Save pivoted version too
pivot_path = "C:/Users/Masha/Documents/labour_market_pivoted.csv"
df_pivot.to_csv(pivot_path, index=False, encoding="utf-8-sig")

print(f"💾 Saved pivoted dataset to: {pivot_path}")
print(f"✅ Pivoted shape: {df_pivot.shape}")
print(df_pivot.head(10))
