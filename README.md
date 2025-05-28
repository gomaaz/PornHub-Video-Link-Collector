inspired by https://github.com/mariosemes/PornHub-downloader-python

# Pornhub Video Link Collector

This script collects video links from [pornhub.com](https://www.pornhub.com) search and listing pages, and saves them to a file called `video_urls.txt`.

It is designed to help you quickly gather direct video page links (those containing a `viewkey` parameter) across all pages of a search result or video listing, making it easy to feed these links into download tools such as **JDownloader**.

## Features

- **Multi-page scraping:** Automatically iterates through all result pages (using the `?page=` parameter) and collects all matching video links.
- **Filter by criteria:** Only collects links that match your given search criteria, including support for HD-only results (e.g. `&hd=1`) or any other search parameters.
- **Viewkey-only links:** Only video links that contain a `viewkey` in their URL are collected, ensuring that only valid, direct video pages are included.
- **Batch support:** You can provide a single URL or a batch file with multiple URLs for processing.
- **Useful for automation:** The collected links in `video_urls.txt` can be directly used with download managers like JDownloader.

## Usage

Run the script via command line. For example, to collect all HD public videos:

```sh
python3 phdler.py custom "https://www.pornhub.com/video/search?search=public&hd=1"
```
You need to make sure that the file `video_urls.txt` is deleted with each run of your process to prevent the file from growing with appended data.

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

in this container run the following:

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


PrettyTables <br />
BS4 aka BeautifulSoup4 <br />
and of course, all of you :)
