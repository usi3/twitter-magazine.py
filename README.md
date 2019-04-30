# twitter-magazine.py

Twitterで管理しているリストをメールマガジンのような形式で自分のみに配信するPythonスクリプトです。配信されるメールにはいいねやRT数、アイコンなどが表示されます。

「Twitter依存を脱却したい」が「友人・知人のつぶやきを漏れなく読みたい」。
「特定界隈で話題になったつぶやきは上位数十件のみ読みたい」場合などに便利です。

![実行例](https://github.com/usi3/twitter-magazine.py/blob/master/sample.png?raw=true)

上記の画像は配信メールのサンプルです。この画像に示す通り、添付写真の表示には対応しておらず、代わりに写真のURLが表示されます。また、いいね/RTしたい場合はアイコンをクリックして元のツイートをブラウザで表示する必要があります。

## 導入手順
以下の導入手順はDebian系のLinuxディストリビューションを前提としています。
環境に応じて適宜変えてください。

1. Python 3系列でのみ動作を確認しています
    - `python --version`
2. Python の Twitter クライアントである tweepy が必要です
    - `pip install tweepy`
3. Gmail でメールを配信する場合はアプリパスワードを取得する必要があります
    - https://support.google.com/mail/answer/185833?hl=ja
4. GNU mail と sSMTP を用いてメールを配信します
    - `apt install ssmtp mailutils`
5. SMTPでメールを送信できるよう `/etc/ssmtp/ssmtp.conf` の設定が必要です
    - mailコマンドの動作確認
        - `echo "Hello." | mail -s "Test Title" your-account@gmail.com`
6. Twitter の開発者ツールにおいて新規アプリを作成しキーとトークンを取得します
    - [Twitter Developer Platform](https://developer.twitter.com/)

7. `twitter-magazine.py` を開いて冒頭の変数と関数を編集します

8. 以下を実行すると自分宛てにメールが届くはずです
    - `python twitter-magazine.py`
   
9. 動作を確認できたら `cron` 等に登録します

### 設定例
#### /etc/ssmtp/ssmtp.conf (Gmailの場合)
    # sudo emacs /etc/ssmtp/ssmtp.conf
    root=your-account@gmail.com
    mailhub=smtp.gmail.com:587
    hostname=your-host-name
    AuthUser=your-account@gmail.com
    AuthPass=your-application-password
    UseTLS=YES

#### twitter-magazine.py
    my_email_address = "your-account@gmail.com" # mailコマンドの宛先アドレス
    my_screen_name = 'your-twitter-screen-name' # 自分のTwitter IDを記入
    lists = ["friends", "news", "researchers"] # 収集対象のリストを列挙。メールにはこの順番で表示されます。
    consumer_key = 'xxxxxxxxxxxxxxxxxxxxxx'
    consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    access_token_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    start_time_sec = 25 * 60 * 60 # 現在から start_time_sec 秒前のつぶやきを起点に収集
    end_time_sec = 1 * 60 * 60 # 現在から end_time_sec 秒前までのつぶやきを収集

    # 好みのフィルタリングルールを twfilter メソッドに記述します。以下はサンプルです。
    def twfilter(statuses):
        # statuses["friends"]には何も変更を加えない
        statuses["news"] = getTopTweets(removeRTs(statuses["news"]))
        statuses["researchers"] = getTopTweets(removeRTs(statuses["researchers"]))

        return statuses

#### cron
    > # 例：毎日昼の12:00にメール配信
    > # crontab -e
    > 00 12 * * * python /home/xxx/twitter-magazine.py 

# FAQ
## Twitter APIの認証に失敗する
各トークンが一字一句間違わずにコピーされていることを確認してください。
また、実行環境の時刻（システムクロック）がずれていても認証に失敗します。



