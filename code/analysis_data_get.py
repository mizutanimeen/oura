import pandas as pd
#本番データ作成
df = pd.read_csv("oura1.csv", sep=",")
# 分析用のカラムを抽出
# df = df.loc[:,['date','Sleep Score','Total Sleep Duration','Awake Time', 'Restless Sleep','Sleep Latency Score','Sleep Timing',\
#     'Bedtime Start', 'Bedtime End','Inactive Time','Low Activity Time',"Non-wear Time","Eat End","Bath End","Smartphone End"]]
df = df.loc[:,['date','Sleep Score','Total Sleep Duration','Awake Time', 'Restless Sleep','Sleep Latency Score','Sleep Timing',\
    'Bedtime Start', 'Bedtime End','Inactive Time','Low Activity Time',"Non-wear Time"]]
df = df.set_index("date")
#Sleep Score がないものは取り除く
df = df.dropna(subset=["Sleep Score"])
df["Eat End"] = None
df["Bath End"] = None
df["Smartphone End"] = None
#保存
df.to_csv("oura1.csv")