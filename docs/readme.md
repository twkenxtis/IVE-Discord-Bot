# IVE 的完全客製化 Discord 機器人

支援 **Python 3.10 - 3.12**

# 如何設置：

- 步驟 1

虛擬環境 (可選)
```
python3 -m venv path/to/venv
source path/to/venv/bin/activate
```
- 步驟 2
```
git clone https://github.com/twkenxtis/IVE-Discord-Bot
cd IVE-Discord-Bot
pip3 install -r requirements.txt
```

- 步驟 3
  
```
cd src 
vim Discord.py 
```

 編輯 Discord.py 第 111 行：``def channel_id(ive_name: str) -> int:``
 > 請根據您自己的 Discord 頻道 ID 進行編輯。
例如：
    
    class DCBot_Twitter(object):

      # 省略一些函式...

      
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
      
  - 步驟 4
 
  ```
  cd ../config
  mv .env.example .env
  vim .env
  ```

  更改 `.env` 中的 RSSHUB URL 為您自己的RSSHUB URL地址，
  將 `.env` 中的 Discord Token 更改為您自己的
  
  例如，我的 RSSHUB 運行在 http://127.0.0.1:1200 我想要獲取Twitter用戶媒體

  ```
  Discord_TOKEN = JcJbLXfJHU2fpi0PjZo3BdfBUEi4eydqb3u89Jmqsr1msxXSFkviYDlEyuZ02SrdSDSShfEY
  RSS_HUB_URL = http://127.0.0.1:1200/twitter/media/
  ```

  or

  ```
  Discord_TOKEN=JcJbLXfJHU2fpi0PjZo3BdfBUEi4eydqb3u89Jmqsr1msxXSFkviYDlEyuZ02SrdSDSShfEY
  RSS_HUB_URL=http://127.0.0.1:1200/twitter/media/
  ```

### 開始運作機器人!

- 步驟 5 : 首先運行 Discord BOT
  
``` 
cd src 
python3 Discord.py
```
    
    
- 步驟 6 運行 main.py
  
```
python3 main.py
```
  

# 工作原理？
對 [**RSSHUB**](https://github.com/DIYgod/RSSHub) 發送 GET 請求，經過一些魔法後發送到 Discord 頻道
- 什麼是 RSSHUB？
> **我正在使用 **RSSHUB** 作為我的核心請求 API，您可以選擇任何您想要的 RSS 服務（強烈推薦 [rsshub](https://github.com/DIYgod/RSSHub)）一個開源的 MIT 項目)**


### 更新版本
⚠️ 執行重新拉取之前請先備份位於 assets 的所有數據!
