from cProfile import label
import tkinter as tk
import PIL.Image, PIL.ImageTk
from tkcalendar import DateEntry
import pandas as pd
import numpy as np
import datetime
from tkinter import ttk
import openpyxl
import time
import threading
import random

class App(tk.Tk):
#region----------------------------設定----------------------------------------------
    '''
    ここの設定なんとかする
    行動データのカラムとかいらない？
    '''
    # 行動データのカラム
    element_list = ["date","Sleep Score","Smartphone End", "Active Start", "Bedtime Start"]
    element_list_date_none = ["Sleep Score","Smartphone End", "Active Start", "Bedtime Start"]
    #行動データのロード先とセーブ先
    load_csv = "./csv/main_data.csv"
    save_csv = load_csv
    # 目標行動の目標時刻（分表示）
    #"Smartphone End", "Active Start", "Bedtime Start"
    '''
    辞書形式にする？
    '''
    target_time = [1320,1080,1380]
    #region----------------------メモ用----------------------------------------------------
    memo_path = "./csv/memo_oura.xlsx"
    wb = openpyxl.load_workbook(memo_path)
    ws = wb["Sheet1"]
    c1 = ws["A1"]
    #endregion--------------------------------------------------------------------------
    # 呪文
    def __init__(self, *args, **kwargs):
        # 呪文
        tkk = tk.Tk.__init__(self, *args, **kwargs)
        self.title("oura")
        self.geometry("1500x700")
        # ウィンドウのグリッドを 1x1 にする
        # この処理をコメントアウトすると配置がズレる
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
#endregion--------------------------------------------------------------------------
#region-----------------------------UI---------------------------------------------
#region-----------------------------main_frame-----------------------------------
        self.main_frame = tk.Frame()
        self.main_frame.grid(row=0, column=0, sticky="nsew",padx=30,pady=30)
        #---------------------------行動データ読み込み-----------------------------------------------
        self.df = pd.read_csv(self.load_csv, sep=",")
        self.df = self.sort_date(self.df)
        #--------------------------------------------------------------------------
        self.lbl_home = tk.Label(self.main_frame, text="HOMEページ", font=('Helvetica', '20'))
        self.lbl_home.place(x=0,y=0)
        #---------------------------終了ボタン-----------------------------------------------
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        menu_file = tk.Menu(self, tearoff = False) 
        menubar.add_cascade(label='終了', menu=menu_file) 
        menu_file.add_command(label='終了', command=lambda:exit()) 
        #region---------------------入力フォーム-----------------------------------------------------
        self.lbl1 = tk.Label(self.main_frame, text="要素をNaNにしたい場合は-1を記入")
        self.lbl1.place(x=0,y=50)
        self.lbl2 = tk.Label(self.main_frame, text="時刻は小文字数字のみ,4桁,深夜１時を２５時と記述（例：01:02→2502）")
        self.lbl2.place(x=0,y=70)
        self.lbl3 = tk.Label(self.main_frame, text="SleepScore")
        self.txt0 = tk.Entry(self.main_frame, width=20)
        self.lbl3.place(x=0,y=90)
        self.txt0.place(x=230,y=90)
        self.lbl4 = tk.Label(self.main_frame, text="スマホの終了時間")
        self.txt1 = tk.Entry(self.main_frame, width=20)
        self.lbl4.place(x=0,y=110)
        self.txt1.place(x=230,y=110)
        self.lbl5 = tk.Label(self.main_frame, text="運動の開始時刻（してないなら空欄）")
        self.txt2 = tk.Entry(self.main_frame,width=20)
        self.lbl5.place(x=0,y=130)
        self.txt2.place(x=230,y=130)
        self.lbl6 = tk.Label(self.main_frame, text="布団に入った時間")
        self.txt3 = tk.Entry(self.main_frame, width=20)
        self.lbl6.place(x=0,y=150)
        self.txt3.place(x=230,y=150)
        self.date_entry = DateEntry(self.main_frame)
        self.date_entry.place(x=0,y=170)
        self.save_btn = tk.Button(self.main_frame,text="保存",command=lambda: self.data_output_csv())
        self.save_btn.place(x=0,y=200)
        #endregion
        #region---------------------エラーメッセージ-----------------------------------------------------
        self.lbl_error1 = tk.Label(self.main_frame, text="")
        self.lbl_error2 = tk.Label(self.main_frame, text="")
        self.lbl_error1.place(x=0,y=230)
        self.lbl_error2.place(x=0,y=250)
        #endregion
        #region---------------------行動データ表示-----------------------------------------------------
        column = ("Date","Sleep Score","スマホの終了時間","運動の開始時間","布団に入った時間")
        self.tree = ttk.Treeview(self.main_frame, columns=column,height=2)
        self.tree.column('#0',width=0, stretch='no')
        self.tree.column('Date', anchor='center', width=80,stretch='no')
        self.tree.column('Sleep Score',anchor='center', width=80)
        self.tree.column('スマホの終了時間', anchor='center', width=100)
        self.tree.column('運動の開始時間', anchor='center', width=100)
        self.tree.column('布団に入った時間', anchor='center', width=100)
        self.tree.heading('Date', text='Date',anchor='center')
        self.tree.heading('Sleep Score', text='Sleep Score', anchor='center')
        self.tree.heading('スマホの終了時間',text='スマホの終了時間', anchor='center')
        self.tree.heading('運動の開始時間',text='運動の開始時間', anchor='center')
        self.tree.heading('布団に入った時間',text='布団に入った時間', anchor='center')
        self.insert_daily_tree()
        self.tree.place(x=0,y=270)
        #endregion
        #region---------------------目標テーブル-----------------------------------------------------
        self.lbl_purpose = tk.Label(self.main_frame, text="目標")
        self.lbl_purpose.place(x=500,y=50)
        column_purpose = ("スマホの終了時間","運動の開始時間","布団に入った時間")
        self.tree_purpose = ttk.Treeview(self.main_frame, columns=column_purpose,height=1)
        self.tree_purpose.column('#0',width=0, stretch='no')
        self.tree_purpose.column('スマホの終了時間', anchor='center', width=100)
        self.tree_purpose.column('運動の開始時間', anchor='center', width=100)
        self.tree_purpose.column('布団に入った時間', anchor='center', width=100)
        self.tree_purpose.heading('スマホの終了時間',text='スマホの終了時間', anchor='center')
        self.tree_purpose.heading('運動の開始時間',text='運動の開始時間', anchor='center')
        self.tree_purpose.heading('布団に入った時間',text='布団に入った時間', anchor='center')
        tpl = []
        for i in range(len(self.target_time)):
            tpl.append(str(self.target_time[i] // 60) + " : " +  str(self.target_time[i] % 60).zfill(2))
        value = tuple(tpl)
        self.tree_purpose.insert(parent='', index='end', iid=1 ,values=(value))
        self.tree_purpose.place(x=500,y=70)
        #endregion
        #region---------------------達成回数テーブル-----------------------------------------------------
        self.lbl_achievement = tk.Label(self.main_frame, text="達成回数")
        self.lbl_achievement.place(x=500,y=120)
        column_achievement = ("スマホの終了時間","運動の開始時間","布団に入った時間")
        self.tree_achievement = ttk.Treeview(self.main_frame, columns=column_achievement,height=1)
        self.tree_achievement.column('#0',width=0, stretch='no')
        self.tree_achievement.column('スマホの終了時間', anchor='center', width=100)
        self.tree_achievement.column('運動の開始時間', anchor='center', width=100)
        self.tree_achievement.column('布団に入った時間', anchor='center', width=100)
        self.tree_achievement.heading('スマホの終了時間',text='スマホの終了時間', anchor='center')
        self.tree_achievement.heading('運動の開始時間',text='運動の開始時間', anchor='center')
        self.tree_achievement.heading('布団に入った時間',text='布団に入った時間', anchor='center')
        self.insert_achievement()
        self.tree_achievement.place(x=500,y=140)
        #endregion
        #region---------------------メモ-----------------------------------------------------
        self.memo_box = tk.Text(self.main_frame,width=42,height=10)
        self.memo_box.insert("1.0", self.c1.value)
        self.memo_box.place(x=500,y=200)
        self.save_button = tk.Button(self.main_frame,text="save")
        self.save_button.place(x=630,y=340)
        self.save_button["command"] = self.memo_save_click
        #endregion
        #region---------------------スコア平均テーブル-----------------------------------------------------
        column_scores = ("これまでのスコア平均","今月のスコア平均")
        self.tree_scores = ttk.Treeview(self.main_frame, columns=column_scores,height=1)
        self.tree_scores.column('#0',width=0, stretch='no')
        self.tree_scores.column('これまでのスコア平均', anchor='center', width=200)
        self.tree_scores.column('今月のスコア平均', anchor='center', width=200)
        self.tree_scores.heading('これまでのスコア平均',text='これまでのスコア平均', anchor='center')
        self.tree_scores.heading('今月のスコア平均',text='今月のスコア平均', anchor='center')
        '''
        tree_scoresを関数化する
        '''
        tpl = []
        all_sleep_mean = 0
        all_sleep_mean = int(np.mean(self.df["Sleep Score"]))
        first_day = datetime.date.today().replace(day=1)
        month_sleep_mean = 0
        month_sleep_mean = int(np.mean(self.df[self.df["date"] >= str(first_day)]["Sleep Score"]))
        tpl.append(all_sleep_mean)
        ratio = 0
        ratio = month_sleep_mean / all_sleep_mean
        ratio = int((ratio-1)*100)
        ratio_str = '{:+}%'.format(ratio)
        tpl.append(f"{month_sleep_mean}({ratio_str})")
        value = tuple(tpl)
        self.tree_scores.insert(parent='', index='end', iid=1 ,values=(value))
        self.tree_scores.place(x=850,y=70)
        #endregion
        #region---------------------敵を倒した数-----------------------------------------------------
        self.battle_df = pd.read_csv("./csv/battle_results.csv", sep=",")
        column_wins = ("これまでの勝利数","今月の勝利数")
        self.tree_wins = ttk.Treeview(self.main_frame, columns=column_wins,height=1)
        self.tree_wins.column('#0',width=0, stretch='no')
        self.tree_wins.column('これまでの勝利数', anchor='center', width=200)
        self.tree_wins.column('今月の勝利数', anchor='center', width=200)
        self.tree_wins.heading('これまでの勝利数',text='これまでの勝利数', anchor='center')
        self.tree_wins.heading('今月の勝利数',text='今月の勝利数', anchor='center')
        self.insert_wins_tree()
        self.tree_wins.place(x=850,y=140)
        #endregion--------------------------------------------------------------------------
        #----------------------フレーム移動ボタン----------------------------------------------------
        self.changePageButton_main = tk.Button(self.main_frame, text="今日の戦闘へ", command=lambda : self.changePage(self.attackpage))
        self.changePageButton_main.place(x=610,y=400)
        #--------------------------------------------------------------------------
#endregion--------------------------------------------------------------------
#region-----------------------------attackpage---------------------------------------
        self.attackpage = tk.Frame()
        self.attackpage.grid(row=0, column=0, sticky="nsew",padx=30,pady=30)
        #------------------------------attackpageで使うDataFrame取得-------------------------------------
        self.player_df = pd.read_csv("./csv/player_data.csv", sep=",")
        self.enemy_df = pd.read_csv("./csv/enemy_data.csv", sep=",")
        #------------------------------今日の行動データを取得--------------------------------------------
        self.today_data_get()
        #region------------------------------プレイヤーのデータ取得--------------------------------------------
        self.player = self.player_df.iloc[len(self.player_df) - 1]
        self.player_level = self.player["Level"]
        self.player_hp = self.player["Hp"]
        self.player_attack = self.player["Attack"]
        #endregion--------------------------------------------------------------------------
        #region------------------------------敵のデータ取得--------------------------------------------
        self.enemy = self.enemy_df.iloc[datetime.datetime.now().day-1]
        self.enemy_hp = self.enemy["Hp"]
        self.enemy_attack = self.enemy["Attack"]
        self.enemy_weaknesses = self.enemy["Weaknesses"]
        #endregion--------------------------------------------------------------------------
        #region------------------------------今日の日付を０埋めしてない形で取得--------------------------------------------
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m").lstrip("0")
        day = datetime.datetime.now().strftime("%d").lstrip("0")
        date_without_0 = year + "/" + month + "/" + day
        #endregion--------------------------------------------------------------------------
        #region------------------------------今日既にバトルをしたかどうか確認、今日のデータがないなら新しく作る--------------------------------------------
        self.battle_df = pd.read_csv("./csv/battle_results.csv", sep=",")
        self.battle_df_Index = self.battle_df[self.battle_df["date"]==date_without_0].index.tolist()
        if self.battle_df_Index:
            # バトルしたかどうか調べてしてるならボタン削除
            if self.battle_df.loc[self.battle_df_Index[0],"do Battle"]:
                self.changePageButton_main.destroy()
        else:
            #バトルしたかどうかのデータがないなら新しく作る
            self.battle_df.loc[len(self.battle_df)] = [date_without_0,False,False]
            self.battle_df_Index = self.battle_df[self.battle_df["date"]==date_without_0].index.tolist()
            self.battle_df.to_csv("./csv/battle_results.csv",index=False)
        #endregion--------------------------------------------------------------------------
        #region------------------------------画像表示--------------------------------------------
        #canvas
        self.canvas = tk.Canvas(self.attackpage,height=1000, width=1800)
        self.canvas.place(x = 0,y = 0)
        #player
        self.player_image = PIL.Image.open(f"./images/player/image{self.player_level//5}.png")
        self.player_image = self.player_image.resize((250, 250))
        self.player_image = PIL.ImageTk.PhotoImage(self.player_image)
        self.canvas.create_image(350, 50, image=self.player_image, anchor=tk.NW,tags="player")
        #enemy
        self.enemy_image = PIL.Image.open(f"./images/enemy/image{(self.enemy_weaknesses * 100) + self.player_level//5}.png")
        self.enemy_image = self.enemy_image.resize((250, 250))
        self.enemy_img = PIL.ImageTk.PhotoImage(self.enemy_image)
        self.canvas.create_image(800, 50, image=self.enemy_img, anchor=tk.NW,tags="enemy")
        #endregion--------------------------------------------------------------------------
        #region------------------------------HPbar--------------------------------------------
        #player
        self.player_val = tk.IntVar()
        self.player_val.set(self.player_hp)
        self.player_hp_bar=ttk.Progressbar(self.attackpage,length=250,maximum=self.player_hp,mode="determinate", variable=self.player_val)
        self.player_hp_bar.place(x = 350,y = 300)
        #enemy
        self.enemy_val = tk.IntVar()
        self.enemy_val.set(self.enemy_hp)
        self.enemy_hp_bar=ttk.Progressbar(self.attackpage,length=250,maximum=self.enemy_hp,mode="determinate", variable=self.enemy_val)
        self.enemy_hp_bar.place(x = 800,y = 300)
        #endregion-----------------------------------------------------------------
        #region------------------------------戦闘log------------------------------
        self.canvas.create_rectangle(0, 400, 2000, 1000, fill = '#d3d3d3', outline ='#696969')
        self.battle_log = tk.Label(self.attackpage, text="",background="#d3d3d3",font=('Helvetica', '20'))
        self.battle_log.place(x=300,y=500)
        #endregion-----------------------------------------------------------------
        #-------------------------------戦闘開始ボタン----------------------------
        self.battle_start_button = tk.Button(self.attackpage, text="戦闘開始", command=lambda : self.battle_start())
        self.battle_start_button.place(x = 0,y = 0)
        #-------------------------------リザルトへのボタン----------------------------------
        self.changePageButton_battle = tk.Button(self.attackpage, text="リザルト画面へ", command=lambda : self.result_start())
#endregion--------------------------------------------------------------------------
#region-----------------------------result---------------------------------------
        self.resultpage = tk.Frame()
        self.resultpage.grid(row=0, column=0, sticky="nsew",padx=30,pady=30)
        self.result_canvas = tk.Canvas(self.resultpage,height=1000, width=1800)
        self.result_canvas.place(x = 0,y = 0)
        #region---------------------------Label-----------------------------------------------
        self.win_or_lose_label = tk.Label(self.resultpage, text="",font=('Helvetica', '40'))
        self.win_or_lose_label.place(x=650,y=0)
        self.mission1 = tk.Label(self.resultpage, text="スマホ終了時間",font=('Helvetica', '15'))
        self.mission2 = tk.Label(self.resultpage, text="運動の開始時間",font=('Helvetica', '15'))
        self.mission3 = tk.Label(self.resultpage, text="布団に入った時間",font=('Helvetica', '15'))
        self.achievement_mission1 = tk.Label(self.resultpage, text="",font=('Helvetica', '15'))
        self.achievement_mission2 = tk.Label(self.resultpage, text="",font=('Helvetica', '15'))
        self.achievement_mission3 = tk.Label(self.resultpage, text="",font=('Helvetica', '15'))
        self.mission1.place(x=250,y=140)
        self.mission2.place(x=250,y=180)
        self.mission3.place(x=250,y=220)
        self.achievement_mission1.place(x=450,y=140)
        self.achievement_mission2.place(x=450,y=180)
        self.achievement_mission3.place(x=450,y=220)
        self.advice = tk.Label(self.resultpage, text="",font=('Helvetica', '20'))
        self.advice.place(x=250,y=480)
        #endregion--------------------------------------------------------------------------
        #-----------------------------宝箱---------------------------------------------
        #関数で表示処理
        #---------------------------メインページに移動するボタン-----------------------------------------------
        self.changePageButton_result = tk.Button(self.resultpage, text="メインページに戻る", command=lambda : self.changePage(self.main_frame))
        self.changePageButton_result.place(x = 0,y = 0)
        #--------------------------------------------------------------------------
#endregion--------------------------------------------------------------------------
        #main_frameを一番上に表示
        self.main_frame.tkraise()
        # self.attackpage.tkraise()
        # self.resultpage.tkraise()
#endregion--------------------------------------------------------------------------
#region-----------------------------関数---------------------------------------------
    def changePage(self, page):
        # 画面遷移用の関数
        page.tkraise()
#region-----------------------------mainpage---------------------------------------------
    #region-------------------------行動データの入力フォームの処理-------------------------------------------------
    #テキストボックスのデータを変数に代入[戻り値 Sleep Score,その他の４桁時間(list,str),日付(str)]
    def get_textbox(self):
        time_str_data = []
        if self.txt0.get() != "":
            sleep_score = int(self.txt0.get())
        else:
            sleep_score = None
        time_str_data.append(self.txt1.get())
        time_str_data.append(self.txt2.get())
        time_str_data.append(self.txt3.get())
        date_data = self.date_entry.get_date()
        date_plus1_data = date_data + datetime.timedelta(days=1)
        #dfの日付要素がstrなのでstrにして存在しているか判定
        date_data = date_data.strftime('%Y-%m-%d')
        date_plus1_data = date_plus1_data.strftime('%Y-%m-%d')
        return sleep_score,time_str_data,date_data,date_plus1_data
    #入力値の時刻を分(1h=60m)に変換[戻り値 数値に変換した時間 (list,int)]
    def change_str_to_num(self,time_str_data):
        time_num_data = []
        self.lbl_error1["text"] = ""
        for time in time_str_data:
            if not len(time) == 4 and not len(time) == 0 and not time == "-1":
                self.lbl_error1["text"] = "時間の記入は例のように記入してください"
                time_num_data.append(None)
            elif time == "":
                time_num_data.append(None)
            elif time == "-1":
                time_num_data.append(-1)
            else:
                hour = int(time[0] + time[1])
                minute = int(time[2] + time[3])
                time_num_data.append(hour*60 + minute)
        return time_num_data
    #日付を基準に降順にソート[戻り値 ソートしたdf]
    def sort_date(self,df):
        df['date'] = pd.to_datetime(df['date'], infer_datetime_format= True)
        df.sort_values(by = 'date', ascending = False, inplace = True) 
        df = df.reset_index()
        df = df.loc[:,self.element_list]
        return df
    #次の日より先に記録できないようにする [戻り値 次の日以降の記録を削除したdf]
    def limit_date(self,df):
        df['date'] = pd.to_datetime(df['date'], infer_datetime_format= True).dt.date
        todayplus = datetime.date.today() + datetime.timedelta(days=1)
        self.lbl_error2["text"] = ""
        if len(df[todayplus < df['date']]) > 0:
            self.lbl_error2["text"] = "明日より先の日付に記録はできません"
        df = df[todayplus >= df['date']]
        return df
    #入力値をcsvに日付を降順にソートして保存    [返り値 保存、ソートしたdf]
    def data_save_csv(self,date_data,date_plus1_data,time_num_data,sleep_score):
        df = pd.read_csv(self.load_csv, sep=",")
        #保存データ絞り込み
        df = df.loc[:,self.element_list]
        df = df.dropna(subset=["date"])
        #既に日付があるか、あるならそのインデックス入手
        df_Index = df[df['date']==date_data].index.tolist()
        #Sleep Scoreと布団に入った時間を記録当日に記入
        if len(df_Index) == 1:
        # 日付が存在している場合
            if time_num_data[2] == -1:
                df.loc[df_Index[0],"Bedtime Start"] = None
            elif time_num_data[2] != None:
                df.loc[df_Index[0],"Bedtime Start"] = time_num_data[2]
            if sleep_score == -1:
                df.loc[df_Index[0],"Sleep Score"] = None
            elif sleep_score != None:
                df.loc[df_Index[0],"Sleep Score"] = sleep_score
        else:
        # 日付が存在していない場合
            #新しい行生成
            df.loc[len(df)] = None
            df.loc[len(df) - 1,"date"] = date_data
            if not time_num_data[2] == -1:
                df.loc[len(df) - 1,"Bedtime Start"] = time_num_data[2]
            if not sleep_score == -1:
                df.loc[len(df) - 1,"Sleep Score"] = sleep_score
        #スマホの終了時間と運動開始時間を次の日に代入
        df_Index = df[df['date']==date_plus1_data].index.tolist()
        if len(df_Index) == 1:
        # 日付が存在している場合
            for i in range(2):
                if time_num_data[i] == None:
                    continue
                if time_num_data[i] == -1:
                    time_num_data[i] = None
                df.loc[df_Index[0],df.columns[i+2]] = time_num_data[i]
        else:
        # 日付が存在していない場合
            #新しい行生成
            df.loc[len(df)] = None
            df.loc[len(df) - 1,"date"] = date_plus1_data
            '''
            行数少し減ってるけど汎用性も低いし読みづらいしやめる？
            '''
            for i in range(2):
                if not time_num_data[i] == -1:
                    df.loc[len(df) - 1,df.columns[i+2]] = time_num_data[i]
        #日付を降順にソート
        df = self.sort_date(df)
        #次の日より先の日のデータ削除
        df = self.limit_date(df)
        #データが入ってない日付を削除
        df = df.dropna(subset=self.element_list_date_none,how="all")
        #データ保存
        df.to_csv(self.save_csv,index=False)
        return df
    #データから引数score以上のSleep Scoreの総数を表示
    #使用していない
    def sum_high_score(self,score,df):
        x = sum(x>=score for x in df["Sleep Score"])
        lbl_high_score_sum = tk.Label(self.main_frame, text=f"Sleep Score{score}以上の日の合計")
        lbl2_high_score_sum = tk.Label(self.main_frame, text= f"：{x}日")
        lbl_high_score_sum.grid(row=1,column=6,sticky = tk.W)
        lbl2_high_score_sum.grid(row=1,column=7,sticky = tk.W)
    #endregion--------------------------------------------------------------------------
    #region-------------------------テーブルの要素処理-------------------------------------------------
    #勝利数のテーブル
    def insert_wins_tree(self):
            tpl = []
            tpl.append(sum(x == True for x in self.battle_df.loc[:,"is Win"]))
            '''
            日付比較できるように
            '''
            self.battle_df['date'] = pd.to_datetime(self.battle_df['date'], infer_datetime_format= True)
            first_day = datetime.date.today().replace(day=1)
            tpl.append(sum(x == True for x in self.battle_df[self.battle_df["date"] >= str(first_day)].loc[:,"is Win"]))
            value = tuple(tpl)
            self.tree_wins.insert(parent='', index='end', iid=1 ,values=(value))
    #直近の行動データのテーブル
    def insert_daily_tree(self):
        for i in range(2):
            tpl = [np.NaN]*len(self.df.columns)
            #１回目は今日のデータで２回目は明日のデータ
            date_data = str(datetime.datetime.today().date() + datetime.timedelta(days=i))
            tpl[0] = date_data
            s = self.df["date"].astype("str")
            df_Index = self.df[s==date_data].index.tolist()
            for index in df_Index:
                for j in range(1,len(self.df.columns)):
                    if str(self.df[self.df.columns[j]][index]) == "nan":
                        continue
                    index_value = self.df[self.df.columns[j]][index].round().astype(int)
                    if j == 1:
                        tpl[j] = index_value
                    else:
                        #時間表示に戻す
                        time_value = str(index_value // 60) + " : " +  str(index_value % 60).zfill(2)
                        tpl[j] = time_value
            value = tuple(tpl)
            self.tree.insert(parent='', index='end', iid=i ,values=(value))
    #目標達成数のテーブル
    def insert_achievement(self):
        tpl = []
        tpl.append(sum(x <= self.target_time[0] for x in self.df[self.element_list[2]]))
        tpl.append(sum(self.target_time[1] - 60 <= x <= self.target_time[1] + 60 for x in self.df[self.element_list[3]]))
        tpl.append(sum(x <= self.target_time[2] for x in self.df[self.element_list[4]]))
        value = tuple(tpl)
        self.tree_achievement.insert(parent='', index='end', iid=1 ,values=(value))
    #複数のテーブルのデータを削除して新しく要素決定
    def update_data_tree(self):
        # daily_data
        a = self.tree.get_children()
        for item in a:
            self.tree.delete(item)
        self.insert_daily_tree()
        #achievement
        b = self.tree_achievement.get_children()
        for item in b:
            self.tree_achievement.delete(item)
        self.insert_achievement()
        #score_mean
        c = self.tree_scores.get_children()
        for item in c:
            self.tree_scores.delete(item)
        '''
        ココ関数化する
        '''
        tpl = []
        all_sleep_mean = int(np.mean(self.df["Sleep Score"]))
        first_day = datetime.date.today().replace(day=1)
        month_sleep_mean = int(np.mean(self.df[self.df["date"] >= first_day]["Sleep Score"]))
        tpl.append(all_sleep_mean)
        ratio = month_sleep_mean / all_sleep_mean
        ratio = int((ratio-1)*100)
        ratio_str = '{:+}%'.format(ratio)
        tpl.append(f"{month_sleep_mean}({ratio_str})")
        value = tuple(tpl)
        self.tree_scores.insert(parent='', index='end', iid=1 ,values=(value))
    #endregion--------------------------------------------------------------------------
    #メモの保存処理
    def memo_save_click(self):
        input_text = self.memo_box.get("1.0", "end")
        self.c1.value = input_text
        self.wb.save(self.memo_path)
        self.memo_box.delete("1.0", tk.END)
        self.memo_box.insert("1.0", self.c1.value)
    #入力フォームの保存ボタンをおしたときの処理
    def data_output_csv(self):
        #入力データ取得
        self.sleep_score,self.time_str_data,self.date_data,self.date_plus1_data = self.get_textbox()
        #データ加工
        self.time_num_data = self.change_str_to_num(self.time_str_data)
        #データ保存
        self.df = self.data_save_csv(self.date_data,self.date_plus1_data,self.time_num_data,self.sleep_score)
        #テーブル更新
        self.update_data_tree()
        #処理用データ更新
        self.today_data_get()
        '''
        today_data_getにもかいてあるけど戦闘ボタンの削除処理をひとつの関数にまとめる
        '''
        #既に戦闘しているなら戦闘ボタンを削除
        if self.battle_df_Index:
            if self.battle_df["do Battle"][self.battle_df_Index[0]]:
                self.changePageButton_main.destroy()
    #処理に使う今日の行動データを取得
    def today_data_get(self):
        s = self.df["date"].astype("str")
        today_data = self.df[s == datetime.datetime.now().strftime("%Y-%m-%d")]
        if not today_data.empty:
            self.today_smartphone_end = today_data["Smartphone End"].values[0]
            self.today_active_start = today_data["Active Start"].values[0]
            self.today_bedtime_start = today_data["Bedtime Start"].values[0]
            self.changePageButton_main.destroy()
            self.changePageButton_main = tk.Button(self.main_frame, text="今日の戦闘へ", command=lambda : self.changePage(self.attackpage))
            self.changePageButton_main.place(x=610,y=400)
        else:
            #データがないから戦闘できない
            self.changePageButton_main.destroy()
#endregion--------------------------------------------------------------------------
#region-----------------------------attackpage---------------------------------------------
    '''
    敵の体力、攻撃力をプレイヤーのレベルの掛け算で増やす
    その際、敵の体力と自分の攻撃力のバランスをとる
    プレイヤーのレベル上がった時のステータス上昇を考える
    ドラクエ参考に？
    '''
    #--------------------------処理中にも画面が動くようにするため------------------------------------------------
    def battle_start(self):
        thread1 = threading.Thread(target=self.battle_main)
        thread1.start()
    #---------------------------バトルのメイン処理-----------------------------------------------
    def battle_main(self):
        # 今日はもうバトル出来なくする
        self.battle_start_button.destroy()
        self.changePageButton_main.destroy()
        self.battle_df.loc[self.battle_df_Index,["do Battle"]] = True
        #どちらかのHPが0になるまで繰り返す
        while True:
            player_attack_damage,enemy_attack_damage = self.damage_decision()
            # playerの攻撃
            self.enemy_hp_bar.step(-player_attack_damage)
            self.battle_log["text"] = f"プレイヤーが敵に{int(player_attack_damage)}ダメージ与えた！"
            self.thread_move_image("player")
            #win処理
            if self.enemy_hp_bar["value"] <= 0:
                self.battle_win()
                break
            time.sleep(1)
            # enemyの攻撃
            self.player_hp_bar.step(-enemy_attack_damage)
            self.battle_log["text"] = f"敵がプレイヤーに{int(enemy_attack_damage)}ダメージ与えた！"
            self.thread_move_image("enemy")
            #Lose処理
            if self.player_hp_bar["value"] <= 0:
                self.battle_lose()
                break
            time.sleep(1)
        #結果を保存
        self.battle_df.to_csv("./csv/battle_results.csv",index=False)
        #resultへのボタン設置
        self.changePageButton_battle.place(x = 0,y = 0)
    #---------------------------win処理-----------------------------------------------
    def battle_win(self):
        self.battle_log["text"] = "WIN"
        self.battle_df.loc[self.battle_df_Index,["is Win"]] = True
        #mainpageの勝利数の更新
        x = self.tree_wins.get_children()
        for item in x:
            self.tree_wins.delete(item)
        self.insert_wins_tree()
    #---------------------------lose処理-----------------------------------------------
    def battle_lose(self):
        self.battle_log["text"] = "LOSE"
        self.battle_df.loc[self.battle_df_Index,["is Win"]] = False
    #---------------------------プレイヤーと敵のダメージ決定処理呼び出し-----------------------------------------------
    def damage_decision(self):
        player_attack_damage = self.player_damage_decision()
        enemy_attack_damage = self.enemy_damage_decision()
        return player_attack_damage,enemy_attack_damage
    #---------------------------プレイヤーのダメージ決定処理-----------------------------------------------
    def player_damage_decision(self):
        '''
        仮処理
        '''
        #目標時間 self.today_smartphone_end 22:00 self.today_bedtime_start 18:00 self.today_active_start 23:00
        count1 = 5
        count2 = 5
        count3 = 5
        # 目標時間と実際の時間の差で倍率を決めてる
        #目標時間より速いなら（15分早いごとにプラス１）＋１、遅いなら１５分ごとにマイナス１、最大１０最低１、記録がないなら０
        if str(self.today_smartphone_end) == "nan":
            count1 += (-5)
        elif (self.target_time[0] - self.today_smartphone_end) < 0:
            count1 += max(-4,(self.target_time[0]-self.today_smartphone_end)/15)
        elif (self.target_time[0] - self.today_smartphone_end) >= 0:
            count1 += min(5,(self.target_time[0] - self.today_smartphone_end)/15 + 1)
        #目標時間から±１時間ならプラス１、１５分離れるごとにマイナス１、最大１０、最低１、記録がないなら０
        if str(self.today_active_start) == "nan":
            count2 += (-5)
        elif abs(self.target_time[1] - self.today_active_start) > 60:
            count2 += max(-4,4 - abs(self.target_time[1] - self.today_active_start)/15)
        elif abs(self.target_time[1] - self.today_active_start) <= 60:
            count2 += 5 - (abs(self.target_time[1] - self.today_active_start)/15)
        #目標時間より速いなら（15分早いごとにプラス１）＋１、遅いなら１５分ごとにマイナス１、最大１０最低１、記録がないなら０
        if str(self.today_bedtime_start) == "nan":
            count3 += (-5)
        elif (self.target_time[2]-self.today_bedtime_start) < 0:
            count3 += max(-4,(self.target_time[2]-self.today_bedtime_start)/15)
        elif (self.target_time[2]-self.today_bedtime_start) >= 0:
            count3 += min(5,(self.target_time[2]-self.today_bedtime_start)/15 + 1)
        #弱点は２倍に
        if self.enemy_weaknesses == 1:
            count1 *= 2
        elif self.enemy_weaknesses == 2:
            count2 *= 2
        elif self.enemy_weaknesses == 3:
            count3 *= 2
        player_attack_damage = count1 + count2 + count3
        #運要素を追加
        r = random.uniform(1, 1.5)
        player_attack_damage*=r * 0.1
        player_attack_damage*= self.player_attack
        return player_attack_damage
    #-------------------------敵のダメージ決定処理-------------------------------------------------
    def enemy_damage_decision(self):
        #運要素を追加
        '''
        仮処理
        '''
        r = random.uniform(0.5, 1.3)
        enemy_attack_damage = self.enemy_attack*r
        return enemy_attack_damage
    #-------------------------攻撃時の画像移動-------------------------------------------------
    def thread_move_image(self,id):
        thread_move_image = threading.Thread(target=self.move_image,kwargs={"id":id})
        thread_move_image.start()
    def move_image(self,id):
        x1 = 25
        x2 = -10
        if id == "enemy":
            x1 *= -1
            x2 *= -1
        for _ in range(10):
            self.canvas.move(id, x1, 0)
            time.sleep(0.01)
        # 攻撃を受けた方を点滅させる
        if id == "player":
            self.thread_blinking_image("enemy")
        else:
            self.thread_blinking_image("player")
        for _ in range(25):
            self.canvas.move(id,x2,0)
            time.sleep(0.001)
    #-------------------------攻撃受けた時の画像点滅-------------------------------------------------
    def thread_blinking_image(self,id):
        thread_blinking_image = threading.Thread(target=self.blinking_image,kwargs={"id":id})
        thread_blinking_image.start()
    def blinking_image(self,id):
        for _ in range(2):
            time.sleep(0.1)
            self.canvas.itemconfigure(id,state="hidden")
            time.sleep(0.1)
            self.canvas.itemconfigure(id,state="normal")
#endregion--------------------------------------------------------------------------
#region-----------------------------resultpage---------------------------------------------
    def result_start(self):
        thread2 = threading.Thread(target=self.result_main)
        thread2.start()
        thread3 = threading.Thread(target=self.treasure_chest_get)
        thread3.start()
    #---------------------------リザルトのメイン処理-----------------------------------------------
    def result_main(self):
        self.changePage(self.resultpage)
        if self.battle_df.loc[self.battle_df_Index,"is Win"].values[0]:
            self.win_or_lose_label["text"] = "WIN"
        else:
            self.win_or_lose_label["text"] = "LOSE"
        #3つの目標を達成しているかそれぞれ判定して1つのリストに入れてる
        achievement_mission_bool= [self.today_smartphone_end <= self.target_time[0],\
            self.target_time[1] - 60 <= self.today_active_start <= self.target_time[1] + 60,\
            self.today_bedtime_start <= self.target_time[2]]
        print(achievement_mission_bool)
        self.achievement_mission1["text"] = self.achievement_mission_text(achievement_mission_bool[0])
        self.achievement_mission2["text"] = self.achievement_mission_text(achievement_mission_bool[1])
        self.achievement_mission3["text"] = self.achievement_mission_text(achievement_mission_bool[2])
        self.advice["text"] = self.advice_text(achievement_mission_bool)
    def achievement_mission_text(self,bl):
        if bl:
            return "達成"
        else:
            return "未達成"
    def advice_text(self,bl_list):
        if not bl_list[0]:
            return "スマホを早くやめよう"
        elif not bl_list[1]:
            return "運動を時間通りにやってみよう"
        elif not bl_list[2]:
            return "早く布団に入ってみよう"
        return "明日もこの調子で頑張ろう"
    #-------------------------------宝箱の獲得判定-------------------------------------------
    def treasure_chest_get(self):
        #宝箱の獲得確率
        r = random.randrange(4)
        #勝利したかつランダムrandrange(4)、if r<=1なら0,1,2,3のうち0,1がでたら宝箱獲得
        if r <= 1 and self.battle_df.loc[self.battle_df_Index,"is Win"].values[0]:
            #宝箱獲得
            self.treasure_chest_image = PIL.Image.open(f"./images/closed_treasure_chest.png")
            self.treasure_chest_image = self.treasure_chest_image.resize((250, 250))
            self.treasure_chest_img = PIL.ImageTk.PhotoImage(self.treasure_chest_image)
            self.result_canvas.create_image(800, 50, image=self.treasure_chest_img, anchor=tk.NW)
            #開封演出
            time.sleep(2)
            self.treasure_chest_image = PIL.Image.open(f"./images/open_treasure_chest.png")
            self.treasure_chest_image = self.treasure_chest_image.resize((250, 250))
            self.treasure_chest_img = PIL.ImageTk.PhotoImage(self.treasure_chest_image)
            self.result_canvas.create_image(800, 50, image=self.treasure_chest_img, anchor=tk.NW)
            #宝箱の中身表示
            self.treasure_get_lbl = tk.Label(self.resultpage, text="EXP３獲得",font=('Helvetica', '15'))
            self.treasure_get_lbl.place(x=800,y=300)
        else:
            #宝箱未獲得
            self.treasure_no_get_lbl = tk.Label(self.resultpage, text="獲得アイテムなし",font=('Helvetica', '20'))
            self.treasure_no_get_lbl.place(x=925,y=170)    
#endregion--------------------------------------------------------------------------
#endregion--------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()