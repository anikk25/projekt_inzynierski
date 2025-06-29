import pandas as pd

df1 = pd.read_csv('ross_described_products1.csv')
df2 = pd.read_csv('ross_described_products2.csv')

df_all = pd.concat([df1, df2], ignore_index=True)

df_all.to_csv('ross_described_products.csv', index=False)
