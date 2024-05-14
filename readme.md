## IVE-Discord-Bot

A fully custom Discord Bot for IVE

Support **Python 3.8 - 3.12**

# How to setup :
```
git clone https://github.com/twkenxtis/IVE-Discord-Bot
cd IVE-Discord-Bot
pip install -r requirements.txt
```

setting up Discord TOKEN
```
cd config 
vim .env
```
Note: If want update ive_hashtag.json after Edit run

```
python3 update_ive_hashtag.py
```
- Please make sure your are following json format edit and **DO NOT CHANGE JSON FILE NAME** Please!
  
Next setup config/settings.json path to chrome notify history path
```
cd config 
vim setting.json
```
  ### windows chrome notify locate
  
  `C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Default\Platform Notifications\000003.log`
  
  > Can't find the file? try typing `windows+R` ➡️ `%appdate%` ➡️ `Follow the path` ➡️ then find out the 000003.log is a binary file.
  > 
  > back to config folder and open `settings.json` change the <username> and your done.
  
  ### windows WSL chrome notify locate
  
  > Change <username> to your computer username on WSL.
  > 
  > ```
  > cat '/mnt/c/Users/<username>/AppData/Local/Google/Chrome/User Data/Default/Platform Notifications/000003.log'
  > ```
  > 
  > If see your notify history then congratulations! Your are find the file.
  > 
  > ```
  > vim settings.json
  > ```
  > then chose UNIX path and write your patch
  > 
  > back to config folder and open `settings.json` change the <username> and your done.
  
  ## Linux chrome notify locate
  
  Please change your **<$HOME>** to your **home path name** in `settings.json` your chrome or chromium browser install path
  
  > Linux chrome notify history file path is
  > ```
  > "home/<username>/.config/google-chrome/Default/Platform Notifications/000003.log"
  > ```
  > If you did't find the file, try to find the file by typing `locate 000003.log` in terminal. or using fzf
  
  back to config folder and open `settings.json` change the <username> and your done.
  
  ### Other environment chrome notify locate
  
  For example your using docker like [docker-webtop](https://docs.linuxserver.io/images/docker-webtop/)
  
  
  > find your browser file path and follow the `\Google\Chrome\User Data\Default\Platform Notifications\000003.log` to find out 000003.log is a binary file.
  > Don't forget bind `000003.log` patch in yor docker volumes into container
  
  back to config folder and open `settings.json` change the <username> and your done.
  
  Ensure that your Docker container is up and running, then examine the Docker logs and environment settings to verify that everything is configured correctly.
  
  If all checks out well, you have successfully completed the setup.

## Before Start the bot!
```
cd src 
vim Discord.py 
```
 Discord.py in line **198** ``Class Match_wich_account()``
 - Please edit to your own channel ID
   
    ```  
   class Match_wich_account():
     def channel_id(self, ive_name):
          channel_id = {
              "GAEUL": "1237020442183860276",
              "fallingin__fall": "1237020442183860276",
              "YUJIN": "1237020290987458643",
              "_yujin_an": "1237020290987458643",
              "REI": "1238508631876567120",
              "reinyourheart": "1238508631876567120",
              "WONYOUNG": "1237020545527054346",
              "for_everyoung10": "1237020545527054346",
              "LIZ": "1237020520092794950",
              "liz.yeyo": "1237020520092794950",
              "LEESEO": "1237020484411985950",
              "eeseooes": "1237020484411985950",
              "GROUPS": "1237421929229582439"
          }
      ```
- Setp 2
  
  change to your own rsshub url in `Twitter_rss_process.py` **line24**
  
  For Example my RSSHUB is runnung on http://127.0.0.1:1200
  I want to get twitter media then limit querry string to 1 post response
  
  ```rss_request = f'http://127.0.0.1:1200/twitter/media/{twitter_account_name}?limit=1'```
 
  ```
  vim src/twitter/Twitter_rss_process.py
  ```

    Example code:

    ```
    class Twitter:

    def __init__(self) -> None:
        self.twitter_rss_dict = Twitter_Dict_Manager()
        pass

    def start_request(self, twitter_account_name: str):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # Change here to your own rsshub url don't change {twitter_account_name} value.
        rss_request = f'http://127.0.0.1:1200/twitter/media/{twitter_account_name}?limit=1'
    ```

# Getting Start!

  Setp1 : run Discord bot first
  
    
    cd src 
    python3 Discord.py
    
    
  Step2: start API_notify.py to trigger notify
  
    
    cd src 
    python3 API_notify.py
    
  

# How it works?
trigger your local chrome notifications and send GET request for [**RSSHUB**](https://github.com/DIYgod/RSSHub) After some magic process send to Discord channel
- What is RSSHUB?
> **I'm using **RSSHUB** for my core request API you can choese whatever you want RSS service (Highly recommended [rsshub](https://github.com/DIYgod/RSSHub)) A open source MIT project)**

  Setp1 : Make sure your chrome allow send notify and turn on this setting on google-chrome  ``System/Continue running backgroud apss when Google chrome is close``
  
  Setp2 : Make sure Allow Twitter and instagram **Web Push API** ， Because sometimes,privacy-focused browser extensions may block it.
  
  Setp3 : goto ```/config/setting/``` and ```/config/.env``` wrote your Discord Token and chrome notify locate.
