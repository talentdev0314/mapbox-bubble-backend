import pandas as pd

file1 = "us-metro-income.csv"
file2 = "us-metro-rental-%-as-income.csv"

df1 = pd.read_csv(file1, dtype={"StateCode": int})
df2 = pd.read_csv(file2, dtype={"StateCode": int})

df1.iloc[:, 0] = df1.iloc[:, 0].astype(str)
df2.iloc[:, 0] = df2.iloc[:, 0].astype(str)
print(df1.iloc[:, 0][:10])
print(df2.iloc[:, 0][:10])

common_indexes = set(df1.iloc[:, 0]) & set(df2.iloc[:, 0])
df1_common = df1[df1.iloc[:, 0].isin(common_indexes)]
df1_common.to_csv(f"us-metro-income-modified.csv", index=False)

df2_common = df2[df2.iloc[:, 0].isin(common_indexes)]
df2_common.to_csv(f"us-metro-rental-%-as-income-modified.csv", index=False)

print("Done filtering")
