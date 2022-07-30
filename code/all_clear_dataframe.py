#データすべて削除
import pandas as pd
df = pd.read_csv("csv/test.csv", sep=",")
print(df)
df = df.drop(range(len(df)))
print(df)
df.to_csv("csv/test.csv",index=False)
