# PornHub Link Crawler

# Installation

Check what version of python you have: python --version <br />
Recommended & tested usage is with python3. <br />
Also, check if you have pip3 installed (apt install python3-pip). <br />

you can install a docker container first if you like
```bash
docker run -it \
    --cap-add=NET_ADMIN\ 
    --net=bridge \
    --name=ph-downloader \
    -v /your/host/folder:/ph \
    ubuntu:latest\
    /bin/bash
```

```bash
apt update && apt upgrade -y       
apt install python3 nano python3 python3-pip wget curl unzip ffmpeg
apt install python3-pip
pip3 install youtube-dl prettytable bs4 requests --break-system-packages
wget https://github.com/gomaaz/PornHub-downloader-python/archive/master.zip
unzip master.zip
cd PornHub-downloader-python-master
python3 phdler.py
```
It will ask you for your download folder PATH. Please enter your full path without the last backslash. <br />
Like this: /home/username/media/phmedia <br />
On first run, phdler will create a database.db which will be used later for everything.


# Usage
```bash

+-------------------+---------+------------------------------------------------------+
| Tool              | command | item                                                 |
+-------------------+---------+------------------------------------------------------+
| python3 phdler.py | start   |                                                      |
| python3 phdler.py | custom  | url | batch                                          |
| python3 phdler.py | add     | model | pornstar | channel | user | playlist | batch |
| python3 phdler.py | list    | model | pornstar | channel | user | playlist | all   |
| python3 phdler.py | delete  | model | pornstar | channel | user | playlist         |
+-------------------+---------+------------------------------------------------------+
```

# Example

## START
```bash
python3 phdler.py start
```

## CUSTOM
```bash
python3 phdler.py custom https://www.pornhub.com/view_video.php?viewkey=ph5d69a2093729e
or
python3 phdler.py custom batch
```
The batch option will ask you for the full path of your .txt file where you can import multiple URLs at once. <br />
Take care that every single URL in the .txt file is in his own row.

## ADD
```bash
python3 phdler.py add https://www.pornhub.com/model/luxurygirl
or
python3 phdler.py add https://www.pornhub.com/pornstar/leolulu
or
python3 phdler.py add https://www.pornhub.com/channels/mia-khalifa
or
python3 phdler.py add https://www.pornhub.com/users/lasse98
or
python3 phdler.py add https://www.pornhub.com/playlist/30012401
or
python3 phdler.py add batch
```
The batch option will ask you for the full path of your .txt file where you can import multiple URLs at once. <br />
Take care that every single URL in the .txt file is in his own row.

## LIST
```bash
python3 phdler.py list model
or
python3 phdler.py list pornstar
or
python3 phdler.py list channels
or
python3 phdler.py list users
or
python3 phdler.py list playlist
or
python3 phdler.py list all
```

## DELETE
```bash
python3 phdler.py delete model
or
python3 phdler.py delete pornstar
or
python3 phdler.py delete channels
or
python3 phdler.py delete users
or
python3 phdler.py delete playlist
```
The option DELETE will list the selected item type, list them from the database and give you an option to enter the item ID of which one you want to be deleted.


# Explained

Every time you add a new item (model/pornstar and so on), the script will scrape the real name from the website and write it to the database. That is how we can have pretty names in final folders. Every added item is treated with a status of NEW=1, so the script knows that it needs to download all videos from the selected item. After the download of all videos is completed for the selected item, the script will change it to NEW=0. This way, when you START the script, it will first run down trough the database and ask for all items that have the status of NEW=1, and after that, it will check for new videos from items with the status NEW=0.
This should not bother you... I just wanted to explain how it works.


# Big thanks to

YouTube-DL <br />
PrettyTables <br />
BS4 aka BeautifulSoup4 <br />
and of course, all of you :)
