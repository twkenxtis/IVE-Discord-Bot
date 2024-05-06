## IVE-Discord-Bot

A fully custom Discord Bot for IVE

- If want update ive_hashtag.json File using <update_ive_hashtag.py>

> Please make sure your are following json format edit and **DO NOT CHANGE JSON FILE NAME** Please!

### About settings.json:

## windows

`C:\Users\<username\AppData\Local\Google\Chrome\User Data\Default\Platform Notifications\000003.log`

> Can't find the file? try typing `windows+R`➡️`%appdate%`➡️`Follow the path`➡️then find out the 000003.log is a binary file.
> back to config folder and open `settings.json` change the <username> and your done.

## windows WSL

> Change <username> to your computer username on WSL.
> `cat '/mnt/c/Users/<username>/AppData/Local/Google/Chrome/User Data/Default/Platform Notifications/000003.log'`
> If see your notify history then congratulations! Your are find the file.
> `vim settings.json` then chose UNIX path and write your patch
> back to config folder and open `settings.json` change the <username> and your done.

## Linux

Please change your **<$HOME** to your **home path name** in `settings.json`
Linux chrome notify history file path is `"$HOME/.config/google-chrome/Default/Platform Notifications/000003.log"`
If you don't find the file, try to find the file by typing `locate 000003.log` in terminal. or using fzf
back to config folder and open `settings.json` change the <username> and your done.

## Other environment

For example your using docker like [docker-webtop](https://docs.linuxserver.io/images/docker-webtop/)
find your browser file path and follow the `\Google\Chrome\User Data\Default\Platform Notifications\000003.log` to find out 000003.log is a binary file.
Don't forget bind `000003.log` patch in yor docker volumes into container
back to config folder and open `settings.json` change the <username> and your done.
Ensure that your Docker container is up and running, then examine the Docker logs and environment settings to verify that everything is configured correctly. If all checks out well, you have successfully completed the setup.

## I don't have Mac so I'm not sure is working on Mac....

> If your trying running on mac try to find 000003.log then check file authority!
