import pandas as pd
import re

# 加工前データを読み込む
df = pd.read_csv("oura.csv", sep=",")
# 時間表示を数字に置換
# 例：T20-12-33.→20*60 + 12→1212  例: T00-00-00.→ 24-00-00  → 24*60 → 1440
# 引数1=変換したいカラムの名前,引数2=24:00（00:00）を超えた数字がでてくるかどうか(でてくるならTRUE)
def time_to_num(columns_name, is_night_time):
    x = df[columns_name]
    x = x.dropna()
    num = len(x)
    for i in range(num):
        content = x[i]
        pattern = '.*?[T](\d+.\d+.\d+).*'
        result = re.match(pattern, content)
        if result:
            result = result.group(1)
            hour = int(result[0] + result[1])
            if hour < 10 and is_night_time:
                hour += 24
            minute = int(result[3] + result[4])
            df[columns_name][i] = hour*60 + minute
        else:
            print("追加処理")
# 数字に置換実行
time_to_num("Bedtime Start",True)
time_to_num("Bedtime End",False)
# エクセルに保存
df.to_csv("oura.csv")