import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# データを読み込む
df = pd.read_csv("./csv/Analysis data/oura_main1.csv", sep=",")
plt.figure(figsize=(1, 1))
#分析データを選択
df = df.loc[:,['Sleep Score','Total Sleep Duration','Awake Time', 'Restless Sleep','Sleep Latency Score','Sleep Timing',\
    'Bedtime Start', 'Bedtime End','Inactive Time','Low Activity Time',"Non-wear Time"]]
df = df.dropna(subset=["Sleep Score"])
# データ型が数値じゃないものを消している
# df = df.drop(["date"], axis=1)
# df = df.drop(["date","Bedtime Start","Bedtime End","Previous Day Activity Score"], axis=1)
# df = df.loc[:,['Sleep Score','Bedtime Start', 'Bedtime End',"Eat End","Bath End","Smartphone End"]]

#Sleep Scoreとの相関係数corr_num以上のカラムのみにする
def corr_higher(corr_num):
    print(f"相関係数{corr_num}以上")
    df_bool = abs(df.corr()["Sleep Score"]) > corr_num
    dft = df.T
    dft = dft[df_bool]
    dft = dft.T
    print(dft.columns)
    return dft

# すべてのデータをSleepScoreを含めた５つ程度のデータに分けて散布図にする
def scatter_diagram(df_len,df):
    df_len_5 = df_len // 5
    if df_len > 0:
        for i in range(df_len_5):
            df1 = df.iloc[:,i*5:(i+1)*5]
            df2 = df["Sleep Score"]
            if not i==0:df1 = pd.concat([df2, df1],axis=1)
            sns.pairplot(df1)
    if df_len % 5 > 0:
        df1 = df.iloc[:,df_len_5*5:df_len]
        df2 = df["Sleep Score"]
        if not df_len_5==0:
            df1 = pd.concat([df2, df1],axis=1)
        sns.pairplot(df1)
    plt.show()

# 関数実行
# 相関係数〇〇以上のデータとSleep Scoreの散布図を表示
dft = corr_higher(0.1)
scatter_diagram(len(dft.columns),dft)