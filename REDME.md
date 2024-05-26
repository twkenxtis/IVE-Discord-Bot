# A fully custom Discord Bot for IVE

## IVE 的完全客製化 Discord 機器人
  [繁體中文版](https://github.com/twkenxtis/IVE-Discord-Bot/tree/main/docs)

Support **Python 3.10 - 3.12**

# How to setup :

- Setp 1

venv (optional)
```
python3 -m venv path/to/venv
source path/to/venv/bin/activate
```

- Setp 2
```
git clone https://github.com/twkenxtis/IVE-Discord-Bot
cd IVE-Discord-Bot
pip3 install -r requirements.txt
```

- Setp 3
  
Remove .example from the extension
```
cd assets

mv Twitter_dict.json.example Twitter_dict.json
mv Twitter_dict.pkl.example Twitter_dict.pkl
```

- Setp 4
  
```
cd src 
vim Discord.py 
```

 Edit Discord.py line :111 　``def channel_id(ive_name: str) -> int:``
 > Please edit to your own discord channel ID.
For example:
    
    class DCBot_Twitter(object):

      # skip some funcation...

      
      @staticmethod
      @ lru_cache(maxsize=7)
      def channel_id(ive_name: str) -> int:
          channel_dict = {
              "GAEUL": "1142900837300043889",
              "fallingin__fall": "1142900837300043889",
              "YUJIN": "1142900711315734599",
              "_yujin_an": "1142900711315734599",
              "REI": "1142900891393994782",
              "reinyourheart": "1142900891393994782",
              "WONYOUNG": "1142900973405229056",
              "for_everyoung10": "1142900973405229056",
              "LIZ": "1142901102526869556",
              "liz.yeyo": "1142901102526869556",
              "LEESEO": "1142901201332097205",
              "eeseooes": "1142901201332097205",
              "GROUPS": "1157550597248135208"
          }
      
    
- Setp 5
 
  ```
  cd ../config
  mv .env.example .env
  vim .env
  ```
  
  change to your own rsshub url in `.env` ,
  chaneg to your own Discord Token in `.env`
  
  For Example my RSSHUB is runnung on http://127.0.0.1:1200/ I wabt got Twitter user media
  
  ```
  Discord_TOKEN = JcJbLXfJHU2fpi0PjZo3BdfBUEi4eydqb3u89Jmqsr1msxXSFkviYDlEyuZ02SrdSDSShfEY
  RSS_HUB_URL = http://127.0.0.1:1200/twitter/media/
  ```

  or

  ```
  Discord_TOKEN=JcJbLXfJHU2fpi0PjZo3BdfBUEi4eydqb3u89Jmqsr1msxXSFkviYDlEyuZ02SrdSDSShfEY
  RSS_HUB_URL=http://127.0.0.1:1200/twitter/media/
  ```

### Getting Start running BOT!

- Setp 6 : Run Discord BOT first
  
``` 
cd src 
python3 Discord.py
```
    
    
- Step 7 start main.py
  
```
python3 main.py
```
  

# How it works?
Send GET request for [**RSSHUB**](https://github.com/DIYgod/RSSHub) After some magic send to Discord channel
- What is RSSHUB?
> **I'm using **RSSHUB** for my core request API you can choese whatever you want RSS service (Highly recommended [rsshub](https://github.com/DIYgod/RSSHub)) A open source MIT project)**

