## IVE-Discord-Bot

A fully custom Discord Bot for IVE

Support **Python 3.8 - 3.12**

# How to setup :
```
git repo clone twkenxtis/IVE-Discord-Bot \
cd IVE-Discord-Bot \
pip install -r requirements.txt
```

setting up Discord TOKEN
```
cd config \
vim .env
```
- If want update ive_hashtag.json File using `update_ive_hashtag.py`

> Please make sure your are following json format edit and **DO NOT CHANGE JSON FILE NAME** Please!
  
Next setup config/settings.json path to chrome notify history path
```
cd /config \
vim setting.json
```
### windows

`C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Default\Platform Notifications\000003.log`

> Can't find the file? try typing `windows+R` ➡️ `%appdate%` ➡️ `Follow the path` ➡️ then find out the 000003.log is a binary file.
> 
> back to config folder and open `settings.json` change the <username> and your done.

### windows WSL

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

## Linux

Please change your **<$HOME>** to your **home path name** in `settings.json` your chrome or chromium browser install path

> Linux chrome notify history file path is
> ```
> "home/<username>/.config/google-chrome/Default/Platform Notifications/000003.log"
> ```
> If you did't find the file, try to find the file by typing `locate 000003.log` in terminal. or using fzf

back to config folder and open `settings.json` change the <username> and your done.

### Other environment

For example your using docker like [docker-webtop](https://docs.linuxserver.io/images/docker-webtop/)


> find your browser file path and follow the `\Google\Chrome\User Data\Default\Platform Notifications\000003.log` to find out 000003.log is a binary file.
> Don't forget bind `000003.log` patch in yor docker volumes into container

back to config folder and open `settings.json` change the <username> and your done.

Ensure that your Docker container is up and running, then examine the Docker logs and environment settings to verify that everything is configured correctly.

If all checks out well, you have successfully completed the setup.

# Start the bot!
```
cd /src \
python3 Discord.py \
cd .. \
python3 main.py
```

# How it works?
trigger your local chrome notifications and send GET request for [**RSSHUB**](https://github.com/DIYgod/RSSHub) After some magic process send to Discord channel
- What is RSSHUB?
> **I'm using **RSSHUB** for my core request API you can choese whatever you want RSS service (Highly recommended [rsshub](https://github.com/DIYgod/RSSHub)) A open source MIT project)**

  Setp1 : Make sure your chrome allow send notify and turn on this setting on google-chrome  ``System/Continue running backgroud apss when Google chrome is close``
  
  Setp2 : Make sure Allow Twitter and instagram **Web Push API** ， Because sometimes,privacy-focused browser extensions may block it.
  
  Setp3 : goto ```/config/setting/``` and ```/config/.env``` wrote your Discord Token and chrome notify locate.
  

## In the END, I don't have Mac so I'm not sure is working on Mac....

> If your trying running on mac try to find 000003.log then check file authority!
