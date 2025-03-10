import pandas as pd
import numpy as np

df = pd.read_csv("us-county-income-modified.csv", skipinitialspace=True, na_values=["", "NA"]).fillna(0)

states = df.iloc[:, 0]
year_columns = df.columns[1:]

df_long = df.melt(id_vars=[df.columns[0]], var_name="Year", value_name="Income", value_vars=year_columns)
df_long["Year"] = pd.to_datetime(df_long["Year"].astype(str) + "-01-31")  # Convert to last day of Jan

print(df_long.head())
all_months = pd.date_range(start=df_long["Year"].min(), end=df_long["Year"].max(), freq="ME")

df_interpolated = df_long.groupby(df.columns[0], group_keys=False).apply(
    lambda g: g.set_index("Year").reindex(all_months).interpolate()
).reset_index()

print(df_interpolated.head())

df_final = df_interpolated.pivot(index=df.columns[0], columns="index", values="Income").reset_index()

print(df_final.columns)

df_final.columns = [df.columns[0]] + [date.strftime("%Y-%m-%d") for date in all_months]

df_final.to_csv("us-county-income-populated.csv", index=False)

print(df_final.head())