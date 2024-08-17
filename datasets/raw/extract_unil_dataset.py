# A script that we wrote to convert the original authors' dataset to the format we use in our method.
import pandas as pd

REPORT_P1_XLSX_PATH = 'Report_P1.xlsx'
REPORT_P2_XLSX_PATH = 'Report_P2.xlsx'
OUTPUT_CSV_PATH = 'measurements.csv'
ORIGINAL_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

df_p1 = pd.read_excel(REPORT_P1_XLSX_PATH, header=1)
df_p2 = pd.read_excel(REPORT_P2_XLSX_PATH, header=1)
df_p1 = df_p1[['Time', 'Latitude', 'Longitude']]
df_p2 = df_p2[['Time', 'Latitude', 'Longitude']]
df_p1["measured_from"] = "P1"
df_p2["measured_from"] = "P2"
df_p1["precise"] = "on" # mentioned in the authors' paper
df_p2["precise"] = "on" # mentioned in the authors' paper

rename_columns = {
    'Time': 'datetime',
    'Latitude': 'lat',
    'Longitude': 'lng',
}
df_p1.rename(columns=rename_columns, inplace=True)
df_p2.rename(columns=rename_columns, inplace=True)
df_p1['datetime'] = pd.to_datetime(df_p1['datetime'], format=ORIGINAL_DATE_FORMAT)
df_p2['datetime'] = pd.to_datetime(df_p2['datetime'], format=ORIGINAL_DATE_FORMAT)
df = pd.concat([df_p1, df_p2], ignore_index=True)

# change column order to measured_from, datetime, lat, lng, precisee
df = df[['measured_from', 'datetime', 'lat', 'lng', 'precise']]
# sort by measured_from and datetime
df.sort_values(['measured_from', 'datetime'], inplace=True)

df.to_csv(OUTPUT_CSV_PATH, index=False)
