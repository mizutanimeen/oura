import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
# 因子分析
# 加工後データを読み込む
df = pd.read_csv("./csv/Analysis data/oura_main1.csv", sep=",")
# 分析用のカラムを抽出
df = df.loc[:,['Sleep Score','Total Sleep Duration','Awake Time', 'Restless Sleep','Sleep Latency Score','Sleep Timing',\
    'Bedtime Start', 'Bedtime End','Inactive Time','Low Activity Time',"Non-wear Time","Eat End","Bath End","Smartphone End"]]
df = df.dropna(subset=["Sleep Score"])
# dfを標準化
sc = StandardScaler()
sc.fit(df)
df_sc = sc.transform(df)
df_sc = pd.DataFrame(df_sc)

eigenvalue_one:np.ndarray = np.array([1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0])
plt.plot(np.linalg.eigvals(df_sc.corr()), "s-")
plt.plot(eigenvalue_one,"s-")
plt.show()
# 因子数入力
n = 5
# 因子分析と因子係数求め方
fa = FactorAnalyzer(n_factors=n,rotation="promax",impute="drop")
fa.fit(df_sc)
result_factor = pd.DataFrame(fa.loadings_, columns=["第１因子","第２因子","第３因子","第４因子","第５因子"],index=[df.columns])
print(result_factor)