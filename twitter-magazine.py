import os
import time
import datetime
import re
import subprocess
import numpy as np
import tweepy

my_email_address = '' # mailコマンドの宛先アドレス
my_screen_name = '' # 自分のTwitter IDを記入
lists = ["friends", "news", "researchers"] # 収集対象のリストを列挙。メールにはこの順番で表示されます。
consumer_key = 'xxxxxxxxxxxxxxxxxxxxxx'
consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
start_time_sec = 25 * 60 * 60 # 現在から start_time_sec 秒前のつぶやきを起点に収集
end_time_sec = 1 * 60 * 60 # 現在から end_time_sec 秒前までのつぶやきを収集

# 以下に3つある関数のうち少なくとも twfilter は好みに応じて編集する必要があります
def removeRTs(tweets):
    """ つぶやきのリストからRTを削除

    Args:
        tweets (list of tweepy.API.Status): つぶやきのリスト
    Returns:
        list of tweepy.API.Status: 削除後のリスト
    """
    ret = []
    for s in tweets:
        if not re.match('^RT+', s.full_text):
            ret.append(s)
    return ret

def getTopTweets(tweets):
    """ 何らかの基準でつぶやきのリストをソートし上位K件のみを返す。
    デフォルトの評価関数は favorite_count + retweet_count。

    Args:
        tweets (list of tweepy.API.Status): つぶやきのリスト
    Returns:
        list of tweepy.API.Status: 上位K件のつぶやき
    """

    K = 20 # 上位K件のつぶやきのみを抽出
    scores = np.array([status.favorite_count + status.retweet_count for status in tweets])

    if len(tweets) <= K:
        unsorted_max_indices = np.array(list(range(len(tweets))))
    else:
        unsorted_max_indices = np.argpartition(-scores, K)[:K]
    
    y = scores[unsorted_max_indices]
    indices = np.argsort(-y)
    max_k_indices = unsorted_max_indices[indices]
    return [tweets[i] for i in max_k_indices]

# 好みのフィルタリングルールを twfilter メソッドに記述します。以下はサンプルです。
def twfilter(statuses):
    """全てのつぶやきをユーザの好みに応じてフィルタリングした結果を返す。
    
    Args:
        statuses (dict of tweepy.API.Status): リスト名をキーとするつぶやきのdict
    Returns:
        dict of tweepy.API.Status: フィルタ結果
    """

    statuses["news"] = getTopTweets(removeRTs(statuses["news"]))
    statuses["researchers"] = getTopTweets(removeRTs(statuses["researchers"]))

    return statuses


# 以下は特に編集する必要ありません（正しく動けば・・・）

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

user = api.get_user(my_screen_name)
print("API initialized. User screen name = " + user.screen_name + " (" + str(user.followers_count) + " followers)")

statuses = {}
for s in lists:
    statuses[s] = []

failedcount = 0
for slug in lists:
    page = 1
    stopflag = False
    now = datetime.datetime.now() - datetime.timedelta(hours = 9)

    while True:
       try:
           print("Get the list of " + slug + ": page = " + str(page))
           tl = api.list_timeline(my_screen_name, slug, since_id = None, page = page, tweet_mode='extended')
           # current to old

           for status in tl:
               tdiffsec = (now - status.created_at).total_seconds()
               if tdiffsec >= end_time_sec and tdiffsec < start_time_sec:
                   statuses[slug].append(status)
               if tdiffsec >= start_time_sec:
                   # stop
                   stopflag = True
                   break

           if stopflag == True:
               break

           print("oldest = " + str((now - tl[-1].created_at).total_seconds()/60/60) + " hours before")
           print("len(statuses[slug]) = " + str(len(statuses[slug])))
           time.sleep(2)
           page += 1
       except:
           print("Something wrong.")
           failedcount += 1
           if failedcount >= 1:
               break
           time.sleep(60)
    print("Collected " + str(len(statuses[slug])) + " tweets")
    if failedcount >= 1:
       break

statuses = twfilter(statuses)

basePath = os.path.dirname(os.path.abspath(__file__))
fname = basePath + "/" + datetime.datetime.now().strftime("%Y%m%d-%H%M") + ".htm"
with open(fname, "w", encoding="utf-8") as f:
    f.write("<html><body>")
    for slug in lists:
        f.write("\n")
        f.write("<h2>List: " + slug + "</h2>\n")
        f.write("<hr>")
        for status in statuses[slug]:
            status.created_at += datetime.timedelta(hours=9)
            url = "https://twitter.com/" + status.author.screen_name + "/status/" + str(status.id)
            purl = "https://twitter.com/" + status.author.screen_name
            iurl = status.author.profile_image_url
            imghtml = "<img src=\"" + iurl + "\" />"

            f.write("<div style=\"float:left; width: 48px; padding-right: 10px;\">")
            f.write("<a href=\"" + url + "\" target=\"_blank\">")
            f.write(imghtml)
            f.write("</a>")
            f.write("</div>")
            f.write("<div style=\"\">")
            f.write("<a href=\"" + purl + "\" target=\"_blank\">@" + status.author.screen_name + "</a> [" + str(status.retweet_count) + " RTs / " + str(status.favorite_count) + " favs]")
            f.write("<br>")
            f.write(status.full_text)
            f.write("</div>")
            f.write("<div style=\"clear:both; padding: 10px;\"></div>")
    f.write("</html></body>")

time.sleep(1)
time_window_hour = str(int((start_time_sec - end_time_sec) / 3600))
cmd = "cat " + fname + " | mail -s \"$(echo \"過去" + time_window_hour + "時間のTwitterまとめ " + datetime.datetime.now().strftime("%m月%d日") + "\\nContent-Type: text/html; charset=utf-8\")\" " + my_email_address
print("cmd = " + cmd)
res = subprocess.call(cmd, shell = True)
print(res)

